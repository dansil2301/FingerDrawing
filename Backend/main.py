from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from Server.Handlers.WebSocketHandler import WebSocketHandler
from Server.Domen.WebRTC.AnswerResponse import AnswerResponse
from Server.Handlers.SessionHandler import SessionHandler
from Server.Domen.WebRTC.IceRequest import IceRequest
from Server.Domen.WebRTC.OfferRequest import OfferRequest
from Backend.Server.Handlers.WebRTCHandler import WebRTCHandler


web_rtc_handler = WebRTCHandler()
web_socket_handler = WebSocketHandler()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/api/orchestration/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await web_socket_handler.connect(websocket, session_id)


@app.post("/api/stream-offer")
async def stream_offer(offer: OfferRequest) -> AnswerResponse:
    return await web_rtc_handler.get_description(offer)


@app.post("/api/ice-candidate")
async def ice_candidate(ice: IceRequest) -> None:
    await web_rtc_handler.get_ice(ice)
