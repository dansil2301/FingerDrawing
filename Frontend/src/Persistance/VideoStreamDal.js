class VideoStreamDal {
    constructor () {
        const protocol =
        process.env.REACT_APP_ENV === "d" ? "http" : "https";

        const baseUrl =
        process.env.REACT_APP_BE_URL || "localhost:8000";

        this.httpUrl = `${protocol}://${baseUrl}`;

        this.iceCandidateQueue = [];
        this.remoteDescSet = false;

        this.rtc = new RTCPeerConnection({
            iceServers: [
                { urls: "stun:stun.l.google.com:19302" }
            ]
        });

        this.rtc.onconnectionstatechange = () => {
            console.log("Connection:", this.rtc.connectionState);
        };

        this.rtc.onicecandidate = this.setIce.bind(this);
    }

    setIce (event) {
        if (!event.candidate) return;
        if (this.remoteDescSet) {
            this.sendIce(event);
        } else {
            this.iceCandidateQueue.push(event.candidate);
        }
    }

    async connect (stream) {
        try{
            stream.getTracks().forEach((track) => {
                this.rtc.addTrack(track, stream);
            });

            const offer = await this.rtc.createOffer();

            await this.rtc.setLocalDescription(offer);

            const answer = await this.sendOffer();

            await this.rtc.setRemoteDescription(answer);

            this.remoteDescSet = true;
            for (const candidate of this.iceCandidateQueue) {
                await this.sendIce({ candidate });
            }
            this.iceCandidateQueue = [];
        }
        catch (err) {
            console.error("WebRTC connect failed:", err);
            this.close();
            throw err;
        }
    }

    async sendOffer () {
        const response = await fetch(`${this.httpUrl}/stream-offer`, {
            method: "POST",
            body: JSON.stringify({
                sdp:  this.rtc.localDescription.sdp,
                type: this.rtc.localDescription.type,
            }),
            headers: { "Content-Type": "application/json" },
        });

        if (!response.ok) {
            throw new Error(`Offer rejected: ${response.status}`);
        }

        return response.json();
    }

    async sendIce(event) {
        if (!event.candidate) return;

        try {
            await fetch(`${this.httpUrl}/ice-candidate`, {
                method: "POST",
                body: JSON.stringify(event.candidate),
                headers: { "Content-Type": "application/json" }
            });
        } catch (err) {
            console.error("ICE send failed:", err);
        }
    }

    close() {
        if (this.rtc.signalingState === "closed") return;
        this.rtc.getSenders().forEach(sender => sender.track?.stop());
        this.rtc.close();
    }
}

export default VideoStreamDal
