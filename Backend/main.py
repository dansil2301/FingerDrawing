import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from Server.SessionHandler import SessionHandler
from Server.domen.WebRTC.IceRequest import IceRequest
from Server.domen.WebRTC.OfferRequest import OfferRequest
from Server.WebRTC import WebRTC


web_rtc = WebRTC()
websocket_handler = SessionHandler()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/coordinates/{socket_id}")
async def websocket_endpoint(websocket: WebSocket, socket_id: str):
    await websocket.accept()
    websocket_handler.add_socket(socket_id, websocket)

    try:
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        pass
    finally:
        print("WS send failed:", e)
        websocket_handler.remove_socket(socket_id)


@app.post("/stream-offer")
async def stream_offer(offer: OfferRequest):
    return await web_rtc.get_description(offer)


@app.post("/ice-candidate")
async def ice_candidate(ice: IceRequest):
    await web_rtc.get_ice(ice)
