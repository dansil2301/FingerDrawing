import time

from Server.Handlers.WebSocketHandler import WebSocketHandler
from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.DTO.SessionObject import SessionObject
from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.websocket_handler = WebSocketHandler()
        self.sessions: dict[str, SessionObject] = {}
    
    def create(self, id: str) -> SessionObject:
        session = SessionObject(
            session_id=id,
            started_at_timestamp=time.time() * 1000
        )
        self.sessions[id] = session
        return session

    async def get(self, id: str) -> SessionObject:
        session = self.sessions.get(id, None)

        if session and session.started_at_timestamp + 60 * 1000 < time.time() * 1000:
            self.remove(id)
            if session.web_socket:
                self.websocket_handler.send_session_expired_signal(session.web_socket)
            raise SessionExpiredException("Session expired")

        return session
    
    def remove(self, id: str) -> None:
        if id in self.sessions:
            del self.sessions[id]
