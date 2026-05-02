from collections import deque

from fastapi import WebSocket

from Server.Constants import ALLOWED_ACTIVE_USERS
from Server.DTO.QueueObject import QueueObject
from Server.Utils.Singleton import SingletonMeta
from Server.Utils.logging_config import logger


class QueueHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.queue: deque[QueueObject] = deque()
    
    def create(self, id: str, websocket: WebSocket) -> QueueObject:
        existing = next((item for item in self.queue if item.session_id == id), None)
        if existing:
            existing.web_socket = websocket
            logger.info(f"Session {id} reconnected to existing queue position")
            return existing

        queue_item = QueueObject(
            session_id=id,
            web_socket=websocket
        )
        self.queue.append(queue_item)
        return queue_item

    def remove(self, session_id: str = None) -> QueueObject:
        for queue_item in list(self.queue):

            if queue_item.session_id == session_id:
                self.queue.remove(queue_item)
                return queue_item
            
        return None

    def get_allowed_and_not_active(self) -> list[QueueObject]:
        allowed_and_not_active = []
        for queue_item in list(self.queue)[:ALLOWED_ACTIVE_USERS + 1]:
            if not queue_item.active:
                allowed_and_not_active.append(queue_item)
        
        return allowed_and_not_active
