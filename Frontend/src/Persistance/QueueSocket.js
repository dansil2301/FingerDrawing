class QueueSocket {
    constructor() {
        const protocol = process.env.REACT_APP_ENV === "d" ? "ws" : "wss";
        const baseUrl = process.env.REACT_APP_BE_URL || "localhost:8000";
        this.baseUrl = `${protocol}://${baseUrl}/api/orchestration`;

        this.socket = null;
        this._intentionalClose = false;
        this._heartbeat = null;
    }

    connect(sessionId, { onUpdate, onSessionExpired, onStateChange }) {
        this._intentionalClose = false;

        const url = `${this.baseUrl}/${sessionId}`;
        console.log("[Queue] connecting:", url);

        this.socket = new WebSocket(url);

        this.socket.onopen = () => {
            console.log("[Queue] connected");
            onStateChange?.("connected");

            this._startHeartbeat();
        };

        this.socket.onmessage = (event) => {
            if (event.data === "pong") return;
            this._handleMessage(event, { onUpdate, onSessionExpired });
        };

        this.socket.onclose = () => {
            console.warn("[Queue] closed");

            this._stopHeartbeat();

            if (!this._intentionalClose) {
                onStateChange?.("disconnected");
            }
        };

        this.socket.onerror = (err) => {
            console.error("[Queue] error:", err);
        };
    }

    _startHeartbeat() {
        this._stopHeartbeat();

        this._heartbeat = setInterval(() => {
            if (this.socket?.readyState === WebSocket.OPEN) {
                try {
                    this.socket.send("ping");
                } catch (err) {
                    console.error("[Queue] heartbeat failed:", err);
                }
            }
        }, 5000);
    }

    _stopHeartbeat() {
        if (this._heartbeat) {
            clearInterval(this._heartbeat);
            this._heartbeat = null;
        }
    }

    _handleMessage(event, { onUpdate, onSessionExpired }) {
        let data;

        try {
            data = JSON.parse(event.data);
        } catch {
            // ignore non-JSON (like pong if you add later)
            return;
        }

        if (data?.error === "session expired") {
            console.warn("[Queue] session expired");

            this._intentionalClose = true;
            this.socket?.close();

            onSessionExpired?.();
            return;
        }

        if (
            typeof data.position === "number" &&
            typeof data.allowed === "boolean"
        ) {
            onUpdate?.({
                position: data.position,
                allowed: data.allowed
            });
            return;
        }

        console.warn("[Queue] unknown message:", data);
    }

    disconnect() {
        this._intentionalClose = true;

        this._stopHeartbeat(); // ✅ important
        this.socket?.close();
    }
}

export default QueueSocket;