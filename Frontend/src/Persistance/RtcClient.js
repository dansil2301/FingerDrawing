import SignalingApi from '../Persistance/SignalingApi';


class RtcClient {
    constructor() {
        this.api = new SignalingApi();

        this.pc = null;
        this.iceQueue = [];
        this.remoteDescSet = false;
        this.sessionId = null;
    }

    _getIceServers() {
        const isDev = process.env.REACT_APP_ENV === "d";

        if (isDev) {
            return [{ urls: "stun:stun.l.google.com:19302" }];
        }

        return [
            { urls: "stun:stun.relay.metered.ca:80" },
            {
                urls: "turn:global.relay.metered.ca:80",
                username: process.env.REACT_APP_TURN_USERNAME,
                credential: process.env.REACT_APP_TURN_CREDENTIAL,
            },
            {
                urls: "turn:global.relay.metered.ca:80?transport=tcp",
                username: process.env.REACT_APP_TURN_USERNAME,
                credential: process.env.REACT_APP_TURN_CREDENTIAL,
            },
            {
                urls: "turn:global.relay.metered.ca:443",
                username: process.env.REACT_APP_TURN_USERNAME,
                credential: process.env.REACT_APP_TURN_CREDENTIAL,
            },
            {
                urls: "turns:global.relay.metered.ca:443?transport=tcp",
                username: process.env.REACT_APP_TURN_USERNAME,
                credential: process.env.REACT_APP_TURN_CREDENTIAL,
            },
        ];
    }

    _createPeerConnection(onStateChange, onData, onSessionExpired) {
        this.pc = new RTCPeerConnection({
            iceServers: this._getIceServers()
        });

        this.dataChannel = this.pc.createDataChannel("coordinates");
        this.dataChannel.onopen = () => console.log("[RTC] data channel open");
        this.dataChannel.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                
                console.log()
                if (data?.error === "session expired") {
                    onSessionExpired?.();
                    return;
                }

                onData?.(data);
            } catch (err) {
                console.error("[RTC] invalid data", e.data);
            }
        };

        this.pc.onconnectionstatechange = () => {
            const state = this.pc.connectionState;
            console.log("[RTC] state:", state);
            onStateChange?.(state);
        };

        this.pc.onicecandidate = (event) => this._handleIce(event);
    }

    _handleIce(event) {
        if (!event.candidate) return;

        if (this.remoteDescSet) {
            this.api.sendIce(event.candidate, this.sessionId);
        } else {
            this.iceQueue.push(event.candidate);
        }
    }

    async _flushIceQueue() {
        for (const candidate of this.iceQueue) {
            await this.api.sendIce(candidate, this.sessionId);
        }
        this.iceQueue = [];
    }

    async start(stream, sessionId, onStateChange, onData, onSessionExpired) {
        this.sessionId = sessionId;

        this._createPeerConnection(onStateChange, onData, onSessionExpired);

        try {
            stream.getTracks().forEach(track => this.pc.addTrack(track, stream));

            const offer = await this.pc.createOffer();
            await this.pc.setLocalDescription(offer);
            console.log("[RTC] offer created");

            const answer = await this.api.sendOffer(
                this.pc.localDescription,
                sessionId
            );

            await this.pc.setRemoteDescription(answer);
            console.log("[RTC] answer received");

            this.remoteDescSet = true;
            await this._flushIceQueue();

        } catch (err) {
            console.error("[RTC] start failed:", err);
            this.close();
            throw err;
        }
    }

    close() {
        if (!this.pc || this.pc.signalingState === "closed") return;

        this.dataChannel?.close();
        this.pc.getSenders().forEach(s => s.track?.stop());
        this.pc.close();

        this.pc = null;
        this.dataChannel = null;
        this.iceQueue = [];
        this.remoteDescSet = false;

        console.log("[RTC] closed");
    }
}

export default RtcClient;
