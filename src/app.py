import os
import cv2
import time
import threading
from dotenv import load_dotenv

from flask import Flask, render_template, Response, jsonify, request

from src.config.settings import *
from src.models.sign_model import SignLanguageModel
from src.models.word_dictionary import WordRecommender
from src.services.hand_detector import HandDetectionService
from src.services.video_processor import VideoProcessor
from src.utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logger(__name__, LOG_LEVEL, LOG_FORMAT)

# Initialize Flask app
app = Flask(__name__)

# Global state
sentence = ""
current_letter = ""
recommendations = []
video_processor = None
hand_detector = None
sign_model = None
word_recommender = None
processing_thread = None
stop_processing = False

def initialize_services():
    """Initialize all services."""
    global video_processor, hand_detector, sign_model, word_recommender
    
    try:
        logger.info("Initializing services...")
        
        # Initialize model
        sign_model = SignLanguageModel(MODEL_PATH)
        
        # Initialize hand detector
        hand_detector = HandDetectionService(
            max_hands=MAX_HANDS,
            detection_confidence=HAND_DETECTION_CONFIDENCE
        )
        
        # Initialize video processor
        video_processor = VideoProcessor(
            camera_index=CAMERA_INDEX,
            canvas_size=CANVAS_SIZE,
            predict_every=PREDICT_EVERY,
            vote_queue_size=VOTE_QUEUE_SIZE,
            letter_cooldown=LETTER_COOLDOWN,
            hand_stable_time=HAND_STABLE_TIME,
            no_hand_space_time=NO_HAND_SPACE_TIME
        )
        
        # Initialize word recommender
        word_recommender = WordRecommender(limit=WORD_RECOMMENDATIONS_LIMIT)
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

def update_recommendations():
    """Update word recommendations based on current sentence."""
    global sentence, recommendations, word_recommender
    
    try:
        if word_recommender is None:
            return
        
        words = sentence.split()
        if not words:
            recommendations = []
            return
        
        current_word = words[-1]
        recommendations = word_recommender.get_recommendations(current_word)
        
    except Exception as e:
        logger.error(f"Error updating recommendations: {e}")

def generate_frames():
    """Generate video frames with sign language detection."""
    global sentence, current_letter, video_processor, hand_detector, sign_model
    
    if video_processor is None or hand_detector is None or sign_model is None:
        logger.error("Services not initialized")
        return
    
    logger.info("Starting frame generation")
    
    try:
        while not stop_processing:
            success, frame = video_processor.get_frame()
            if not success:
                break
            
            # Detect hands
            hands, frame = hand_detector.detect_hands(frame)
            
            if hands:
                video_processor.update_last_hand_time()
                hand = hands[0]
                
                # Extract and process hand ROI
                hand_roi = hand_detector.extract_hand_roi(
                    frame, hand, CANVAS_SIZE
                )
                
                # Make prediction if needed
                if video_processor.should_predict():
                    processed_roi = video_processor.process_hand_roi(
                        hand_roi, sign_model, MODEL_INPUT_SIZE
                    )
                    
                    if processed_roi is not None:
                        predicted_letter, confidence = sign_model.predict(processed_roi)
                        if predicted_letter:
                            video_processor.add_prediction(predicted_letter)
                
                # Get current letter from vote queue
                current_letter = video_processor.get_current_letter()
                
                # Check if letter should be added to sentence
                if current_letter and video_processor.should_add_letter(current_letter):
                    sentence += current_letter
                    video_processor.add_letter(current_letter)
                    update_recommendations()
            
            else:
                # No hand detected - check if space should be added
                if video_processor.should_add_space():
                    if sentence and not sentence.endswith(" "):
                        sentence += " "
                        update_recommendations()
            
            # Encode frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       buffer.tobytes() + b'\r\n')
    
    except Exception as e:
        logger.error(f"Error in frame generation: {e}")
    
    finally:
        logger.info("Frame generation stopped")

@app.route('/')
def index():
    """Render main page."""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_text')
def get_text():
    """Get current text state."""
    return jsonify({
        "sentence": sentence,
        "letter": current_letter,
        "recs": recommendations
    })

@app.route('/clear', methods=['POST', 'GET'])
def clear():
    """Clear current text."""
    global sentence, current_letter, video_processor
    
    try:
        sentence = ""
        current_letter = ""
        
        if video_processor:
            video_processor.reset_state()
        
        update_recommendations()
        return jsonify({"ok": True})
    
    except Exception as e:
        logger.error(f"Error clearing text: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/append_suggestion', methods=['POST'])
def append_suggestion():
    """Append suggested word to sentence."""
    global sentence
    
    try:
        data = request.get_json()
        word = data.get('word', '')
        
        if word:
            words = sentence.split()
            if words:
                words[-1] = word
                sentence = ' '.join(words)
            else:
                sentence = word
            update_recommendations()
        
        return jsonify({"ok": True, "sentence": sentence})
    
    except Exception as e:
        logger.error(f"Error appending suggestion: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/delete_last', methods=['POST'])
def delete_last():
    """Delete last character from sentence."""
    global sentence
    
    try:
        if sentence:
            sentence = sentence[:-1]
            update_recommendations()
        return jsonify({"ok": True, "sentence": sentence})
    
    except Exception as e:
        logger.error(f"Error deleting last character: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/add_space', methods=['POST'])
def add_space():
    """Add space to sentence."""
    global sentence
    
    try:
        if sentence and not sentence.endswith(" "):
            sentence += " "
            update_recommendations()
        return jsonify({"ok": True, "sentence": sentence})
    
    except Exception as e:
        logger.error(f"Error adding space: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        status = {
            "status": "healthy",
            "services": {
                "video_processor": video_processor is not None,
                "hand_detector": hand_detector is not None,
                "sign_model": sign_model is not None,
                "word_recommender": word_recommender is not None
            }
        }
        return jsonify(status)
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

def cleanup():
    """Cleanup resources."""
    global stop_processing, video_processor
    
    logger.info("Cleaning up resources...")
    stop_processing = True
    
    if video_processor:
        video_processor.release()
    
    logger.info("Cleanup completed")

if __name__ == "__main__":
    try:
        # Initialize services
        initialize_services()
        
        # Setup cleanup on exit
        import atexit
        atexit.register(cleanup)
        
        logger.info(f"Starting Flask app on {FLASK_HOST}:{FLASK_PORT}")
        app.run(
            host=FLASK_HOST,
            port=FLASK_PORT,
            debug=FLASK_DEBUG,
            threaded=True
        )
    
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    finally:
        cleanup()
