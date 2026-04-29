from dataclasses import dataclass


@dataclass
class QueueObject:
    session_id: str
    position: int
    active: bool = True
    allowed: bool = False
    ttl_timestamp: int | None = None
