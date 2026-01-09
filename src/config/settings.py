import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "sign_language_AZ_CNN.h5"))
MODEL_INPUT_SIZE = (64, 64)

# Camera Configuration
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))

# Hand Detection Configuration
HAND_DETECTION_CONFIDENCE = float(os.getenv("HAND_DETECTION_CONFIDENCE", "0.7"))
MAX_HANDS = int(os.getenv("MAX_HANDS", "1"))

# Canvas Configuration
CANVAS_SIZE = int(os.getenv("CANVAS_SIZE", "400"))

# Prediction Configuration
PREDICT_EVERY = int(os.getenv("PREDICT_EVERY", "4"))
VOTE_QUEUE_SIZE = int(os.getenv("VOTE_QUEUE_SIZE", "6"))
STABLE_FRAMES = int(os.getenv("STABLE_FRAMES", "5"))

# Timing Configuration
LETTER_COOLDOWN = float(os.getenv("LETTER_COOLDOWN", "1.2"))
HAND_STABLE_TIME = float(os.getenv("HAND_STABLE_TIME", "2.0"))
NO_HAND_SPACE_TIME = float(os.getenv("NO_HAND_SPACE_TIME", "4.0"))

# Flask Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Word Dictionary Configuration
WORD_RECOMMENDATIONS_LIMIT = int(os.getenv("WORD_RECOMMENDATIONS_LIMIT", "5"))
