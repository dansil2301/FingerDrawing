import os

from aiortc.sdp import candidate_from_sdp
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi import WebSocket

from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection
from Server.domen.WebRTC.IceRequest import IceRequest
from Server.domen.WebRTC.AnswerResponse import AnswerResponse
from Server.domen.WebRTC.OfferRequest import OfferRequest


class WebRTC:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
        self.hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

        self.sessions: dict[str, RTCPeerConnection] = {}

        self.websockets: list[WebSocket] = []

    def _make_pc(self, session_id: str) -> RTCPeerConnection:
        pc = RTCPeerConnection()

        @pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                await self._process_video(session_id, track)

        @pc.on("connectionstatechange")
        async def on_state():
            print(f"[{session_id}] Connection: {pc.connectionState}")
            if pc.connectionState in ("failed", "closed", "disconnected"):
                await self._cleanup(session_id)

        return pc

    async def _process_video(self, session_id: str, track):
        while True:
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
            
                result = self.hand_detector.find_hand_coords(img)

                for ws in self.websockets[:]:
                    try:
                        #print(result)
                        await ws.send_json(result.model_dump())
                    except Exception as e:
                        print(f"Error sending data: {e}")
                        continue
                        #self.websockets.remove(ws)
            except Exception:
                break

    async def get_description(self, offer: OfferRequest) -> AnswerResponse:
        pc = self._make_pc(offer.session_id)
        self.sessions[offer.session_id] = pc

        await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return AnswerResponse(
            sdp=pc.localDescription.sdp,
            type=pc.localDescription.type
        )

    async def get_ice(self, ice: IceRequest) -> None:
        rtc = self.sessions.get(ice.session_id)
        if rtc is None:
            raise ValueError(f"No session: {ice.session_id}")

        candidate = candidate_from_sdp(ice.candidate)

        candidate.sdpMid = ice.sdpMid
        candidate.sdpMLineIndex = ice.sdpMLineIndex

        await rtc.addIceCandidate(candidate)

    async def _cleanup(self, session_id: str):
        pc = self.sessions.pop(session_id, None)
        if pc and pc.signalingState != "closed":
            await pc.close()
        print(f"[{session_id}] cleaned up")

    async def close_all(self):
        for session_id in list(self.sessions):
            await self._cleanup(session_id)
