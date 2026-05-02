import time

from Server.Constants import SESSION_LIFE_SECONDS
from Server.Handlers.WebSocketHandler import WebSocketHandler
from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.DTO.SessionObject import SessionObject
from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.sessions: dict[str, SessionObject] = {}
    
    def create(self, id: str) -> SessionObject:
        session = SessionObject(
            session_id=id,
            started_at_timestamp=time.time() * 1000,
        )
        self.sessions[id] = session
        return session
    
    def get_raise(self, id: str) -> SessionObject:
        session = self.sessions.get(id, None)

        if session and session.started_at_timestamp + SESSION_LIFE_SECONDS * 1000 < time.time() * 1000:
            raise SessionExpiredException("Session expired")

        return session

    def get(self, id: str) -> SessionObject:
        return self.sessions.get(id, None)
    
    def remove(self, id: str) -> None:
        if id in self.sessions:
            del self.sessions[id]
