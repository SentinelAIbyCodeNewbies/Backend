import yt_dlp
import uuid
import os

def download_media_ytdlp(url: str) -> str:
    base_name = f"temp_{uuid.uuid4}"

    ydl_opts = {
        'outtmpl' : f'{base_name}.%(ext)s',
        'format': 'bestvideo[ext=mp4]/best[ext=mp4]/best',

        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        downloaded_file = None
        for file in os.listdir('.'):
            if file.startswith(base_name):
                downloaded_file = file
                break
        
        if not downloaded_file:
            raise Exception("yt-dlp finished but the file could not be found")
        
        return downloaded_file
    
    except Exception as e:
        raise Exception(f"yt-dlp extraction failed: {str(e)}")