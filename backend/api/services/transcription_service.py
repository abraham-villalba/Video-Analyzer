from openai import OpenAI
from api.config import Config
from api.utils.logger import logger
import os


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes the given audio file into text using the Whisper model.

    This function loads an audio file from the given path and returns the
    transcription as a string. 

    :param audio_path: Path to the audio file to be transcribed
    :type audio_path: str
    :returns: Transcribed text from the audio file
    :rtype: str
    :raises FileNotFoundError: If the audio file does not exist
    """
    logger.info(f"Transcribing audio file {audio_path}...")
    # Ensure the file exist
    if not os.path.exists(audio_path):
        logger.error(f"File {audio_path} does not exists...")
        raise FileNotFoundError(f"File {audio_path} does not exist")
    
    try:
        client = OpenAI(
            api_key=Config.OPENAI_API_KEY
        )
        audio_file= open(audio_path, "rb")

        transcription = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe", 
            file=audio_file
        )

        logger.debug(f"Result from transcribing audio file: {transcription.text}")
        return transcription.text
    except Exception as e:
        logger.error(f"Error during audio transcription: {str(e)}")
        raise e

    

