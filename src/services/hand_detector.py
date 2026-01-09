import cv2
import numpy as np
import logging
from cvzone.HandTrackingModule import HandDetector

logger = logging.getLogger(__name__)

class HandDetectionService:
    def __init__(self, max_hands=1, detection_confidence=0.7):
        """Initialize hand detection service."""
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.detector = HandDetector(
            maxHands=max_hands, 
            detectionCon=detection_confidence
        )
        logger.info(f"Hand detector initialized with max_hands={max_hands}, confidence={detection_confidence}")
    
    def detect_hands(self, frame):
        """Detect hands in the given frame."""
        try:
            hands, processed_frame = self.detector.findHands(frame, draw=True, flipType=False)
            return hands, processed_frame
        except Exception as e:
            logger.error(f"Hand detection failed: {e}")
            return [], frame
    
    def extract_hand_roi(self, frame, hand_info, canvas_size=400):
        """Extract and process hand region of interest."""
        try:
            x, y, w, h = hand_info['bbox']
            landmarks = hand_info['lmList']
            
            # Create white canvas
            canvas = np.ones((canvas_size, canvas_size, 3), np.uint8) * 255
            
            # Calculate offset to center the hand
            offset_x = (canvas_size - w) // 2
            offset_y = (canvas_size - h) // 2
            
            # Draw hand skeleton on canvas
            self._draw_hand_skeleton(canvas, landmarks, x, y, offset_x, offset_y)
            
            return canvas
            
        except Exception as e:
            logger.error(f"ROI extraction failed: {e}")
            return np.ones((canvas_size, canvas_size, 3), np.uint8) * 255
    
    def _draw_hand_skeleton(self, canvas, landmarks, x, y, offset_x, offset_y):
        """Draw hand skeleton connections on canvas."""
        def draw_line(point1_idx, point2_idx):
            p1 = (int(landmarks[point1_idx][0] - x + offset_x), 
                  int(landmarks[point1_idx][1] - y + offset_y))
            p2 = (int(landmarks[point2_idx][0] - x + offset_x), 
                  int(landmarks[point2_idx][1] - y + offset_y))
            cv2.line(canvas, p1, p2, (0, 255, 0), 3)
        
        # Draw finger connections
        finger_starts = [0, 5, 9, 13, 17]
        for start in finger_starts:
            for i in range(start, start + 4):
                if i + 1 < len(landmarks):
                    draw_line(i, i + 1)
        
        # Draw landmark points
        for landmark in landmarks:
            point = (int(landmark[0] - x + offset_x), 
                    int(landmark[1] - y + offset_y))
            cv2.circle(canvas, point, 2, (0, 0, 255), -1)
