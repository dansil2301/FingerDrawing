import numpy as np

from Server.DTO.Point import Point
from Server.DTO.Rectangle import Rectangle


class GesturesCoords:
    @classmethod
    def rectangle_coords(cls, frame: np.ndarray, hand_landmarks: list) -> Rectangle:
        h, w, _ = frame.shape

        all_x = [point.x for point in hand_landmarks]
        all_y = [point.y for point in hand_landmarks]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        min_x, min_y = int(min_x * w), int(min_y * h)
        max_x, max_y = int(max_x * w), int(max_y * h)

        ru_corner = Point(max_x, max_y)
        lf_corner = Point(min_x, min_y)
        
        return Rectangle(ru_corner, lf_corner)
    
    @classmethod
    def index_coords(cls, frame, hand_landmarks) -> Point:
        h, w, _ = frame.shape

        index_tip = hand_landmarks[8]
        x, y = int(index_tip.x * w), int(index_tip.y * h)

        return Point(x, y)
