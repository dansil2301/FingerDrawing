import CoordsStreamDAL from "../Persistance/CoordsStreamDAL";

class CoordsStreamLog {
    constructor() {
        this.coordsDal = new CoordsStreamDAL();
    }

    connect(onMessage) {
        this.coordsDal.connect(onMessage);
    }

    disconnect() {
        this.coordsDal.disconnect();
    }
}

export default CoordsStreamLog;
