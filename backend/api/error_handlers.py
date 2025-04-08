from api.utils.response_model import ResponseModel

def register_error_handlers(app):
    """ Registers error handlers for the Flask app. """
    @app.errorhandler(404)
    def not_found(_):
        return ResponseModel(status='error', error={'code': 404, 'message': 'Not Found'}).to_json(), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return ResponseModel(status='error', error={'code': 500, 'message': 'Internal Server Error'}).to_json(), 500
    
    @app.errorhandler(400)
    def bad_request(_):
        return ResponseModel(status='error', error={'code': 400, 'message': 'Bad Request'}).to_json(), 400
    
    @app.errorhandler(405)
    def method_not_allowed(_):
        return ResponseModel(status='error', error={'code': 405, 'message': 'Method Not Allowed'}).to_json(), 405
    
    @app.errorhandler(415)
    def unsupported_media_type(_):
        return ResponseModel(status='error', error={'code': 415, 'message': 'Unsupported Media Type'}).to_json(), 415
    
    # In case of any other error, return a generic error message
    @app.errorhandler(Exception)
    def generic_error(error):
        print(error)
        return ResponseModel(status='error', error={'code': 500, 'message': 'Internal Server Error'}).to_json(), 500