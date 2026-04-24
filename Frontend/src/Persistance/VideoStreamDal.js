import SessionStore from './SessionStore';


class VideoStreamDal {
    constructor() {
        const protocol = process.env.REACT_APP_ENV === "d" ? "http" : "https";
        const baseUrl = process.env.REACT_APP_BE_URL || "localhost:8000";
        this.httpUrl = `${protocol}://${baseUrl}`;
        this.rtc = null;
    }

    _createPc(onStateChange) {
        this.iceCandidateQueue = [];
        this.remoteDescSet = false;

        const isDev = process.env.REACT_APP_ENV === "d";

        const iceServers = isDev
            ? [{ urls: "stun:stun.l.google.com:19302" }]
            : [
                {
                    urls: [
                        "turn:openrelay.metered.ca:80",
                        "turn:openrelay.metered.ca:443",
                        "turn:openrelay.metered.ca:443?transport=tcp"
                    ],
                    username: "openrelayproject",
                    credential: "openrelayproject"
                }
            ];

        this.rtc = new RTCPeerConnection({
            iceServers,
            ...(isDev ? {} : { iceTransportPolicy: "relay" })
        });

        this.rtc.onconnectionstatechange = () => {
            const state = this.rtc.connectionState;
            console.log("[RTC] Connection:", this.rtc.connectionState);
            onStateChange?.(state);
        };

        this.rtc.onicecandidate = this._setIce.bind(this);
    }

    _setIce(event) {
        if (!event.candidate) return;
        if (this.remoteDescSet) {
            this._sendIce(event);
        } else {
            this.iceCandidateQueue.push(event.candidate);
        }
    }

    async connect(stream, onStateChange) {
        this._createPc(onStateChange);

        try {
            stream.getTracks().forEach(track => this.rtc.addTrack(track, stream));

            const offer = await this.rtc.createOffer();
            await this.rtc.setLocalDescription(offer);

            const answer = await this._sendOffer();
            await this.rtc.setRemoteDescription(answer);

            this.remoteDescSet = true;
            for (const candidate of this.iceCandidateQueue) {
                await this._sendIce({ candidate });
            }
            this.iceCandidateQueue = [];
        } catch (err) {
            console.error("[RTC] WebRTC connect failed:", err);
            this.close();
            throw err;
        }
    }

    async _sendOffer() {
        const response = await fetch(`${this.httpUrl}/stream-offer`, {
            method: "POST",
            body: JSON.stringify({
                sdp: this.rtc.localDescription.sdp,
                type: this.rtc.localDescription.type,
                session_id: SessionStore.get(),
            }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) throw new Error(`Offer rejected: ${response.status}`);
        return response.json();
    }

    async _sendIce(event) {
        if (!event.candidate) return;

        await fetch(`${this.httpUrl}/ice-candidate`, {
            method: "POST",
            body: JSON.stringify({
                candidate: event.candidate.candidate,
                sdpMid: event.candidate.sdpMid,
                sdpMLineIndex: event.candidate.sdpMLineIndex,
                session_id: SessionStore.get(),
            }),
            headers: { "Content-Type": "application/json" },
        });
    }

    close() {
        if (!this.rtc || this.rtc.signalingState === "closed") return;
        this.rtc.getSenders().forEach(sender => sender.track?.stop());
        this.rtc.close();
        SessionStore.clear();
        console.log(`[RTC] Connection closed`);
    }
}

export default VideoStreamDal;
