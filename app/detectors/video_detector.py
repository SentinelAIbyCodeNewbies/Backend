import cv2
import numpy as np
import tensorflow as tf
import os
from mtcnn import MTCNN

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "app", "models", "video_detect", "video_model.keras")

print("Loading video model and MTCNN face detector...")
model = tf.keras.models.load_model(MODEL_PATH)
detector = MTCNN()

FAKE_CLASS_INDEX = 0
REAL_CLASS_INDEX = 1

FAKE_THRESHOLD = 0.5

MIN_FRAMES_FOR_DECISION = 5

#face detection using mtcnn pipeline

def extract_face(frame: np.ndarray):

    rgb_frame = cv2.detector(frame, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(rgb_frame)

    if not results:
        return None
    
    largest_face = None
    max_area = 0
    for result in results:
        x, y, w, h = result['box']
        x, y =  max(0, x), max(0, y)
        area = w * h
        if area > max_area:
            max_area = area
            largest_face = (x, y, w, h)

    if largest_face is None:
        return None
    
    x, y, w, h = largest_face

    ih, iw, _ = frame.shape
    w = min(iw -x, w)
    h = min(ih -y, h)

    face = frame[y:y + h, x:x + w]

    if face.shape[0] < 50 or face.shape[1] < 50:
        return None
    
    return face

def predict_video(video_path:str) -> dict:

    cap = cv2.VideoCapture(video_path)

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    if fps == 0:
        fps = 30


    frame_interval = max(1, fps//2)
    frame_count = 0
    faces_batch = []

    success, frame = cap.read()
    while success:
        if frame_count % frame_interval == 0:
            face = extract_face(frame)
            if face is not None:
                face_resized = cv2.resize(face, (224, 224))
                face_float = face_resized.astype(np.float32)
                faces_batch.append(face_float)

        success, frame = cap.read()
        frame_count += 1

    cap.release()

    if len(faces_batch) == 0:
        return{
            "error": "No faces could be detected in this video. "
                        "Ensure it contains clear, frontal faces."
        }
    
    batch_array = np.array(faces_batch) #shape: (N, 224, 224 ,3)
    preds = model.predict(batch_array, verbose=0) #shape: (N, 2)

    fake_probabilities = preds[:, FAKE_CLASS_INDEX]
    average_fake_prob = float(np.mean(fake_probabilities))

    is_fake = average_fake_prob > FAKE_THRESHOLD

    frames_analysed = len(faces_batch)

    if is_fake:
        label: "fake"
        confidence = round(average_fake_prob * 100, 2)

    else:
        label: "real"
        confidence: round((1.0 - average_fake_prob) *100, 2)

    return {
        "prediction":       label,
        "confidence":       confidence,
        "low_confidence":   frames_analysed < MIN_FRAMES_FOR_DECISION,
        "raw_score":        round(average_fake_prob, 4),
        "fake_probability": round(average_fake_prob * 100, 2),
        "real_probability": round((1.0 - average_fake_prob) * 100, 2),
        "frames_analysed":  frames_analysed,
        "fake_frame_ratio": round(
            float(np.mean(preds[:, FAKE_CLASS_INDEX] > FAKE_THRESHOLD)) * 100, 2
        ),
    }
