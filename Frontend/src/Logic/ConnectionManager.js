import QueueSocket from '../Persistance/QueueSocket';
import RtcClient from '../Persistance/RtcClient';
import SessionStore from '../Persistance/SessionStore'


class ConnectionManager {
    constructor() {
        this.queue = new QueueSocket();
        this.rtc = new RtcClient();

        this._rtcStarted = false;
        this._allowed = false;
        this._stopped = false;
    }

    async connect(stream, { onQueueUpdate, onStateChange, onSessionExpired, onData }) {
        this._stream = stream;
        this._onQueueUpdate = onQueueUpdate;
        this._onStateChange = onStateChange;
        this._onSessionExpired = onSessionExpired;
        this._handleRtcData = onData;

        this._connectQueue();
    }

    disconnect() {
        this._stopped = true;
        this.queue.disconnect();
        this.rtc.close();
    }

    _connectQueue() {
        const sessionId = SessionStore.get();

        this.queue.connect(sessionId, {
            onUpdate: (data) => this._handleQueueUpdate(data),

            onSessionExpired: () => this._handleSessionExpired(),

            onStateChange: (state) => {
                if (state === "disconnected") {
                    console.warn("[CM] WS disconnected → reload");
                    this._onStateChange("fatal", "Connection lost. Please reload.");
                }
            }
        });
    }

    async _handleQueueUpdate(data) {
        this._allowed = data.allowed;

        this._onQueueUpdate?.(data);

        if (!data.allowed) {
            this._onStateChange("waiting");
            return;
        }

        if (data.allowed && !this._rtcStarted) {
            this._rtcStarted = true;
            await this._startRtc();
        }
    }

    async _startRtc() {
        try {
            await this.rtc.start(
                this._stream,
                SessionStore.get(),
                (state) => this._handleRtcState(state),
                (data) => this._handleRtcData(data)
            );
        } catch (err) {
            console.error("[CM] RTC failed:", err);
            this._onStateChange("fatal", "Failed to start stream. Reload required.");
        }
    }

    _handleRtcState(state) {
        if (state === "connected") {
            this._onStateChange("connected");
        }

        if (state === "failed" || state === "disconnected") {
            console.warn("[CM] RTC died → reload");
            this._onStateChange("fatal", "Connection lost. Please reload.");
        }
    }

    _handleSessionExpired() {
        this._stopped = true;

        this.queue.disconnect();
        this.rtc.close();

        this._onSessionExpired?.();
    }
}

export default ConnectionManager;
