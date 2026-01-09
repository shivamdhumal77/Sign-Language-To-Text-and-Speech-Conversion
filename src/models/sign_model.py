import logging
from pathlib import Path
from tensorflow.keras.models import load_model
from .word_dictionary import WORD_DICT

logger = logging.getLogger(__name__)

class SignLanguageModel:
    def __init__(self, model_path: str):
        """Initialize the sign language recognition model."""
        self.model_path = Path(model_path)
        self.model = None
        self.input_shape = None
        self._load_model()
    
    def _load_model(self):
        """Load the trained model."""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model = load_model(self.model_path)
            self.input_shape = self.model.input_shape
            logger.info(f"Model loaded successfully from {self.model_path}")
            logger.info(f"Model input shape: {self.input_shape}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def predict(self, processed_image):
        """Make prediction on processed hand image."""
        try:
            if self.model is None:
                raise ValueError("Model not loaded")
            
            prediction = self.model.predict(processed_image, verbose=0)
            predicted_class = int(prediction.argmax())
            predicted_letter = chr(65 + predicted_class)
            confidence = float(prediction[0][predicted_class])
            
            return predicted_letter, confidence
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None, 0.0
    
    @property
    def model_info(self):
        """Get model information."""
        if self.model is None:
            return None
        
        return {
            "input_shape": self.input_shape,
            "model_path": str(self.model_path),
            "loaded": True
        }
