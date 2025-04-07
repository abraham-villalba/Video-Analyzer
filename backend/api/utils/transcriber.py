import whisper
import os
from api.utils.logger import logger

model = whisper.load_model('base')

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
    
    result = model.transcribe(audio_path)
    logger.debug(f"Result from transcribing audio file: {result}")
    return result['text']