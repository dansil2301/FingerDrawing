import CoordsStreamDAL from '../Persistance/CoordsStreamDAL';
import VideoStreamDal from '../Persistance/VideoStreamDal';

const MAX_ATTEMPTS = 5;
const BASE_DELAY = 1000;
const MAX_DELAY = 15000;

class ConnectionManager {
    constructor() {
        this.coordsDal = new CoordsStreamDAL();
        this.videoDal = new VideoStreamDal();
        this._attempts = 0;
        this._stopped = false;
    }

    async connect(stream, onMessage, onStateChange, onNeedsFreshStream) {
        this._onMessage = onMessage;
        this._onStateChange = onStateChange;
        this._onNeedsFreshStream = onNeedsFreshStream;
        
        await this._start(stream);
    }

    async reconnectWithStream(stream) {
        await this._start(stream);
    }

    disconnect() {
        this._stopped = true;
        this.videoDal.close();
        this.coordsDal.disconnect();
    }

    async _start(stream) {
        try {
            this._onStateChange("connecting");
            await this.videoDal.connect(stream, (state) => this._onRtcState(state));
        } catch (err) {
            this._retry(err);
        }
    }

    _onRtcState(state) {
        if (state === "connected") {
            this.coordsDal.connect(this._onMessage);
            this._attempts = 0;
            this._onStateChange("connected");
        } else if (state === "failed" || state === "disconnected") {
            this._retry();
        }
    }

    _retry(err) {
        if (this._stopped) return;

        if (this._attempts >= MAX_ATTEMPTS) {
            this._onStateChange("fatal", `Failed after ${MAX_ATTEMPTS} attempts. Please refresh.`);
            return;
        }

        const delay = Math.min(BASE_DELAY * 2 ** this._attempts, MAX_DELAY);
        this._attempts++;

        this._onStateChange("reconnecting", `Reconnecting... (${this._attempts}/${MAX_ATTEMPTS})`);
        console.log(`[CM] Retry ${this._attempts}/${MAX_ATTEMPTS} in ${delay}ms`, err?.message ?? "");

        setTimeout(() => {
            this.videoDal.close();
            this.coordsDal.disconnect();
            this._onNeedsFreshStream();
        }, delay);
    }
}

export default ConnectionManager;