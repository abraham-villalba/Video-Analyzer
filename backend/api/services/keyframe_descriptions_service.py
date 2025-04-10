from PIL import Image
import io
import os
import base64
import json
from api.config import Config
from api.utils.logger import logger
from openai import OpenAI

# Languages dictionary for mapping language codes to names
LANGUAGES = {
    'en': 'english',
    'es': 'spanish',
    'fr': 'french',
    'de': 'deutch',
    'infer': 'english'
}

# OpenAI client configuration
client = OpenAI(
    api_key=Config.OPENAI_API_KEY,
    timeout=100,
    max_retries=2,
)

# JSON structure for the descriptions schema
json_structure = {
    "type": "json_schema",
    "json_schema": {
        "name": "image_descriptions",
        "schema": {
            "type": "object",
            "properties": {
                "descriptions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "frame_number": {"type": "integer"},
                            "description": {"type": "string"}
                        },
                        "required": ["frame_number", "description"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["descriptions"],
            "additionalProperties": False
        },
        "strict": True
    }
}

# Function to encode images from their file path with resizing
def encode_image(image_path: str) -> str:
    """Encode an image file into base64"""
    try:        
        with open(image_path, 'rb') as image:
            return base64.b64encode(image.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image {image_path}: {e}")
        return None

# Function to encode all images in a given directory
def encode_images(keyframes_path: str) -> list:
    """Iterates over images in a directory and returns them as base64 encoded strings"""
    images = []
    for file_name in os.listdir(keyframes_path):
        if file_name.endswith(('.jpg', '.jpeg', '.png')):
            file_path = os.path.join(keyframes_path, file_name)
            base64_image = encode_image(file_path)
            if base64_image:
                images.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "low"
                    }
                })
    return images

def generate_keyframe_descriptions(keyframes_path: str, language='en'):
    """
    Generate descriptions for images in the specified directory

    :param keyframes_path: Path to the directory containing keyframe images.
    :type keyframes_path: str
    :param language: Language to generate the keyframe descriptions,
    :type language: str
    :return: A list of dictionaries with image paths and their corresponding descriptions.
    """
    try:
        # Get images as base64 encoded strings
        encoded_images = encode_images(keyframes_path)
        # Prepare the user content for the OpenAI model as prompt
        user_content = [
            {
                "type": "text",
                "text": f"These are frames from a video. Analyze each frame and provide a description of each one of them."
            },
        ]
        for img in encoded_images:
            user_content.append(img)

        logger.info(f"Generating Keyframe descriptions of {len(encoded_images)} frames in {keyframes_path} in {LANGUAGES.get(language, 'english')}.")
        # Prepare the prompt for the OpenAI model
        # Make the OpenAI API call to generate the descriptions
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": f"You are an assistant that provides detailed descriptions for frames in a video in {LANGUAGES.get(language, 'english')}."},
                {
                    "role": "user", 
                    "content": user_content
                },
            ],
            response_format=json_structure,
            max_tokens=1000,
            temperature=0.4
        )
        
        # Parse the response into structured JSON format
        descriptions = json.loads(response.choices[0].message.content)
        return build_response(descriptions, keyframes_path)
    except Exception as e:
        logger.error(f"Error while generating keyframe descriptions: {e}")
        return None
    
def build_response(descriptions, keyframes_path):
    """
    Build a structured response combining each keyframe image path with its corresponding description.

    :param descriptions: A dictionary containing descriptions for each frame.
                         Expected format: {"descriptions": [{"frame_number": 1, "description": "..."}, ...]}
    :param keyframes_path: Path to the directory containing keyframe images.
    :return: A list of dictionaries with image paths and their descriptions.
    """
    response = []

    for item in descriptions.get("descriptions", []):
        frame_number = item["frame_number"]
        description = item["description"]

        # Frame numbers in filenames start at 0
        filename = f"frame_{frame_number - 1:02d}.jpg"
        image_path = os.path.join(keyframes_path, filename)

        response.append({
            "image_path": image_path,
            "description": description
        })

    return response