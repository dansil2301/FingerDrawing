import asyncio

from fastapi import WebSocket

from Server.Domen.SessionExpired import SessionExpired
from Server.SessionHandler import SessionHandler


class WebSocketHandler:
    def __init__(self):
        pass
        #self.session_handler = SessionHandler()

    async def connect(self, websocket: WebSocket, session_id: str):
        try:
            await websocket.accept()
        
            #session = self.session_handler.create(session_id)

            #session.web_socket = websocket
        except Exception as e:
            print(f"Error: {e}")
        
        await self._keep_socket_alive(session_id)

    async def send_session_expired_signal(self, websocket: WebSocket):
        try:
            await websocket.send_json(SessionExpired().model_dump())
            print("Successfully sent session expiry signal")
        except Exception as e:
            print(f"Error: sending session expiry signal failed ({e})")

    async def _keep_socket_alive(self, session_id: str):
        try:
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print("WS send failed:", e)
        finally:
            pass
            #self.session_handler.remove(session_id)
