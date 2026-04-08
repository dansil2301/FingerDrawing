import cv2
import numpy as np
import mediapipe as mp
import time

from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera failed to open")
    exit()

hand_detector = HandDetection("hand_landmarker.task", RunningMode.VIDEO, 1)

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