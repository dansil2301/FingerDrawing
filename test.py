import cv2
import numpy as np
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = "hand_landmarker.task"

BaseOptions = python.BaseOptions
HandLandmarker = vision.HandLandmarker
HandLandmarkerOptions = vision.HandLandmarkerOptions
VisionRunningMode = vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera failed to open")
    exit()

ret, frame = cap.read()
h, w, _ = frame.shape
canvas = np.zeros((h, w, 3), dtype=np.uint8)
prev_point = None

start_time = time.time()

with HandLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int((time.time() - start_time) * 1000)

        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        h, w, _ = frame.shape

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:

                # Draw landmarks
                for lm in hand_landmarks:
                    x, y = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                def is_up(tip, dip):
                    return hand_landmarks[tip].y < hand_landmarks[dip].y
                
                def is_thumb_up():
                    return hand_landmarks[4].x > hand_landmarks[3].x if hand_landmarks[17].x < hand_landmarks[0].x else hand_landmarks[4].x < hand_landmarks[3].x

                fingers = {
                    "Thumb":  is_thumb_up(),
                    "Index":  is_up(8, 7),
                    "Middle": is_up(12, 11),
                    "Ring":   is_up(16, 15),
                    "Pinky":  is_up(20, 19),
                }

                up_names = [name for name, up in fingers.items() if up]
                total = len(up_names)

                if total == 1 and fingers["Index"]:
                    index_tip = hand_landmarks[8]

                    x, y = int(index_tip.x * w), int(index_tip.y * h)

                    if prev_point is not None:
                        cv2.line(canvas, prev_point, (x, y), (255, 0, 0), 5)

                    prev_point = (x, y)
                else:
                    prev_point = None

                cv2.putText(frame, f"{total} finger{'s' if total != 1 else ''}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                cv2.putText(frame, " ".join(up_names),
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        frame = cv2.add(frame, canvas)
        cv2.imshow("Hands (New API)", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()