from pydantic import BaseModel


class AnswerResponse(BaseModel):
    sdp: str
    type: str
    session_id: str
