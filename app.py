import os 
import cv2
import time
import threading
from collections import deque

import numpy as np
from flask import Flask, render_template, Response, jsonify, request
from cvzone.HandTrackingModule import HandDetector
from tensorflow.keras.models import load_model

# ---------------- APP ----------------
app = Flask(__name__)

# ---------------- CONFIG ----------------
MODEL_PATH = r"E:\primary\Desktop\Sign-Language-To-Text-and-Speech-Conversion-master\sign_language_AZ_CNN.h5"
CANVAS_SIZE = 400
PREDICT_EVERY = 4
VOTE_QUEUE = 6
STABLE_FRAMES = 5

LETTER_COOLDOWN = 1.2
HAND_STABLE_TIME = 2
NO_HAND_SPACE_TIME = 4.0

# ---------------- INIT ----------------
model = load_model(MODEL_PATH)
_, M_H, M_W, M_C = model.input_shape

cap = cv2.VideoCapture(0)
hd = HandDetector(maxHands=1, detectionCon=0.7)

# ---------------- GLOBAL STATE ----------------
sentence = ""
current_letter = ""
recommendations = []

vote_queue = deque(maxlen=VOTE_QUEUE)

last_added = ""
last_added_time = 0
last_hand_time = time.time()
frame_idx = 0

stable_letter = ""
stable_start_time = 0

# ---------------- WORD & SENTENCE RECOMMENDATIONS (100+) ----------------
WORD_DICT = [
    # Common Words
    "HELLO", "HELP", "YES", "NO", "PLEASE", "THANKYOU", "SORRY", "WELCOME",
    "GOOD", "BAD", "AMAZING", "NICE", "LOVE", "LIKE", "HATE",

    # Daily Life
    "WATER", "FOOD", "APPLE", "BREAD", "RICE", "MILK", "TEA", "COFFEE",
    "EAT", "DRINK", "SLEEP", "WAKE", "HOME", "OFFICE", "SCHOOL", "COLLEGE",

    # People
    "MOTHER", "FATHER", "BROTHER", "SISTER", "FRIEND", "TEACHER", "STUDENT",

    # Places
    "INDIA", "HOSPITAL", "MARKET", "PARK", "HOTEL", "ROOM",

    # Actions
    "GO", "COME", "STOP", "WAIT", "RUN", "WALK", "SIT", "STAND",

    # Emotions
    "HAPPY", "SAD", "ANGRY", "EXCITED", "TIRED", "SCARED",

    # Technology
    "PHONE", "LAPTOP", "INTERNET", "CAMERA", "MACHINE", "AI", "ROBOT",

    # Sentences
    "HELLO HOW ARE YOU",
    "I NEED HELP",
    "THANK YOU VERY MUCH",
    "PLEASE HELP ME",
    "I AM FINE",
    "GOOD MORNING",
    "GOOD NIGHT",
    "WHAT IS YOUR NAME",
    "MY NAME IS",
    "I AM LEARNING SIGN LANGUAGE",
    "THIS IS AMAZING",
    "I LOVE MACHINE LEARNING",
    "WELCOME TO INDIA",
    "HAVE A NICE DAY",
    "SEE YOU SOON",
    "TAKE CARE",
    "PLEASE WAIT",
    "STOP HERE",
    "GO HOME",
    "I AM HAPPY",
    "I AM SAD",
    "I NEED WATER",
    "I NEED FOOD",
    "CALL THE DOCTOR",
    "OPEN THE DOOR",
    "CLOSE THE DOOR",
    "TURN ON THE LIGHT",
    "TURN OFF THE LIGHT"
]

# ---------------- RECOMMENDATION LOGIC ----------------
def update_recommendations():
    global sentence, recommendations
    words = sentence.split()
    if not words:
        recommendations = []
        return
    
    current_word = words[-1].upper()
    matches = [w for w in WORD_DICT if w.startswith(current_word) and w != current_word]
    recommendations = matches[:5]

# ---------------- VIDEO STREAM ----------------
def generate_frames():
    global sentence, current_letter, frame_idx
    global last_added, last_added_time, last_hand_time
    global stable_letter, stable_start_time

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame_idx += 1

        hands, frame = hd.findHands(frame, draw=True, flipType=False)

        if hands:
            last_hand_time = time.time()
            hand = hands[0]
            x, y, w, h = hand['bbox']
            pts = hand['lmList']

            white = np.ones((CANVAS_SIZE, CANVAS_SIZE, 3), np.uint8) * 255
            os_x = (CANVAS_SIZE - w) // 2
            os_y = (CANVAS_SIZE - h) // 2

            def draw_l(p1, p2):
                p1c = (int(pts[p1][0]-x+os_x), int(pts[p1][1]-y+os_y))
                p2c = (int(pts[p2][0]-x+os_x), int(pts[p2][1]-y+os_y))
                cv2.line(white, p1c, p2c, (0,255,0), 3)

            for s in [0,5,9,13,17]:
                for j in range(s, s+4):
                    if j+1 < len(pts):
                        draw_l(j, j+1)

            for p in pts:
                cv2.circle(white, (int(p[0]-x+os_x), int(p[1]-y+os_y)), 2, (0,0,255), -1)

            if frame_idx % PREDICT_EVERY == 0:
                img = cv2.resize(white, (M_W, M_H))
                img = (img.astype("float32") / 255.0).reshape(1, M_H, M_W, M_C)
                probs = model.predict(img, verbose=0)[0]
                pred_letter = chr(65 + int(np.argmax(probs)))
                vote_queue.append(pred_letter)

            if vote_queue:
                current_letter = max(set(vote_queue), key=vote_queue.count)

                if current_letter != stable_letter:
                    stable_letter = current_letter
                    stable_start_time = time.time()

                if time.time() - stable_start_time >= HAND_STABLE_TIME:
                    now = time.time()
                    if current_letter != last_added or (now - last_added_time) > LETTER_COOLDOWN:
                        sentence += current_letter
                        last_added = current_letter
                        last_added_time = now
                        vote_queue.clear()
                        update_recommendations()

        else:
            if time.time() - last_hand_time > NO_HAND_SPACE_TIME:
                if sentence and not sentence.endswith(" "):
                    sentence += " "
                    last_hand_time = time.time()
                    update_recommendations()

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')

# ---------------- ROUTES ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_text')
def get_text():
    return jsonify({
        "sentence": sentence,
        "letter": current_letter,
        "recs": recommendations
    })

@app.route('/clear', methods=['POST', 'GET'])
def clear():
    global sentence, current_letter, vote_queue
    sentence = ""
    current_letter = ""
    vote_queue.clear()
    update_recommendations()
    return jsonify({"ok": True})

@app.route('/append_suggestion', methods=['POST'])
def append_suggestion():
    global sentence
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

@app.route('/delete_last', methods=['POST'])
def delete_last():
    global sentence
    if sentence:
        sentence = sentence[:-1]
        update_recommendations()
    return jsonify({"ok": True, "sentence": sentence})

@app.route('/add_space', methods=['POST'])
def add_space():
    global sentence
    if sentence and not sentence.endswith(" "):
        sentence += " "
        update_recommendations()
    return jsonify({"ok": True, "sentence": sentence})

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)