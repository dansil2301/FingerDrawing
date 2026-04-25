import math
from typing import List

from Server.SessionHandler import SessionHandler


class CoordsSmoothing:
    def __init__(self, alpha: float = 0.5, jump_percent: float = 0.03):
        self.alpha = alpha
        self.jump_percent = jump_percent

        self.session_handler = SessionHandler()

    def _ema(self, prev: float, curr: float, alpha: float) -> float:
        return alpha * curr + (1 - alpha) * prev
    
    def _distance(self, prev, curr) -> float:
        return math.sqrt((curr.x - prev.x) ** 2 + (curr.y - prev.y) ** 2)

    def _adaptive_alpha(self, distance: float) -> float:
        if distance > self.jump_percent:
            return 1.0
        t = distance / self.jump_percent
        return self.alpha + (1.0 - self.alpha) * t

    def smooth(self, session_id: str, hand_landmarks: list) -> List:
        session = self.session_handler.get(session_id)

        if session.prev_coords is None:
            session.prev_coords = hand_landmarks.copy()
            return hand_landmarks

        smoothed = []

        for i, curr in enumerate(hand_landmarks):
            prev = session.prev_coords[i]
            dist = self._distance(prev, curr)
            alpha = self._adaptive_alpha(dist)

            curr.x = self._ema(prev.x, curr.x, alpha)
            curr.y = self._ema(prev.y, curr.y, alpha)
            smoothed.append(curr)
        session.prev_coords = smoothed.copy()
        return smoothed
