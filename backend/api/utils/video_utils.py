""" Util functions to interact with video files """
import subprocess
import os
from api.utils.logger import logger

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