import os
import pytest
import subprocess
from api.utils.video_utils import extract_audio

@pytest.fixture
def sample_video():
    """Provide a path to a sample video"""
    video_path = "uploads/test/test_video.mp4"
    audio_path = "uploads/test/test_audio.wav"

    # Ensure the file doesn't exist before the test starts
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return video_path, audio_path  # This will provide the video and audio paths for the test

def test_extract_audio_runs(sample_video):
    video_path, audio_path = sample_video

    # Run the audio extraction function
    extract_audio(video_path=video_path, audio_path=audio_path) 

    # Check if the audio file was successfully created
    assert os.path.exists(audio_path), "Audio file was not created!"

    # Check if it's the correct file type 
    assert audio_path.endswith('.wav'), "The extracted audio file should be a .wav file."

def test_extract_audio_file_not_found():
    """Test that extract_audio raises an exception if the video file does not exist"""
    non_existent_video_path = "uploads/test/non_existent_video.mp4"
    audio_path = "uploads/test/test_audio.wav"

    # Test if the extract_audio function raises a subprocess.CalledProcessError
    with pytest.raises(FileNotFoundError):
        extract_audio(non_existent_video_path, audio_path)