import asyncio
import os

from aiortc.sdp import candidate_from_sdp
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from dotenv import load_dotenv
from fastapi.websockets import WebSocketState

from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.SessionHandler import SessionHandler
from Server.Enums.RunningMode import RunningMode
from Server.Gestures.HandDetection import HandDetection
from Server.Domen.WebRTC.IceRequest import IceRequest
from Server.Domen.WebRTC.AnswerResponse import AnswerResponse
from Server.Domen.WebRTC.OfferRequest import OfferRequest


class WebRTCHandler:
    def __init__(self):
        load_dotenv()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, "hand_landmarker.task")
        self.hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

        self.session_handler = SessionHandler()

    def _make_pc(self, session_id: str) -> RTCPeerConnection:
        pc = RTCPeerConnection(RTCConfiguration(
            iceServers=[
                RTCIceServer(urls="stun:stun.relay.metered.ca:80"),
                RTCIceServer(
                    urls=[
                        "turn:global.relay.metered.ca:80",
                        "turn:global.relay.metered.ca:80?transport=tcp",
                        "turn:global.relay.metered.ca:443",
                        "turns:global.relay.metered.ca:443?transport=tcp",
                    ],
                    username=os.getenv('TURN_USERNAME'),
                    credential=os.getenv('TURN_CREDENTIAL')
                ),
            ]
        ))

        @pc.on("track")
        async def on_track(track):
            if track.kind == "video":
                await self._process_video(session_id, track)

        @pc.on("connectionstatechange")
        async def on_state():
            print(f"[{session_id}] Connection: {pc.connectionState}")
            if pc.connectionState in ("failed", "closed", "disconnected"):
                await self._cleanup(session_id)

        @pc.on("icegatheringstatechange")
        def on_gathering():
            print(f"[{session_id}] ICE gathering: {pc.iceGatheringState}")

        @pc.on("iceconnectionstatechange")  
        def on_ice():
            print(f"[{session_id}] ICE connection: {pc.iceConnectionState}")

        return pc

    async def _process_video(self, session_id: str, track):
        while True:
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")

                session = await self.session_handler.get(session_id)
                if session is None:
                    break

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.hand_detector.find_hand_coords,
                    session,
                    img
                )

                ws = session.web_socket
                if ws and ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(result.model_dump())

            except ValueError as e:
                if "monotonically" in str(e):
                    print(f"Skipping frame: {e}")
                    continue
                raise
            
            except Exception as e:
                print(f"Error type: {type(e).__name__}, message: {e}")
                print(f"Error in video processing: {e}")
                self.session_handler.remove(session_id)
                break

    async def get_description(self, offer: OfferRequest) -> AnswerResponse:
        session = self.session_handler.create(offer.session_id)
        session.detector = self.hand_detector.create_detector()
        pc = self._make_pc(offer.session_id)
        session.web_rtc = pc

        await pc.setRemoteDescription(RTCSessionDescription(sdp=offer.sdp, type=offer.type))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        
        return AnswerResponse(
            sdp=pc.localDescription.sdp,
            type=pc.localDescription.type
        )

    async def get_ice(self, ice: IceRequest) -> None:
        try:
            session = await self.session_handler.get(ice.session_id)
        except SessionExpiredException:
            raise ValueError(f"Session expired: {ice.session_id}")
        
        if session is None or session.web_rtc is None:
            raise ValueError(f"No session: {ice.session_id}")

        candidate = candidate_from_sdp(ice.candidate)
        candidate.sdpMid = ice.sdpMid
        candidate.sdpMLineIndex = ice.sdpMLineIndex
        await session.web_rtc.addIceCandidate(candidate)

    async def _cleanup(self, session_id: str):
        try:
            session = await self.session_handler.get(session_id)
        except SessionExpiredException:
            return

        if session is None:
            return
            
        self.session_handler.remove(session_id)
        print(f"[{session_id}] cleaned up")
