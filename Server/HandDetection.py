import time

import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import mediapipe as mp

from Server.Enums.RunningMode import RunningMode


class HandDetection:
    def __init__(self, model_path: str, running_mode: RunningMode, num_hands: int):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=running_mode.value,
            num_hands=num_hands
        )

        self.detector = vision.HandLandmarker.create_from_options(options)

        self.start_time = time.time()

    def find_hand(self, frame: np.ndarray):
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        result = self.detector.detect_for_video(mp_image, timestamp_ms)

        frame = self._unpack_result(frame, result)
        
        return frame

    def _unpack_result(self, frame: np.ndarray, result: object):
        for hand_landmarks in result.hand_landmarks:
            frame = self._draw_key_point(frame, hand_landmarks)
        return frame    

    def _draw_key_point(self, frame: np.ndarray, hand_landmarks: list):
        h, w, _ = frame.shape
        for lm in hand_landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame
