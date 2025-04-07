""" Util functions to interact with video files """
import subprocess
from api.utils.logger import logger

def extract_audio(video_path : str, audio_path : str) -> None:
    """
    Extracts audio from a video file into a 165kHz WAV file
    :param video_path: The path of the video to extract audio from
    :param audio_path: The output path to store the audio file
    """
    logger.info(f"Extracting audio from: {video_path} to: {audio_path}")
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