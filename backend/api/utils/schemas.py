"""
Includes request schemas for the API endpoints.
"""
from marshmallow import Schema, fields, ValidationError

class AnalyzeVideoRequestSchema(Schema):
    """ Schema for the analyze video request. """
    # Required fields

def validate_analyze_video_request(data, schema):
    """ Validates the chat request data. """
    try:
        return schema.load(data), None
    except ValidationError as e:
        return False, e.messages