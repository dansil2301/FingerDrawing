from collections import deque

from fastapi import WebSocket

from Server.Constants import ALLOWED_ACTIVE_USERS
from Server.DTO.QueueObject import QueueObject
from Server.Utils.Singleton import SingletonMeta

class QueueHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.queue: deque[QueueObject] = []
    
    def create(self, id: str, websocket: WebSocket) -> QueueObject:
        queue_item = QueueObject(
            session_id=id,
            web_socket=websocket
        )
        self.queue.append(queue_item)
        return queue_item

    def remove(self, session_id: str = None) -> QueueObject:
        for queue_item in self.queue:

            if queue_item.session_id == session_id:
                self.queue.remove(queue_item)
                return queue_item
            
        return None

    def get_taken_positions(self) -> list[QueueObject]:
        taken = []
        for queue_item in self.queue[:ALLOWED_ACTIVE_USERS]:
            taken.append(queue_item)
        
        return taken
