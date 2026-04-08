from enum import Enum

from mediapipe.tasks.python import vision


class RunningMode(Enum):
    VIDEO = vision.RunningMode.VIDEO
    IMG   = vision.RunningMode.IMAGE
    LIVE  = vision.RunningMode.LIVE_STREAM
