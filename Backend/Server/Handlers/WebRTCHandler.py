import asyncio
import os
from typing import Any

from aiortc.sdp import candidate_from_sdp
from aiortc import RTCConfiguration, RTCIceServer, RTCPeerConnection, RTCSessionDescription
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel

from Server.Domen.SessionExpired import SessionExpired
from Server.QueueOrchestration import QueueOrchestration
from Server.Exceptions.SessionExpiredException import SessionExpiredException
from Server.Handlers.SessionHandler import SessionHandler
from Server.Enums.RunningMode import RunningMode
from Server.Gestures.HandDetection import HandDetection
from Server.Domen.WebRTC.IceRequest import IceRequest
from Server.Domen.WebRTC.AnswerResponse import AnswerResponse
from Server.Domen.WebRTC.OfferRequest import OfferRequest
from Server.Utils.logging_config import logger


class WebRTCHandler:
    def __init__(self):
        load_dotenv()
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MODEL_PATH = os.path.join(BASE_DIR, "Gestures", "hand_landmarker.task")
        self.hand_detector = HandDetection(MODEL_PATH, RunningMode.VIDEO)

        self.session_handler = SessionHandler()
        self.queue_orchestration = QueueOrchestration()

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

        @pc.on("datachannel")
        async def on_datachannel(channel):
            logger.info(f"Data channel for session {session_id}: {channel.label}")
            session = self.session_handler.get(session_id)
            if session:
                session.data_channel = channel

        @pc.on("connectionstatechange")
        async def on_state():
            logger.info(f"Connection for session {session_id}: {pc.connectionState}")
            if pc.connectionState in ("failed", "closed", "disconnected"):
                await self._cleanup(session_id)

        @pc.on("icegatheringstatechange")
        def on_gathering():
            logger.info(f"ICE gathering for session {session_id}: {pc.iceGatheringState}")

        @pc.on("iceconnectionstatechange")  
        def on_ice():
            logger.info(f"ICE connection for session {session_id}: {pc.iceConnectionState}")

        return pc

    async def _process_video(self, session_id: str, track):
        while True:
            try:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")

                session = self.session_handler.get_raise(session_id)
                if session is None:
                    break

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.hand_detector.find_hand_coords,
                    session,
                    img
                )

                self._send_data(session_id, result.model_dump_json(), result)

            except SessionExpiredException as e:
                logger.warning(f"Session {session_id} expired")
                session = self.session_handler.get(session_id)
                self._send_data(session_id, session.data_channel, SessionExpired())
                await self.queue_orchestration.next(session_id)
                break

            except Exception as e:
                logger.error(f"Error in video processing: {e}")
                break

    async def get_description(self, offer: OfferRequest) -> AnswerResponse:
        if not self.queue_orchestration.accept_connection(offer.session_id):
            raise HTTPException(status_code=404, detail="Session not found in allowed connection list")

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
        session = self.session_handler.get(ice.session_id)
        
        if session is None or session.web_rtc is None:
            raise HTTPException(status_code=404, detail=f"No session: {ice.session_id}")

        candidate = candidate_from_sdp(ice.candidate)
        candidate.sdpMid = ice.sdpMid
        candidate.sdpMLineIndex = ice.sdpMLineIndex
        await session.web_rtc.addIceCandidate(candidate)

    def _send_data(self, session_id: str, data_channel: Any, data: BaseModel):
        if data_channel and data_channel == "open":
            try:
                data_channel.send(data.model_dump_json())
            except Exception as e:
                logger.error(f"Session {session_id} message sent failed ({e})")

    async def _cleanup(self, session_id: str):
        session = self.session_handler.get(session_id)

        if session is None:
            return
            
        self.session_handler.remove(session_id)
        logger.info(f"[{session_id}] cleaned up")
