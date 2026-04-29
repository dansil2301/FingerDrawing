import time

from fastapi import WebSocket

from Server.Domen.QueueResponse import QueueResponse
from Server.Constants import ALLOWED_ACTIVE_USERS
from Server.Handlers.QueueHandler import QueueHandler
from Server.Handlers.WebSocketHandler import WebSocketHandler


class QueueOrchestration:
    def __init__(self):
        self.websocket_handler = WebSocketHandler()
        self.queue_handler = QueueHandler()

    async def conenct(self, websocket: WebSocket, session_id: str):
        self.websocket_handler.connect(websocket, session_id, self.next)
        self.queue_handler.create()

        await self._broadcast_positions(self.queue_handler.queue)

    async def next(self, gone_session_id: str):
        self.queue_handler.remove(gone_session_id)
        await self._broadcast_positions(self.queue_handler.queue)

    async def _broadcast_positions(self):
        for idx, queue_object in enumerate(self.queue_handler.queue):
            if queue_object.web_socket is None:
                continue

            if idx in range(ALLOWED_ACTIVE_USERS) and not queue_object.allowed:
                queue_object.tries = 1
                queue_object.ttl_timestamp = int(time.time() * 1000)
                queue_object.allowed = True

            await self.websocket_handler.send(queue_object.web_socket, 
                                              QueueResponse(position=idx - ALLOWED_ACTIVE_USERS, 
                                                            allowed=queue_object.allowed)) 
