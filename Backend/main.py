import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from Server.domen.WebRTC.AnswerResponse import AnswerResponse
from Server.SessionHandler import SessionHandler
from Server.domen.WebRTC.IceRequest import IceRequest
from Server.domen.WebRTC.OfferRequest import OfferRequest
from Server.WebRTC import WebRTC


web_rtc = WebRTC()
session_handler = SessionHandler()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/coordinates/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = session_handler.get(session_id)
    if session is None:
        await websocket.close()
        return

    session.web_socket = websocket

    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print("WS send failed:", e)
    finally:
        session_handler.remove(session_id)


@app.post("/stream-offer")
async def stream_offer(offer: OfferRequest) -> AnswerResponse:
    return await web_rtc.get_description(offer)


@app.post("/ice-candidate")
async def ice_candidate(ice: IceRequest) -> None:
    await web_rtc.get_ice(ice)
