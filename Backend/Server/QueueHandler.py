from Server.Exceptions import QueueException
from Server.DTO.QueueObject import QueueObject
from Server.Utils.Singleton import SingletonMeta


class SessionHandler(metaclass=SingletonMeta):
    def __init__(self):
        self.queue: list[QueueObject] = []
        self.allowed_connected = 1
    
    def create(self, id: str) -> QueueObject:
        queue_item = QueueObject(
            session_id=id,
        )
        self.queue.append(queue_item)
        return queue_item

    def get_by_id(self, id: str) -> QueueObject:
        # ToDo: fix queue (inverted logic now)
        first_n_queue = self.queue[len(self.queue) - self.allowed_connected:]
        
        for queue_item in first_n_queue:
            if queue_item.session_id == id and queue_item.allowed and queue_item.active:
                return queue_item

        raise QueueException(f"Error: session with id {id} is not queued or not yet allowed to connect")
    
    def allow_connection_first_in_queue(self): 
        for i in range(len(self.queue) - 1, -1, -1):
            queue_item = self.queue[i]
            if queue_item.active:
                queue_item.allowed = True
    