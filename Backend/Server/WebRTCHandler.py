import asyncio
import os

from aiortc.sdp import candidate_from_sdp
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from dotenv import load_dotenv

from Server.SessionHandler import SessionHandler
from Server.Enums.RunningMode import RunningMode
from Server.HandDetection import HandDetection
from Server.domen.WebRTC.IceRequest import IceRequest
from Server.domen.WebRTC.AnswerResponse import AnswerResponse
from Server.domen.WebRTC.OfferRequest import OfferRequest


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
            
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.hand_detector.find_hand_coords,
                    session_id,
                    img
                )

                session = self.session_handler.get(session_id)
                if session:
                    try:
                        await session.web_socket.send_json(result.model_dump())
                    except Exception as e:
                        print(f"Error sending data on websocket {session_id}: {e}")
            except Exception:
                break

    async def get_description(self, offer: OfferRequest) -> AnswerResponse:
        session = self.session_handler.create(offer.session_id)
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
        print(f"Ice candidate for session {ice.session_id} - {ice.candidate}")
        session = self.session_handler.get(ice.session_id)
        pc = session.web_rtc
        if pc is None:
            raise ValueError(f"No session: {ice.session_id}")

        candidate = candidate_from_sdp(ice.candidate)

        candidate.sdpMid = ice.sdpMid
        candidate.sdpMLineIndex = ice.sdpMLineIndex

        await pc.addIceCandidate(candidate)

    async def _cleanup(self, session_id: str):
        session = self.session_handler.get(session_id)
        if session is None:
            return
            
        pc = session.web_rtc
        if pc and pc.signalingState != "closed":
            await pc.close()
        self.session_handler.remove(session_id)
        print(f"[{session_id}] cleaned up")
