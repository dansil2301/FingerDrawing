from typing import List

from Server.DTO.Point import Point
from Server.DTO.Rectangle import Rectangle


class GesturesCoords:
    @classmethod
    def finger_tips(cls, hand_landmarks: list) -> List[Point]:
        tip_indices = [4, 8, 12, 16, 20]

        coordinates = [
            Point(x=hand_landmarks[i].x, y=hand_landmarks[i].y)
            for i in tip_indices
        ]

        return coordinates

    @classmethod
    def rectangle_coords(cls, hand_landmarks: list) -> Rectangle:
        all_x = [point.x for point in hand_landmarks]
        all_y = [point.y for point in hand_landmarks]

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        min_x, min_y = min_x, min_y
        max_x, max_y = max_x, max_y

        ru_corner = Point(x=max_x, y=max_y)
        ld_corner = Point(x=min_x, y=min_y)
        
        return Rectangle(ru_corner=ru_corner, ld_corner=ld_corner)
    
    @classmethod
    def index_coords(cls, hand_landmarks) -> Point:
        index_tip = hand_landmarks[8]
        x, y = index_tip.x, index_tip.y

        return Point(x=x, y=y)
