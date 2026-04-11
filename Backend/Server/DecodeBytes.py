import cv2
import numpy as np


class DecodeBytes:
    @classmethod
    def decode(self, data: bytes):
        np_arr = np.frombuffer(data, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
