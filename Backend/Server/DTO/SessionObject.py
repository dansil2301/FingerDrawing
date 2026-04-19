from dataclasses import dataclass

from aiortc import RTCPeerConnection
from fastapi import WebSocket


@dataclass
class SessionObject:
    web_socket: WebSocket | None = None
    web_rtc: RTCPeerConnection | None = None
