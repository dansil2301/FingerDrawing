import asyncio

from fastapi import WebSocket

from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.SessionHandler import SessionHandler


class WebSocketHandler:
    def __init__(self):
        self.session_handler = SessionHandler()

    async def connect(self, websocket: WebSocket, session_id: str):
        try:    
            await websocket.accept()
        
        
            session = await self.session_handler.get(session_id)
        
            if session is None:
                await websocket.close()
                return

            session.web_socket = websocket
        except Exception as e:
            print(f"Error: {e}")
        
        await self._keep_socket_alive(session_id)

    async def _keep_socket_alive(self, session_id: str):
        try:
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print("WS send failed:", e)
        finally:
            self.session_handler.remove(session_id)
    