import os

from fastapi import FastAPI, WebSocket

from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection
from Server.DecodeBytes import DecodeBytes


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

app = FastAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_bytes()
        # try:
        frame = DecodeBytes.decode(data)
        response = hand_detector.find_hand_coords(frame)
        # except Exception as e:
        #     print(e)
        #     continue

        print(f"Received frame: {len(data)} bytes")
        await websocket.send_json(response.model_dump())
