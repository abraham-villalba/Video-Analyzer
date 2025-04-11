import requests
from dotenv import load_dotenv
import os

load_dotenv()

BACKEND_URI = os.environ.get("BACKEND_URI", "http://localhost:5000")

def upload_video(video) -> str:
    try:
        files = {"video": (video.name, video.getvalue())}
        response = requests.post(
            f"{BACKEND_URI}/api/upload_video",
            files=files,
            timeout=100
        )
        if response.status_code == 200:
            data = response.json()["data"]["id"]
            return data
        else:
            raise Exception("Upload failed with status code: " + str(response.status_code))
    except requests.exceptions.RequestException as e:
        print(f"Upload failed: {str(e)}")
        return None
    
def analyze_video(video_id: str, language: str, summary_type: str) -> dict:
    try:
        response = requests.post(
            f"{BACKEND_URI}/api/analyze_video",
            json={
                "video_id": video_id,
                "language": language.lower(),
                "summary_type": summary_type.lower()
            },
            timeout=100
        )
        if response.status_code == 200:
            data = response.json()["data"]
            return data
        else:
            raise Exception("Analysis failed with status code: " + str(response.status_code))
    except requests.exceptions.RequestException as e:
        print(f"Anlysis failed: {str(e)}")
        return None