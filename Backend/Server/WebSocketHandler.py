import asyncio

from fastapi import WebSocket

from Server.SessionHandler import SessionHandler


class WebSocketHandler:
    def __init__(self):
        self.session_handler = SessionHandler()

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        session = self.session_handler.get(session_id)
        if session is None:
            await websocket.close()
            return

        session.web_socket = websocket

        try:
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print("WS send failed:", e)
        finally:
            print("here")
            self.session_handler.remove(session_id)
    