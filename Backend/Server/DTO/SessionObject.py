from dataclasses import dataclass
from datetime import datetime
from typing import List

from aiortc import RTCPeerConnection
from fastapi import WebSocket


@dataclass
class SessionObject:
    session_id: str
    created_at: datetime
    web_socket: WebSocket | None = None
    web_rtc: RTCPeerConnection | None = None
    prev_coords: List | None = None
    detector: any = None
