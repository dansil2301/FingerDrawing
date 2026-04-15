import VideoStreamDal from "../Persistance/VideoStreamDal";


class VideoStreamLog {
    constructor() {
        this.videoDal = new VideoStreamDal();
    }

    connect(stream) {
        this.videoDal.connect(stream);
    }

    close() {
        this.videoDal.close();
    }
}

export default VideoStreamLog
