from pydantic import BaseModel


class QueueResponse(BaseModel):
    position: int
    allowed: bool
