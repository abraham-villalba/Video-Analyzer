""" Configuration settings for the Flask app. """

import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    """ Base configuration. """
    DEBUG = bool(os.getenv('DEBUG', 'False'))

    LLM_WRAPPER = os.getenv('LLM_WRAPPER')
    if not LLM_WRAPPER:
        raise ValueError('LLM_WRAPPER environment variable is not set.')
    
    LLM_MODEL = os.getenv('LLM_MODEL')
    if not LLM_MODEL:
        raise ValueError('LLM_MODEL environment variable is not set.')
    
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError('OPENAI_API_KEY environment variable is not set.')