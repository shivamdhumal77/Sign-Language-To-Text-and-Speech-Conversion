import os
import math
import time
import traceback
from collections import deque

import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
from tensorflow.keras.models import load_model

# ---------------- CONFIG ----------------
# UPDATE THIS PATH TO YOUR MODEL
MODEL_PATH = r"E:\\primary\\Desktop\\Sign-Language-To-Text-and-Speech-Conversion-master\\sign_language_AZ_CNN.h5"
CAMERA_ID = 0

# Internal Processing Configs
CANVAS_SIZE = 400      # Size for drawing the skeleton
PREDICT_EVERY = 3      # Run model every 3 frames to save CPU
VOTE_QUEUE = 6         # Smoothing buffer
STABLE_FRAMES = 5      # Confirm letter after 5 consistent predictions
LETTER_COOLDOWN = 1.2  # Pause before same letter can be added again
NO_HAND_SPACE_TIME = 2.0 

# ---------------- INITIALIZATION ----------------
if not os.path.exists(MODEL_PATH):
    print(f"!!! MODEL NOT FOUND AT: {MODEL_PATH} !!!")
    exit()

print("Loading model...")
model = load_model(MODEL_PATH)

# Detect model requirements dynamically
# This fixes the "expected axis -1 to have value 4608" error
_, M_H, M_W, M_C = model.input_shape
print(f"Model loaded. Required Input: {M_W}x{M_H}x{M_C}")

cap = cv2.VideoCapture(CAMERA_ID)
hd = HandDetector(maxHands=1, detectionCon=0.7)

# State Variables
vote_queue = deque(maxlen=VOTE_QUEUE)
sentence = ""
last_added = None
last_added_time = 0
last_hand_time = time.time()
frame_idx = 0

def dist_2d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

print("Running. Press ESC to quit, 'C' to clear text.")

# ---------------- MAIN LOOP ----------------
while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    frame_idx += 1
    h_orig, w_orig, _ = frame.shape

    # Find hand
    hands, frame = hd.findHands(frame, draw=True, flipType=False)
    
    display_char = None

    if hands:
        last_hand_time = time.time()
        hand = hands[0]
        bbox = hand['bbox'] # [x, y, w, h]
        pts = hand['lmList'] # 21 points
        
        x, y, w, h = bbox

        # 1. Create the White Skeleton Canvas (400x400)
        white = np.ones((CANVAS_SIZE, CANVAS_SIZE, 3), dtype=np.uint8) * 255
        os_x = (CANVAS_SIZE - w) // 2
        os_y = (CANVAS_SIZE - h) // 2

        # Draw Skeleton lines (matching original approach)
        def draw_l(img, p1_idx, p2_idx):
            p1 = (int(pts[p1_idx][0] - x + os_x), int(pts[p1_idx][1] - y + os_y))
            p2 = (int(pts[p2_idx][0] - x + os_x), int(pts[p2_idx][1] - y + os_y))
            cv2.line(img, p1, p2, (0, 255, 0), 3)

        # Connect joints
        for i in [0, 5, 9, 13, 17]:
            if i < 17: draw_l(white, i, i+4 if i==0 else i+4) # simplistic palm
        for start in [1, 5, 9, 13, 17]:
            for j in range(start, start+3): draw_l(white, j, j+1)
        draw_l(white, 0, 1); draw_l(white, 0, 5); draw_l(white, 5, 9); 
        draw_l(white, 9, 13); draw_l(white, 13, 17); draw_l(white, 0, 17)

        for p in pts:
            cv2.circle(white, (int(p[0]-x+os_x), int(p[1]-y+os_y)), 2, (0,0,255), -1)

        cv2.imshow("Skeleton", white)

        # 2. Prediction with Resizing
        if frame_idx % PREDICT_EVERY == 0:
            # RESIZE to model requirement (e.g. 50x50 or 64x64)
            white_resized = cv2.resize(white, (M_W, M_H))
            # NORMALIZE to 0-1
            model_input = (white_resized.astype("float32") / 255.0).reshape(1, M_H, M_W, M_C)
            
            try:
                probs = model.predict(model_input, verbose=0)[0]
                ch1 = int(np.argmax(probs))
                probs[ch1] = 0
                ch2 = int(np.argmax(probs))

                # --- HEURISTIC MAPPING ---
                final_char = None
                c1 = ch1
                pl = [ch1, ch2]

                # Group 0 Mapping (A, E, M, N, S, T)
                if c1 in [5, 3, 6, 4, 1, 2]:
                    # If all fingers are curled down
                    if pts[8][1] > pts[6][1] and pts[12][1] > pts[10][1] and pts[16][1] > pts[14][1]:
                        c1 = 0

                # Final Letter Decision Logic
                if c1 == 0:
                    if pts[4][0] < pts[6][0]: final_char = 'A'
                    elif pts[4][1] > pts[8][1] and pts[4][1] > pts[12][1]: final_char = 'E'
                    elif pts[4][0] > pts[14][0]: final_char = 'M'
                    else: final_char = 'S'
                elif c1 == 2:
                    final_char = 'C' if dist_2d(pts[8], pts[4]) > 50 else 'O'
                elif c1 == 3:
                    final_char = 'G' if dist_2d(pts[8], pts[12]) > 60 else 'H'
                elif c1 == 1:
                    # B, D, F, I, K, R, U, V, W
                    if pts[8][1] < pts[6][1] and pts[12][1] < pts[10][1] and pts[16][1] < pts[14][1]: final_char = 'B'
                    elif pts[8][1] < pts[6][1] and pts[12][1] > pts[10][1]: final_char = 'D'
                    elif pts[8][1] > pts[6][1] and pts[18][1] < pts[20][1]: final_char = 'I'
                    else: final_char = 'V'
                elif c1 == 4: final_char = 'L'
                elif c1 == 5: final_char = 'P'
                elif c1 == 6: final_char = 'X'
                elif c1 == 7: final_char = 'Y'

                if final_char:
                    vote_queue.append(final_char)
            except Exception as e:
                print("Prediction Error:", e)

        if vote_queue:
            display_char = max(set(vote_queue), key=vote_queue.count)
            
            # Sentence Logic
            now = time.time()
            if vote_queue.count(display_char) >= STABLE_FRAMES:
                if display_char != last_added or (now - last_added_time) > LETTER_COOLDOWN:
                    sentence += display_char
                    last_added = display_char
                    last_added_time = now
                    vote_queue.clear()
    else:
        # Auto-spacing
        if time.time() - last_hand_time > NO_HAND_SPACE_TIME:
            if sentence and not sentence.endswith(" "):
                sentence += " "
                last_hand_time = time.time()

    # 3. UI RENDER
    # Background for text
    cv2.rectangle(frame, (0, h_orig-60), (w_orig, h_orig), (0,0,0), -1)
    cv2.putText(frame, sentence[-30:], (20, h_orig-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    
    if display_char:
        cv2.putText(frame, f"Predicting: {display_char}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("Sign Language Translator", frame)

    key = cv2.waitKey(1)
    if key == 27: break
    if key == ord('c'): sentence = ""

cap.release()
cv2.destroyAllWindows()