import asyncio

from fastapi import WebSocket

from Server.Domen.QueueResponse import QueueResponse
from Server.Exceptions.WebSocketException import WebSocketException
from Server.Domen.SessionExpired import SessionExpired


class WebSocketHandler:
    async def connect(self, websocket: WebSocket, session_id: str, on_disconnect: function):
        try:
            await websocket.accept()
        except Exception as e:
            print(f"Error: {e}")
        
        await self._keep_socket_alive(session_id, on_disconnect)

    async def send_session_expired_signal(self, websocket: WebSocket):
        try:
            await websocket.send_json(SessionExpired().model_dump())
            print("Successfully sent session expiry signal")
        except Exception as e:
            print(f"Error: sending session expiry signal failed ({e})")

    async def send(self, websocket: WebSocket, response: QueueResponse):
        try:
            await websocket.send_json(response.model_dump())
            print("Successfully sent retry signal")
        except Exception as e:
            print(f"Error: sending retry signal failed ({e})")

    async def _keep_socket_alive(self, session_id: str, on_disconnect: function):
        try:
            while True:
                await asyncio.sleep(1)
        except Exception as e:
            print("WS send failed: ", e)
            raise WebSocketException("Web socket unexpected error")
        finally:
            on_disconnect(session_id)
