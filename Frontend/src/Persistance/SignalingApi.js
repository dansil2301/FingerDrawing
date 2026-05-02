class SignalingApi {
    constructor() {
        const protocol = process.env.REACT_APP_ENV === "d" ? "http" : "https";
        const baseUrl = process.env.REACT_APP_BE_URL || "localhost:8000";
        this.baseUrl = `${protocol}://${baseUrl}/api`;
    }

    async sendOffer(desc, sessionId) {
        const res = await fetch(`${this.baseUrl}/stream-offer`, {
            method: "POST",
            body: JSON.stringify({
                sdp: desc.sdp,
                type: desc.type,
                session_id: sessionId
            }),
            headers: { "Content-Type": "application/json" }
        });

        if (!res.ok) {
            throw new Error(`Offer failed: ${res.status}`);
        }

        return res.json();
    }

    async sendIce(candidate, sessionId) {
        await fetch(`${this.baseUrl}/ice-candidate`, {
            method: "POST",
            body: JSON.stringify({
                candidate: candidate.candidate,
                sdpMid: candidate.sdpMid,
                sdpMLineIndex: candidate.sdpMLineIndex,
                session_id: sessionId
            }),
            headers: { "Content-Type": "application/json" }
        });
    }
}

export default SignalingApi;
