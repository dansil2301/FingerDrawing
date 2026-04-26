import SessionStore from './SessionStore';


class CoordsStreamDAL {
    constructor() {
        const protocol = process.env.REACT_APP_ENV === "d" ? "ws" : "wss";
        const baseUrl = process.env.REACT_APP_BE_URL || "localhost:8000";
        this.wsBaseUrl = `${protocol}://${baseUrl}/coordinates`;

        this.socket = null;
    }

    connect(onMessage, onSessionExpired, onStateChange) {
        this._intentionalClose = false;
        const url = `${this.wsBaseUrl}/${SessionStore.get()}`;
        console.log("[WS] Connecting to:", url);
        this.socket = new WebSocket(url);
        this.setupHandlers(onMessage, onSessionExpired, onStateChange);
    }

    setupHandlers(onMessage, onSessionExpired, onStateChange) {
        this.socket.onopen = () => {
            console.log("[WS] Connected");
            onStateChange?.("connected");
        };
        this.socket.onmessage = this.handleMessage.bind(this, onMessage, onSessionExpired);
        this.socket.onclose = () => {
            console.warn("[WS] Closed");
            if (!this._intentionalClose) {
                onStateChange?.("disconnected");
            }
        };
        this.socket.onerror = (err) => {
            console.error("[WS] Error:", err);
        };
    }

    handleMessage(onMessage, onSessionExpired, event) {
        try {
            const data = JSON.parse(event.data);
            if (data.error === "session expired") {
                console.warn("[WS] Session expired");
                this._intentionalClose = true;
                onSessionExpired?.();
                return;
            }

            onMessage?.(data);
        } catch (err) {
            console.error("[WS] Parse error:", err);
        }
    }

    disconnect() {
        this._intentionalClose = true;
        this.socket?.close();
    }
}

export default CoordsStreamDAL;