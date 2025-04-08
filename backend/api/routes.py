from flask import Blueprint, request
from api.utils.schemas import AnalyzeVideoRequestSchema, validate_analyze_video_request
from api.utils.response_model import ResponseModel
from api.utils.logger import logger
from api.utils.video_utils import store_video



# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/upload_video', methods=['POST'])
def upload_video():
    """ Endpoint to submit a video for later processing """
    if 'video' not in request.files:
        logger.error("Error uploading video, file is missing")
        return ResponseModel(status="error", error="Error uploading video, file is missing").to_json(), 400

    video = request.files['video']
    print(video)
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
    

    print(f"Request: {data}")
    return ResponseModel(status='success', data={'response': data}).to_json(), 200


