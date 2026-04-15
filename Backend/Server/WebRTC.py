from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription

from Backend.Server.domen.WebRTC import IceRequest
from Backend.Server.domen.WebRTC.AnswerResponse import AnswerResponse
from Backend.Server.domen.WebRTC.OfferRequest import OfferRequest


class WebRTC:
    def __init__(self):
        self.sessions: dict[str, RTCPeerConnection] = {}

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
                print(f"[{session_id}] model output: test")
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
        pc = self.sessions.get(ice.session_id)
        if pc is None:
            raise ValueError(f"No session: {ice.session_id}")

        await pc.addIceCandidate(RTCIceCandidate(
            candidate=ice.candidate,
            sdpMid=ice.sdp_mid,
            sdpMLineIndex=ice.sdp_m_line_index,
        ))

    async def _cleanup(self, session_id: str):
        pc = self.sessions.pop(session_id, None)
        if pc and pc.signalingState != "closed":
            await pc.close()
        print(f"[{session_id}] cleaned up")

    async def close_all(self):
        for session_id in list(self.sessions):
            await self._cleanup(session_id)
