import cv2
import numpy as np
import time
import logging
from collections import deque
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, camera_index=0, canvas_size=400, predict_every=4, 
                 vote_queue_size=6, letter_cooldown=1.2, hand_stable_time=2.0, 
                 no_hand_space_time=4.0):
        """Initialize video processor."""
        self.camera_index = camera_index
        self.canvas_size = canvas_size
        self.predict_every = predict_every
        self.vote_queue_size = vote_queue_size
        self.letter_cooldown = letter_cooldown
        self.hand_stable_time = hand_stable_time
        self.no_hand_space_time = no_hand_space_time
        
        # Initialize camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {camera_index}")
        
        # State variables
        self.frame_count = 0
        self.vote_queue = deque(maxlen=vote_queue_size)
        self.current_letter = ""
        self.stable_letter = ""
        self.stable_start_time = 0
        self.last_added = ""
        self.last_added_time = 0
        self.last_hand_time = time.time()
        
        logger.info(f"Video processor initialized with camera index {camera_index}")
    
    def get_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Get a single frame from the camera."""
        try:
            success, frame = self.cap.read()
            if not success:
                logger.warning("Failed to read frame from camera")
                return False, None
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            self.frame_count += 1
            
            return True, frame
            
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
            return False, None
    
    def process_hand_roi(self, hand_roi, model, target_size=(64, 64)):
        """Process hand ROI for model prediction."""
        try:
            # Resize to model input size
            processed = cv2.resize(hand_roi, target_size)
            
            # Normalize and reshape for model
            processed = (processed.astype("float32") / 255.0).reshape(
                1, target_size[1], target_size[0], 3
            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Error processing hand ROI: {e}")
            return None
    
    def should_predict(self) -> bool:
        """Check if prediction should be made on current frame."""
        return self.frame_count % self.predict_every == 0
    
    def add_prediction(self, predicted_letter: str):
        """Add prediction to vote queue."""
        self.vote_queue.append(predicted_letter)
    
    def get_current_letter(self) -> str:
        """Get current letter based on vote queue."""
        if not self.vote_queue:
            return ""
        
        return max(set(self.vote_queue), key=self.vote_queue.count)
    
    def should_add_letter(self, current_letter: str) -> bool:
        """Check if letter should be added to sentence."""
        current_time = time.time()
        
        # Check if letter is stable
        if current_letter != self.stable_letter:
            self.stable_letter = current_letter
            self.stable_start_time = current_time
            return False
        
        # Check if stable for required time
        if current_time - self.stable_start_time < self.hand_stable_time:
            return False
        
        # Check cooldown
        if (current_letter == self.last_added and 
            current_time - self.last_added_time < self.letter_cooldown):
            return False
        
        return True
    
    def add_letter(self, letter: str):
        """Add letter to sentence."""
        current_time = time.time()
        self.last_added = letter
        self.last_added_time = current_time
        self.vote_queue.clear()
    
    def should_add_space(self) -> bool:
        """Check if space should be added (no hand detected)."""
        return time.time() - self.last_hand_time > self.no_hand_space_time
    
    def update_last_hand_time(self):
        """Update the last time a hand was detected."""
        self.last_hand_time = time.time()
    
    def reset_state(self):
        """Reset processing state."""
        self.vote_queue.clear()
        self.current_letter = ""
        self.stable_letter = ""
        self.stable_start_time = 0
        self.last_added = ""
        self.last_added_time = 0
        self.last_hand_time = time.time()
    
    def release(self):
        """Release camera resources."""
        if self.cap.isOpened():
            self.cap.release()
            logger.info("Camera released")
    
    def __del__(self):
        """Cleanup on deletion."""
        self.release()
