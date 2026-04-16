import requests
import uuid

def download_file(url):
    filename = f"temp_{uuid.uuid4()}.mp4"

    headers = {
        "User-"
    }

    response = requests.get(url, stream=True)

    if response.status_code != 200:
        raise Exception("Download Failed")
    
    with open(filename, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)

    return filename