from flask import Flask
from api.routes import api_bp
from flask_cors import CORS
from api.error_handlers import register_error_handlers

def create_app():
    """ Creates a Flask app instance. """
    app = Flask(__name__)
    # Enable CORS
    CORS(app)
    # Load configurations
    app.config.from_object('api.config.Config')

    # Register the Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    register_error_handlers(app)

    return app