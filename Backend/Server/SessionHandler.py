import uuid

from aiortc import RTCPeerConnection
from fastapi import WebSocket

from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.websockets: dict[str, WebSocket] = {}
        self.webrtcs: dict[str, RTCPeerConnection] = {}
        
    def generate_connection_id(self) -> str:
        return uuid.uuid4()

    def add_socket(self, id: str, websocket: WebSocket) -> None:
        self.websockets[id] = websocket

    def add_rtc(self, id: str, rtc: RTCPeerConnection) -> None:
        self.webrtcs[id] = rtc

    def get_socket(self, id: str) -> WebSocket:
        return self.websockets.get(id, None)
    
    def get_rtc(self, id: str) -> RTCPeerConnection:
        return self.webrtcs.get(id, None)
    
    def remove_socket(self, id: str) -> None:
        if id in self.websockets:
            del self.websockets[id]

    def remove_socket(self, id: str) -> None:
        if id in self.webrtcs:
            del self.webrtcs[id]
