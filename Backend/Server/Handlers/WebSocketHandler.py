import asyncio
from typing import Awaitable, Callable

from fastapi import WebSocket, WebSocketDisconnect

from Server.Domen.QueueResponse import QueueResponse
from Server.Domen.SessionExpired import SessionExpired
from Server.Utils.logging_config import logger


class WebSocketHandler:
    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
        except Exception as e:
            logger.error(f"{e}")

    async def keep_socket_alive(self, websocket: WebSocket, session_id: str, on_disconnect):
        try:
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect as e:
            logger.error(f"WS disconnected: {session_id} ({e})")
        except Exception as e:
            logger.error(f"WS error: {e}")
        finally:
            logger.warning(f"WS closed and the fallback is executed (delete queue)")
            await on_disconnect(session_id)

    async def send_session_expired_signal(self, websocket: WebSocket):
        try:
            await websocket.send_json(SessionExpired().model_dump())
            logger.info("Successfully sent session expiry signal")
        except Exception as e:
            logger.error(f"sending session expiry signal failed ({e})")

    async def send(self, websocket: WebSocket, response: QueueResponse):
        try:
            await websocket.send_json(response.model_dump())
            logger.info("Successfully sent retry signal")
        except Exception as e:
            logger.info(f"Error: sending retry signal failed ({e})")
