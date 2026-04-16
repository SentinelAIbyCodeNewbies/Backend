import tensorflow as tf
import cv2
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "app", "video_detect", "best_tf_model.keras")

model = tf.keras.models.load_model(MODEL_PATH)

def extract_frames(video_path, max_frames=20):
    cap = cv2.VideoCapture(video_path)
    frames=[]
    count=0

    while cap.isOpened() and count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (224,224))
        frame = frame / 255.0
        frames.append(frame)
        count += 1

    cap.release()
    return np.array(frames)

def predict_video(video_path):
    frames = extract_frames(video_path)

    if len(frames) == 0:
        return {"error": "No frames extracted"}
    
    preds = model.predict(frames)

    avg_pred = preds.mean()

    return{
        "prediction": "fake" if avg_pred > 0.5 else "real",
        "confidence": float(avg_pred)
    }