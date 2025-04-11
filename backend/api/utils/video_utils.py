""" Util functions to interact with video files """
import subprocess
import os
import glob
import json
from api.utils.logger import logger
from api.services.transcription_service import transcribe_audio
from werkzeug.utils import secure_filename
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv('UPLOAD_DIR')

if not UPLOAD_DIR:
    # Default fallback to relative path in local development
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads'))

logger.debug(f"[DEBUG] Using UPLOAD_DIR={UPLOAD_DIR}")
MAX_KEYFRAMES = int(os.getenv('MAX_KEYFRAMES', 10))
MAX_KEYFRAMES = min(MAX_KEYFRAMES, 20) # Limit to 20 keyframes to avoid excessive processing

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
    if not os.path.exists(os.path.dirname(audio_path)):
        logger.error(f"Directory {os.path.dirname(audio_path)} does not exist")
        raise FileNotFoundError(f"Directory {os.path.dirname(audio_path)} does not exist")
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
    
def extract_keyframes(video_path: str, output_dir: str, max_frames: int = 20) -> None:
    """
    Extracts up to `max_frames` visually distinct keyframes from a video using FFmpeg's scene detection.

    :param video_path: Path to the input video.
    :param output_dir: Directory to save the extracted keyframes.
    :param max_frames: Maximum number of keyframes to extract.
    :raises FileNotFoundError: If the video file does not exist.
    :raises subprocess.CalledProcessError: If ffmpeg fails during extraction.
    """
    logger.info(f"Extracting up to {max_frames} keyframes from: {video_path}")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} does not exist")

    os.makedirs(output_dir, exist_ok=True)

    # Output template path for frames
    output_template = os.path.join(output_dir, "frame_%02d.jpg")

    # FFmpeg command using scene detection to extract distinct frames
    command = [
        "ffmpeg",
        "-i", video_path,
        "-f", "image2",
        "-vf", "select='eq(pict_type,PICT_TYPE_I)'",
        "-vsync", "vfr",
        output_template
    ]

    try:
        subprocess.run(command, check=True)
        logger.info(f"Keyframe extraction successful. Frames saved to {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error during keyframe extraction: {str(e)}")
        raise e
    
    # Gather all extracted frames
    frame_paths = sorted(glob.glob(os.path.join(output_dir, "frame_*.jpg")))

    total_frames = len(frame_paths)
    logger.info(f"Total keyframes extracted: {total_frames}")

    # Downsample if needed
    if total_frames > max_frames:
        logger.info(f"Downsampling to {max_frames} frames evenly.")

        # Select evenly spaced indices
        selected_indices = set(
            round(i * (total_frames - 1) / (max_frames - 1)) for i in range(max_frames)
        )
        logger.info(f"Indexes choosen to be kept: {selected_indices}")

        for idx, frame_path in enumerate(frame_paths):
            if idx not in selected_indices:
                os.remove(frame_path)

        # Rename retained frames to frame_00.jpg, frame_01.jpg, etc.
        retained_paths = sorted(glob.glob(os.path.join(output_dir, "frame_*.jpg")))
        for i, old_path in enumerate(retained_paths):
            new_path = os.path.join(output_dir, f"frame_{i:02d}.jpg")
            os.rename(old_path, new_path)

    logger.info(f"Keyframe extraction complete. {min(total_frames, max_frames)} frames retained.")

def store_video(video_file):
    """
    Generates an id for a video file and stores it on the system with its corresponding audio file, keyframes and transcript
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

    # Extract keyframes
    keyframes_dir = os.path.join(save_dir, "keyframes")
    os.makedirs(keyframes_dir, exist_ok=True)
    extract_keyframes(video_path, keyframes_dir, MAX_KEYFRAMES)

    # Generate and store transcript
    transcript_path = os.path.join(save_dir, "data.json")
    transcript = transcribe_audio(audio_path)
    with open(transcript_path, 'w') as f:
        json.dump({"transcript": transcript}, f)
    logger.info(f"Transcript stored in {transcript_path}")

    return directory_id

def video_exits(video_id):
    video_dir = os.path.join(UPLOAD_DIR, video_id)
    return os.path.exists(video_dir)

def get_audio_file(video_id):
    video_dir = os.path.join(UPLOAD_DIR, video_id)
    audio_path = os.path.join(video_dir, "audio.wav")
    return audio_path if os.path.exists(audio_path) else None