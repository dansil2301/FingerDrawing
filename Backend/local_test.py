import os

import cv2

from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection


# This is created to test hand detection without FE intervantion
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera failed to open")
    exit()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame = hand_detector.find_hand(frame)

    cv2.imshow("Camera Feed", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()