"""
Includes request schemas for the API endpoints.
"""
from marshmallow import Schema, fields, ValidationError, validate
from pydantic import BaseModel, Field
from typing import List

class AnalyzeVideoRequestSchema(Schema):
    """ Schema for the analyze video request. """
    # Required fields
    video_id = fields.String(required=True, error_messages={"required": "Video ID field is required for analysis"})
    
    language = fields.String(
        required=True,
        validate=validate.OneOf(["en", "es", "fr", "de", "infer"]),
        error_messages={
            "validator_failed": "Invalid language. Must be one of: en, es, fr, de, infer"
        }
    )

    summary_type = fields.String(
        required=True,
        validate=validate.OneOf(["concise", "detailed"]),
        error_messages={
            "validator_failed": "Invalid summary type. Must be 'concise' or 'detailed'"
        }
    )

def validate_analyze_video_request(data, schema):
    """ Validates the analyze video request data. """
    try:
        return schema.load(data), None
    except ValidationError as e:
        return False, e.messages
    
class TopicResponse(BaseModel):
    """ Schema for topic extraction response."""
    topics: List[str] = Field(description="List of the relevant topics \
        of a transcript and keyframe descriptions.")