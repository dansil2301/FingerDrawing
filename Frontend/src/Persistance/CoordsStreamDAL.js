import SessionStore from './SessionStore';


class CoordsStreamDAL {
    constructor() {
        const protocol = process.env.REACT_APP_ENV === "d" ? "ws" : "wss";
        const baseUrl = process.env.REACT_APP_BE_URL || "localhost:8000";
        this.wsBaseUrl = `${protocol}://${baseUrl}/coordinates`;

        this.socket = null;
    }

    connect(onMessage) {
        const url = `${this.wsBaseUrl}/${SessionStore.get()}`;
        console.log("[WS] Connecting to:", url);

        this.socket = new WebSocket(url);
        this.setupHandlers(onMessage);
    }

    setupHandlers(onMessage) {
        this.socket.onopen = this.handleOpen.bind(this);
        this.socket.onmessage = this.handleMessage.bind(this, onMessage);
        this.socket.onclose = this.handleClose.bind(this);
        this.socket.onerror = this.handleError.bind(this);
    }

    handleOpen() {
        console.log("[WS] Connected");
    }

    handleMessage(onMessage, event) {
        try {
            const data = JSON.parse(event.data);
            onMessage?.(data);
        } catch (err) {
            console.error("[WS] Parse error:", err);
            throw err;
        }
    }

    handleClose() {
        console.warn("[WS] Closed");
    }

    handleError(err) {
        console.error("[WS] Error:", err);
        this.socket.close();
        throw err;
    }

    disconnect() {
        this.socket?.close();
    }
}

export default CoordsStreamDAL;