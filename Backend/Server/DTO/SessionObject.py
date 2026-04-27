from dataclasses import dataclass
from datetime import datetime
from typing import Any, List

from aiortc import RTCPeerConnection
from fastapi import WebSocket


@dataclass
class SessionObject:
    session_id: str
    created_at: datetime
    web_socket: WebSocket | None = None
    web_rtc: RTCPeerConnection | None = None
    prev_coords: List | None = None
    detector: Any = None
    last_detected_timestamp: int = None
