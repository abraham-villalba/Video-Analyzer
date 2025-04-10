from flask import Blueprint, request, send_from_directory
from api.utils.schemas import AnalyzeVideoRequestSchema, validate_analyze_video_request
from api.utils.response_model import ResponseModel
from api.utils.logger import logger
from api.utils.video_utils import store_video, video_exits, get_audio_file
from api.services.transcription_service import transcribe_audio
from api.services.summarization_service import generate_transcript_summary, generate_holistic_summary
from api.services.keyframe_descriptions_service import generate_keyframe_descriptions
import os


# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    print("Upload request for file?")
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)

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
    
    audio_path = get_audio_file(video_id)
    transcript = transcribe_audio(audio_path)
    transcript_summary = generate_transcript_summary(transcript, data.get('summary_type', 'concise'), data.get('language', 'infer'))
    keyframe_descriptions = generate_keyframe_descriptions(f"uploads/{video_id}/keyframes", data.get('language', 'infer'))
    holistic_summary = generate_holistic_summary(
        transcript, 
        list(map(lambda x: x['description'], keyframe_descriptions)), 
        data.get('summary_type', 'concise'), 
        data.get('language', 'infer')
    )

    response = {
        'transcript': transcript,
        'transcript_summary': transcript_summary,
        'holistic_summary': holistic_summary,
        'topics': [],
        'keyframes': keyframe_descriptions
    }

    return ResponseModel(status='success', data=response).to_json(), 200


