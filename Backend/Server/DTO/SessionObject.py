from dataclasses import dataclass
from typing import Any, List

from aiortc import RTCPeerConnection
from fastapi import WebSocket


@dataclass
class SessionObject:
    session_id: str
    started_at_timestamp: int | None = None
    web_socket: WebSocket | None = None
    web_rtc: RTCPeerConnection | None = None
    data_channel: Any = None
    prev_coords: List | None = None
    detector: Any = None
    last_detected_timestamp: int = None
