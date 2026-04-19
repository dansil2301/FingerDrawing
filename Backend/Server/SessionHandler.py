import uuid

from aiortc import RTCPeerConnection
from fastapi import WebSocket

from Server.DTO.SessionObject import SessionObject
from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.sessions: dict[str, SessionObject] = {}
    
    def create(self, id: str) -> SessionObject:
        session = SessionObject()
        self.sessions[id] = session
        return session

    def get(self, id: str) -> SessionObject:
        return self.sessions.get(id, None)
    
    def remove(self, id: str) -> None:
        if id in self.sessions:
            del self.sessions[id]
