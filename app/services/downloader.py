import requests
import uuid

def download_file(url):
    filename = f"temp_{uuid.uuid4()}.mp4"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers,stream=True, timeout=15)
    response.raise_for_status()

    if response.status_code != 200:
        raise Exception(f"Download failed with status {response.status_code}")
    
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    return filename