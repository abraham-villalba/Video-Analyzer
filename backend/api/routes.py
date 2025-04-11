from flask import Blueprint, request, send_file
from api.utils.schemas import AnalyzeVideoRequestSchema, validate_analyze_video_request
from api.utils.response_model import ResponseModel
from api.utils.logger import logger
from api.utils.video_utils import store_video, video_exits, get_audio_file
from api.services.transcription_service import transcribe_audio
from api.services.summarization_service import generate_transcript_summary, generate_holistic_summary
from api.services.keyframe_descriptions_service import generate_keyframe_descriptions
from api.services.topics_service import extract_topics
from werkzeug.utils import safe_join
import os
import json
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv('UPLOAD_DIR')

if not UPLOAD_DIR:
    # Default fallback to relative path in local development
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../uploads'))

print(f"[DEBUG] Using UPLOAD_DIR={UPLOAD_DIR}")


# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 


@api_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """ Serve the uploaded keyframe images """

    # Resolve the uploads directory to an absolute path
    base_dir = os.path.abspath(os.path.dirname(__file__)) 
    uploads_dir = os.path.abspath(os.path.join(base_dir, '../', UPLOAD_DIR))

    full_path = safe_join(uploads_dir, filename)
    logger.debug(f"Resolved UPLOAD_DIR: {uploads_dir}")
    logger.debug(f"Full path to serve: {full_path}")
    logger.debug(f"Does file exist? {os.path.exists(full_path)}")

    if not os.path.exists(full_path):
        return ResponseModel(status="error", error="File not found").to_json(), 404

    return send_file(full_path)

@api_bp.route('/upload_video', methods=['POST'])
def upload_video():
    """ Endpoint to submit a video for later processing """
    if 'video' not in request.files:
        logger.error("Error uploading video, file is missing")
        return ResponseModel(status="error", error="Error uploading video, file is missing").to_json(), 400

    video = request.files['video']
    video_id = store_video(video)

    return ResponseModel(status='success', data={'id': video_id}).to_json(), 200

@api_bp.route('/analyze_video', methods=['POST'])
def analyze_video():
    """ Handles Video Analyzis endpoint """
    data, errors = validate_analyze_video_request(request.get_json(), AnalyzeVideoRequestSchema())

    logger.info(f"Analyzing video...")
    logger.debug(f"Analyzing video with data : {data}")

    if errors:
        logger.error(f"Error analyzing video: {errors}")
        return ResponseModel(status="error", error=errors).to_json(), 400 # Bad Request
    
    video_id = data['video_id']
    if not video_exits(video_id):
        logger.error(f"Error analyzing video: Video doesn't exist")
        return ResponseModel(status="error", error=errors).to_json(), 404 # Not Found
    
    # Check if the transcript already exists, if not, generate it
    transcript_path = f"{UPLOAD_DIR}/{video_id}/data.json"
    if not os.path.exists(transcript_path):
        audio_path = get_audio_file(video_id)
        transcript = transcribe_audio(audio_path)
    else:
        with open(transcript_path, 'r') as f:
            file = json.load(f)
        transcript = file.get('transcript', 'No transcript available')


    transcript_summary = generate_transcript_summary(transcript, data.get('summary_type', 'concise'), data.get('language', 'infer'))
    keyframe_descriptions = generate_keyframe_descriptions(f"{UPLOAD_DIR}/{video_id}/keyframes", data.get('language', 'infer'))
    holistic_summary = generate_holistic_summary(
        transcript, 
        list(map(lambda x: x['description'], keyframe_descriptions)), 
        data.get('summary_type', 'concise'), 
        data.get('language', 'infer')
    )
    topics = extract_topics(
        transcript,
        data.get('language', 'infer'),
        list(map(lambda x: x['description'], keyframe_descriptions))
    )

    response = {
        'transcript': transcript,
        'transcript_summary': transcript_summary,
        'holistic_summary': holistic_summary,
        'topics': topics,
        'keyframes': keyframe_descriptions
    }

    return ResponseModel(status='success', data=response).to_json(), 200


