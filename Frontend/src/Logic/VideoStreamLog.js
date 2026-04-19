import VideoStreamDal from "../Persistance/VideoStreamDal";

class VideoStreamLog {
    constructor() {
        this.videoDal = new VideoStreamDal();
    }

    async connect(stream) {
        await this.videoDal.connect(stream);  // returns session_id
    }

    close() {
        this.videoDal.close();
    }
}

export default VideoStreamLog;
