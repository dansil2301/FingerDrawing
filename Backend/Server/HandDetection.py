import time

import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import mediapipe as mp

from Server.Enums.RunningMode import RunningMode
from Server.Gestures import Gestures


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

        self.gestures = Gestures()

        self.canvas = None
        self.prev_point = None

    def find_hand(self, frame: np.ndarray):
        frame = cv2.flip(frame, 1)

        if self.canvas is None:
            self.canvas = np.zeros_like(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        timestamp_ms = int((time.time() - self.start_time) * 1000)

        result = self.detector.detect_for_video(mp_image, timestamp_ms)

        frame = self._unpack_result(frame, result)
        
        return frame

    def _unpack_result(self, frame: np.ndarray, result: object):
        for hand_landmarks in result.hand_landmarks:
            frame = self._draw_key_point(frame, hand_landmarks)

            is_index = self.gestures.index(hand_landmarks)
            is_open = self.gestures.fully_open(hand_landmarks)

            if is_open:
                print("open")
                frame = self._draw_rectangle(frame, hand_landmarks)
            elif is_index:
                print("index")
                frame = self._draw_with_index(frame, hand_landmarks)

            frame = cv2.add(frame, self.canvas)
        return frame
    
    def _draw_rectangle(self, frame: np.ndarray, hand_landmarks: list):
        h, w, _ = frame.shape

        all_x = [point.x for point in hand_landmarks]
        all_y = [point.y for point in hand_landmarks]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        min_x, min_y = int(min_x * w), int(min_y * h)
        max_x, max_y = int(max_x * w), int(max_y * h)

        self.canvas[min_y:max_y, min_x:max_x] = 0

        cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        return frame
    
    def _draw_with_index(self, frame, hand_landmarks):
        h, w, _ = frame.shape

        index_tip = hand_landmarks[8]
        x, y = int(index_tip.x * w), int(index_tip.y * h)

        if self.prev_point is not None:
            cv2.line(self.canvas, self.prev_point, (x, y), (255, 0, 0), 5)

        self.prev_point = (x, y)

        return frame

    def _draw_key_point(self, frame: np.ndarray, hand_landmarks: list):
        h, w, _ = frame.shape
        for lm in hand_landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        return frame
