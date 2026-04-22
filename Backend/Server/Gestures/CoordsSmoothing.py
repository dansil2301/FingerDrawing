from typing import List

from Server.SessionHandler import SessionHandler


class CoordsSmoothing:
    def __init__(self, alpha: float = 0.2, jump_percent: float = 0.005):
        self.alpha = alpha
        self.jump_percent = jump_percent

        self.session_handler = SessionHandler()

    def _ema(self, prev_point: float, curr_point: float) -> float:
        return self.alpha * curr_point + (1 - self.alpha) * prev_point
    
    def _is_big_jump(self, prev_point, curr_point) -> bool:
        return (curr_point.x - prev_point.x) ** 2 + (curr_point.y - prev_point.y) ** 2 > self.jump_percent ** 2

    def smooth(self, session_id: str, hand_landmarks: list) -> List:
        session = self.session_handler.get(session_id)

        if session.prev_coords is None:
            session.prev_coords = hand_landmarks.copy()
            return hand_landmarks

        smoothed = []

        for i, curr in enumerate(hand_landmarks):
            prev = session.prev_coords[i]

            if self._is_big_jump(prev, curr):
                smoothed.append(curr)
            else:
                curr.x = self._ema(prev.x, curr.x)
                curr.y = self._ema(prev.y, curr.y)
                smoothed.append(curr)

        session.prev_coords = [p for p in smoothed]

        return smoothed
