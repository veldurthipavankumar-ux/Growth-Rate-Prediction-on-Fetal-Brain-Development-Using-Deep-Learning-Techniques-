import cv2
import numpy as np
import threading
import time

print("🚗 Driver Drowsiness Detection - LOUD VISUAL ALERTS")
print("👁️  Close eyes for 2 seconds → MASSIVE RED SCREEN + FLASHING")
print("ESC to exit")

# OpenCV cascades (built-in)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Detection variables
COUNTER = 0
ALARM_ON = False
EYES_THRESHOLD = 35
FLASH_COUNTER = 0

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def flash_screen():
    """Flash entire screen RED when drowsy"""
    global FLASH_COUNTER
    while True:
        if ALARM_ON:
            FLASH_COUNTER += 1
            time.sleep(0.2)
        else:
            FLASH_COUNTER = 0
            time.sleep(0.1)

# Start flashing thread
flash_thread = threading.Thread(target=flash_screen, daemon=True)
flash_thread.start()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Face + eye detection
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
    eyes_detected = 0
    
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 3, minSize=(20, 20))
        eyes_detected += len(eyes)
        
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
    
    # Drowsiness detection
    if eyes_detected < 2:
        COUNTER += 1
    else:
        COUNTER = 0
    
    # MASSIVE VISUAL STATUS
    cv2.putText(frame, f"EYES: {eyes_detected} | COUNTER: {COUNTER}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
    
    # *** DROWSINESS ALERT - IMPOSSIBLE TO MISS ***
    if COUNTER > EYES_THRESHOLD:
        ALARM_ON = True
        
        # FLASHING FULL SCREEN RED
        if FLASH_COUNTER % 4 < 2:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (640, 480), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # HUGE TEXT
        cv2.putText(frame, "🚨 DROWSY DETECTED 🚨", (100, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
        cv2.putText(frame, "WAKE UP!!!", (150, 300),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 4)
        
        # THICK RED BORDER
        cv2.rectangle(frame, (0, 0), (640, 480), (0, 0, 255), 15)
        
    else:
        ALARM_ON = False
        cv2.putText(frame, "✅ EYES OPEN - SAFE ✅", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    
    cv2.imshow("DROWSINESS DETECTION - FULL SCREEN ALERTS", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Program ended - NO SOUND NEEDED!")
