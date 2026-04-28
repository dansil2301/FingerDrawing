import datetime

from Server.Domen.SessionExpired import SessionExpired
from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.DTO.SessionObject import SessionObject
from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.sessions: dict[str, SessionObject] = {}
    
    def create(self, id: str) -> SessionObject:
        session = SessionObject(
            session_id=id,
            created_at=datetime.datetime.now()
        )
        self.sessions[id] = session
        return session

    async def get(self, id: str) -> SessionObject:
        '''
        If session is over automatically delete object and send error to FE by websocket
        Aguable to keep the single sending logic here, 
        but it is more logical to keep it session handler, since this is where the session is managed
        Create API for this in WebSocketHandler and call it here?
        '''
        session = self.sessions.get(id, None)

        if session and session.created_at + datetime.timedelta(seconds=60) < datetime.datetime.now():
            self.remove(id)
            if session.web_socket:
                try:
                    await session.web_socket.send_json(SessionExpired().model_dump())
                    print("Successfully sent session expiry signle")
                except Exception as e:
                    print(f"Error: sending session expiry signle failed ({e})")
            raise SessionExpiredException("Session expired")

        return session
    
    def remove(self, id: str) -> None:
        if id in self.sessions:
            del self.sessions[id]
