from dataclasses import dataclass

from fastapi import WebSocket


@dataclass
class QueueObject:
    session_id: str
    web_socket: WebSocket
    allowed: bool = False
    active: bool = False
    ttl_timestamp: int | None = None
    tries: int = 0
