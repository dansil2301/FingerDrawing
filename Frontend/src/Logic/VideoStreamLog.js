import VideoStreamDal from "../Persistance/VideoStreamDal";


class VideoStreamLog {
    constructor() {
        this.videoDal = new VideoStreamDal();
    }

    connect() {
        this.videoDal.connect();
    }

    close() {
        this.videoDal.close();
    }
}

export default VideoStreamLog
