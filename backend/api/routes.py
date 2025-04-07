from flask import Blueprint, request
from api.utils.schemas import AnalyzeVideoRequestSchema, validate_analyze_video_request
from api.utils.response_model import ResponseModel


# Create a Blueprint object to define the routes
api_bp = Blueprint('api', __name__) 

@api_bp.route('/analyze_video', methods=['POST'])
def analyze_video():
    """ Handles Video Analyzis endpoint """
    data, errors = validate_analyze_video_request(request.get_json(), AnalyzeVideoRequestSchema())

    if errors:
        return ResponseModel(status="error", error=errors).to_json(), 400 # Bad Request

    print(f"Request: {data}")
    return ResponseModel(status='success', data={'response': data}).to_json(), 200


