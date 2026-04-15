from pydantic import BaseModel


class IceRequest(BaseModel):
    session_id: str
    candidate: str
    sdp_mid: str
    sdp_m_line_index: int
