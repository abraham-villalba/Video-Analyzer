"""
"""

import logging
from datetime import datetime
import os

# Make sure logs directory exits
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Logger configuration
logger = logging.getLogger("video_analyzer")
logger.setLevel(logging.DEBUG)  # Use INFO or WARNING in production

# Generate timestamp for log file
timestamp = datetime.now().strftime("%Y_%m_%d_%H:%M:%S")

# File handler
file_handler = logging.FileHandler(f"{LOG_DIR}/{timestamp}_video_analyzer.log")
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)