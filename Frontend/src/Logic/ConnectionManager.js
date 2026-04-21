import CoordsStreamDAL from '../Persistance/CoordsStreamDAL';
import VideoStreamDal from '../Persistance/VideoStreamDal';


const MAX_ATTEMPTS = 5;
const BASE_DELAY = 1000;
const MAX_DELAY = 15000;

class ConnectionManager {
    constructor() {
        this.coordsDal = new CoordsStreamDAL();
        this.videoDal = new VideoStreamDal();

        this._stream = null;
        this._onMessage = null;
        this._onStateChange = null;

        this._attempts = 0;
        this._reconnectTimer = null;
        this._stopped = false;
    }

    async connect(stream, onMessage, onStateChange) {
        this._stream = stream;
        this._onMessage = onMessage;
        this._onStateChange = onStateChange;

        await this._tryConnect();
    }

    async _tryConnect() {
        try {
            this._onStateChange("connecting");

            await this.videoDal.connect(
                this._stream, 
                (state) => {
                    this._onStateChange(state);
                    if (state === "failed" || state === "disconnected") {
                        this._scheduleReconnect();
                    }
                }
            );

            this.coordsDal.connect(this._onMessage);

            this._attempts = 0;
            this._onStateChange("connected");

        } catch (err) {
            this._onStateChange("error", this._errorMessage(err));
            this._scheduleReconnect();
        }
    }

    _scheduleReconnect() {
        if (this._stopped) return;
        if (this._attempts >= MAX_ATTEMPTS) {
            this._onStateChange(
                "fatal",
                `Connection failed after ${MAX_ATTEMPTS} attempts. Please refresh.`
            );
            return;
        }

        const delay = Math.min(BASE_DELAY * 2 ** this._attempts, MAX_DELAY);
        this._attempts++;

        console.log(`[CM] Reconnecting in ${delay}ms (attempt ${this._attempts}/${MAX_ATTEMPTS})`);
        this._onStateChange("reconnecting", `Reconnecting... (${this._attempts}/${MAX_ATTEMPTS})`);

        this._reconnectTimer = setTimeout(async () => {
            this.videoDal.close();
            this.coordsDal.disconnect();
            await this._tryConnect();
        }, delay);
    }

    _errorMessage(err) {
        if (err.name === "NotAllowedError") return "Camera access was denied.";
        if (err.name === "NotFoundError")   return "No camera found on this device.";
        if (err.message?.includes("Offer")) return "Could not reach the server.";
        return "Connection failed.";
    }

    disconnect() {
        this._stopped = true;
        clearTimeout(this._reconnectTimer);
        this.videoDal.close();
        this.coordsDal.disconnect();
    }
}

export default ConnectionManager;