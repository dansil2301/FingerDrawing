from pydantic import BaseModel


class SessionExpired(BaseModel):
    error: str = 'session expired'
