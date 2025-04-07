"""
This module contains the ResponseModel class which is used to create a response object
"""
from datetime import datetime
from flask import jsonify

class ResponseModel:
    """ A class to represent the response object. """
    def __init__(self, status: str, data=None, error=None):
        self.status = status
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        """ Converts the response object to a dictionary. """
        response = {
            "status": self.status,
            "timestamp": self.timestamp
        }
        if self.data:
            response["data"] = self.data
        if self.error:
            response["error"] = self.error
        return response
    
    def to_json(self):
        """ Converts the response object to a JSON string. """
        return jsonify(self.to_dict())