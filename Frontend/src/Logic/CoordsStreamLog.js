import CoordsStreamDAL from "../Persistance/CoordsStreamDAL";

class CoordsStreamLog {
    constructor() {
        this.coordsDal = new CoordsStreamDAL();
    }

    connect(sessionId, onMessage) {
        this.coordsDal.connect(sessionId, onMessage);
    }

    disconnect() {
        this.coordsDal.disconnect();
    }
}

export default CoordsStreamLog;
