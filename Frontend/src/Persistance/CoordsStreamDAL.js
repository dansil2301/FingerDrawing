class CoordsStreamDAL {
    constructor() {
        const protocol =
        process.env.REACT_APP_ENV === "d" ? "ws" : "wss";

        const baseUrl =
        process.env.REACT_APP_BE_URL || "localhost:8000";

        this.wsUrl = `${protocol}://${baseUrl}/ws`;

        this.socket = null;
        this.reconnectDelay = 1000;
        this.maxDelay = 10000;
        this.shouldReconnect = true;
    }

    connect(onMessage) {
        console.log("[WS] Connecting to:", this.wsUrl);

        this.socket = new WebSocket(this.wsUrl);

        this.setupHandlers(onMessage);
    }

    setupHandlers(onMessage) {
        this.socket.onopen = this.handleOpen.bind(this);
        this.socket.onmessage = this.handleMessage.bind(this, onMessage);
        this.socket.onclose = this.handleClose.bind(this, onMessage);
        this.socket.onerror = this.handleError.bind(this);
    }

    handleOpen() {
        console.log("[WS] Connected");
        this.reconnectDelay = 1000;
    }

    handleMessage(onMessage, event) {
        try {
            const data = JSON.parse(event.data);
        onMessage?.(data);
        } catch (e) {
            console.error("[WS] Parse error:", e);
        }
    }

    handleClose(onMessage) {
        console.warn("[WS] Closed");

        if (!this.shouldReconnect) return;

        console.log(`[WS] Reconnecting in ${this.reconnectDelay}ms`);

        setTimeout(() => {
            this.connect(onMessage);
        }, this.reconnectDelay);

        this.reconnectDelay = Math.min(
            this.reconnectDelay * 2,
            this.maxDelay
        );
    }

    handleError(err) {
        console.error("[WS] Error:", err);
        this.socket.close();
    }

    disconnect() {
        this.shouldReconnect = false;
        this.socket?.close();
    }
}

export default CoordsStreamDAL;
