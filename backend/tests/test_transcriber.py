import os
import pytest
from api.utils.video_utils import extract_audio
from api.services.transcription_service import transcribe_audio

@pytest.fixture
def sample_audio():
    """Provide a path to a sample audio"""
    video_path = "uploads/test/test_video.mp4"
    audio_path = "uploads/test/test_audio.wav"

    # Ensure the file doesn't exist before the test starts
    if not os.path.exists(audio_path):
        extract_audio(video_path,audio_path)

    return audio_path  # This will provide the audio path for the test

def test_transcriber_produces_output(sample_audio):
    audio_path = sample_audio
    transcription = transcribe_audio(audio_path)

    # Test transcription is not empty
    assert len(transcription) != 0, "Transcription produced an empty string"

def test_transcribe_audio_file_not_found():
    """Test that transcribe_audio raises an exception if the audio file does not exist"""
    non_existent_audio_path = "uploads/test/non_existent_audio.wav"

    # Test if the extract_audio function raises a FileNotFoundError
    with pytest.raises(FileNotFoundError):
        transcribe_audio(non_existent_audio_path)