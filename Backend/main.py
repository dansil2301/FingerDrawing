import os

from fastapi import FastAPI, WebSocket

from Backend.Server.domen.WebRTC import IceRequest, OfferRequest
from Server.WebRTC import WebRTC
from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection
from Server.DecodeBytes import DecodeBytes


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

web_rtc = WebRTC()

app = FastAPI()


@app.websocket("/coordinates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        try:
            data = await websocket.receive_bytes()
            frame = DecodeBytes.decode(data)
            response = hand_detector.find_hand_coords(frame)
        except Exception as e:
            print(e)
            continue

        await websocket.send_json(response.model_dump())


@app.post("/stream-offer")
async def stream_offer(offer: OfferRequest):
    return await web_rtc.get_description(offer)


@app.post("/ice-candidate")
async def ice_candidate(ice: IceRequest):
    await web_rtc.get_ice(ice)
