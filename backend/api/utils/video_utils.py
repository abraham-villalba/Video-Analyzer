""" Util functions to interact with video files """
import subprocess
import os
from api.utils.logger import logger
from werkzeug.utils import secure_filename
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')

def extract_audio(video_path : str, audio_path : str) -> None:
    """
    Extracts audio from a video file into a 165kHz WAV file by using ffmepg

    :param video_path: The path of the video to extract audio from
    :type video_path: str
    :param audio_path: The output path to store the audio file
    :type audio_path: str
    :raises FileNotFoundError: If the video file does not exist
    :raises subprocess.CalledProcessError: If an exception is encountered by ffmpeg
    """
    logger.info(f"Extracting audio from: {video_path} to: {audio_path}")
    if not os.path.exists(video_path):
        logger.error(f"File {video_path} does not exists...")
        raise FileNotFoundError(f"File {video_path} does not exist")
    try:
        command = [
            "ffmpeg", "-i", video_path,
            "-n", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            audio_path
        ]
        subprocess.run(command, check=True)
        logger.debug(f"Audio extraction was succesfull!")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during audio extraction: {str(e)}")
        raise e
    
def store_video(video_file):
    """
    Generates an id for a video file and stores it on the system with its corresponding audio file
    :param video_file: The video to store
    :returns id identifier for this video analysis storage
    """
    filename = secure_filename(video_file.filename)
    directory_id = str(uuid4())
    save_dir = os.path.join(UPLOAD_DIR, directory_id)
    logger.info(f"Storing video with (name, id): ({filename}, {directory_id})")

    os.makedirs(save_dir, exist_ok=True)

    video_path = os.path.join(save_dir, filename)
    video_file.save(video_path)

    # Extract audio
    audio_path = os.path.join(save_dir, "audio.wav")
    extract_audio(video_path, audio_path)

    return directory_id