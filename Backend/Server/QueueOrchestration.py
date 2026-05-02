import asyncio
import time

from fastapi import WebSocket

from Server.DTO.QueueObject import QueueObject
from Server.Domen.QueueResponse import QueueResponse
from Server.Constants import ALLOWED_ACTIVE_USERS, MAX_TTL_TRIES, TLL_WAIT_TIME_SECONDS
from Server.Handlers.QueueHandler import QueueHandler
from Server.Handlers.WebSocketHandler import WebSocketHandler
from Server.Utils.logging_config import logger


class QueueOrchestration:
    def __init__(self):
        self.websocket_handler = WebSocketHandler()
        self.queue_handler = QueueHandler()

    async def watch_ttl(self):
        while True:
            await asyncio.sleep(1)
            waiting_for_approval = self.queue_handler.get_allowed_and_not_active()
            now = int(time.time())

            changed = False

            for queue_item in waiting_for_approval:
                if now - queue_item.ttl_timestamp > TLL_WAIT_TIME_SECONDS:
                    
                    if queue_item.tries < MAX_TTL_TRIES:
                        queue_item.tries += 1
                        queue_item.ttl_timestamp = now

                        await self.websocket_handler.send(queue_item.web_socket, 
                                                            QueueResponse(position=-1, 
                                                                        allowed=True))
                    else:
                        await self.next(queue_item.session_id)
                        changed = True

            if changed:
                await self._rebalance_broadcast_positions()


    async def conenct(self, websocket: WebSocket, session_id: str):
        logger.info(f"New client with session id {session_id} connected")
        await self.websocket_handler.connect(websocket)
        self.queue_handler.create(session_id, websocket)

        await self._rebalance_broadcast_positions()
        logger.info(f"New client with session id {session_id} was put in the queue")
        await self.websocket_handler.keep_socket_alive(websocket, session_id, self.next)

    async def next(self, gone_session_id: str):
        logger.info(f"Remove cient with session id {gone_session_id} from the queue")
        logger.info(self.queue_handler.queue)
        self.queue_handler.remove(gone_session_id)
        await self._rebalance_broadcast_positions()

    def accept_connection(self, session_id) -> bool:
        waiting_for_approval = self.queue_handler.get_allowed_and_not_active()
        for queue_item in waiting_for_approval:
            if queue_item.session_id == session_id:
                queue_item.active = True
                return True
        return False

    async def _rebalance_broadcast_positions(self):
        logger.info(f"Rebalancing was triggered")
        for idx, queue_object in enumerate(self.queue_handler.queue):
            if queue_object.web_socket is None or queue_object.active:
                continue

            if idx in range(ALLOWED_ACTIVE_USERS) and not queue_object.allowed:
                logger.info(f"Client with session {queue_object.session_id} was allowed to connect")
                queue_object.tries = 1
                queue_object.ttl_timestamp = int(time.time())
                queue_object.allowed = True

            await self.websocket_handler.send(queue_object.web_socket, 
                                              QueueResponse(position=idx - ALLOWED_ACTIVE_USERS + 1, 
                                                            allowed=queue_object.allowed))
