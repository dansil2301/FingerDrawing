import time
from typing import Any

import cv2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import mediapipe as mp

from Server.DTO.SessionObject import SessionObject
from Server.Gestures.CoordsSmoothing import CoordsSmoothing
from Server.Enums.Action import Action
from Server.Domen.CoordinatesResponse import CoordinatesResponse
from Server.Gestures.GesturesCoords import GesturesCoords
from Server.Enums.RunningMode import RunningMode
from Server.Gestures.GesturesPos import GesturesPos


class HandDetection:
    def __init__(self, model_path: str, running_mode: RunningMode):
        self.model_path = model_path
        self.running_mode = running_mode

        self.start_time = time.time()

        self.gestures_pos = GesturesPos()
        self.coords_smoothing = CoordsSmoothing()

        self.canvas = None
        self.prev_point = None

    def _frame_preprocessing(self, frame: np.ndarray):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        rgb_frame = np.ascontiguousarray(rgb_frame)

        return mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
    
    def create_detector(self) -> Any:
        base_options = python.BaseOptions(model_asset_path=self.model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=self.running_mode.value,
            num_hands=1
        )

        return vision.HandLandmarker.create_from_options(options)
    
    def _get_timestamp_ms(self, session: SessionObject):
        ts = int((time.time() - session.started_at_timestamp) * 1000)
        if session.last_detected_timestamp and ts <= session.last_detected_timestamp:
            ts = session.last_detected_timestamp + 1
        session.last_detected_timestamp = ts
        return ts
    
    def find_hand_coords(self, session: SessionObject, frame: np.ndarray) -> CoordinatesResponse:
        frame = cv2.flip(frame, 1)
        mp_image = self._frame_preprocessing(frame)
        
        timestamp_ms = self._get_timestamp_ms(session)

        result = session.detector.detect_for_video(mp_image, timestamp_ms)
        
        coordinates = CoordinatesResponse()

        for hand_landmarks in result.hand_landmarks:
            smoothed_landmarks = self.coords_smoothing.smooth(session, hand_landmarks)

            # Always pass finger tips to FE
            coordinates.finger_tips = GesturesCoords.finger_tips(smoothed_landmarks)

            if self.gestures_pos.is_fully_open(smoothed_landmarks):
                coordinates.action = Action.ERASE.value
                coordinates.coordinates = GesturesCoords.rectangle_coords(smoothed_landmarks)

            elif self.gestures_pos.is_index(smoothed_landmarks):
                coordinates.action = Action.DRAW.value
                coordinates.coordinates = GesturesCoords.index_coords(smoothed_landmarks)

        return coordinates
        
    def _unpack_result(self, frame: np.ndarray, result: object):
        for hand_landmarks in result.hand_landmarks:
            frame = self._draw_key_point(frame, hand_landmarks)

            if self.gestures_pos.is_fully_open(hand_landmarks):
                frame = self._draw_rectangle(frame, hand_landmarks)
            elif self.gestures_pos.is_index(hand_landmarks):
                frame = self._draw_with_index(frame, hand_landmarks)

            frame = cv2.add(frame, self.canvas)
        return frame
    
    def _draw_rectangle(self, frame: np.ndarray, hand_landmarks: list):
        h, w, _ = frame.shape
        rectangle = GesturesCoords.rectangle_coords(hand_landmarks)

        max_x, max_y = int(rectangle.ru_corner.x * w), int(rectangle.ru_corner.y * h)
        min_x, min_y = int(rectangle.ld_corner.x * w), int(rectangle.ld_corner.y * h)

        self.canvas[min_y:max_y, min_x:max_x] = 0

        cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 2)
        return frame
    
    def _draw_with_index(self, frame, hand_landmarks):
        h, w, _ = frame.shape
        point = GesturesCoords.index_coords(hand_landmarks)

        x, y = int(point.x * w), int(point.y * h)

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
