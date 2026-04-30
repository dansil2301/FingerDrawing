from fastapi import APIRouter, WebSocket

from Server.Handlers.WebRTCHandler import WebRTCHandler
from Server.QueueOrchestration import QueueOrchestration
from Server.Domen.WebRTC.AnswerResponse import AnswerResponse
from Server.Domen.WebRTC.IceRequest import IceRequest
from Server.Domen.WebRTC.OfferRequest import OfferRequest

router = APIRouter()

def get_router(orchestrator: QueueOrchestration, web_rtc_handler: WebRTCHandler):
    @router.websocket("/api/orchestration/{session_id}")
    async def websocket_endpoint(websocket: WebSocket, session_id: str):
        await orchestrator.conenct(websocket, session_id)

    @router.post("/api/stream-offer")
    async def stream_offer(offer: OfferRequest) -> AnswerResponse:
        return await web_rtc_handler.get_description(offer)

    @router.post("/api/ice-candidate")
    async def ice_candidate(ice: IceRequest) -> None:
        await web_rtc_handler.get_ice(ice)

    return router