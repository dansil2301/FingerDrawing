import { useRef, useEffect } from "react";
import VideoStreamLog from "../Logic/VideoStreamLog";
import CoordsStreamLog from "../Logic/CoordsStreamLog";

const CONSTRAINTS = {
  video: { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } },
  audio: false,
};

export function useMediaStream({ onDraw, onErase, onReset, onReady, onError }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const rtc = new VideoStreamLog();
    const ws = new CoordsStreamLog();

    navigator.mediaDevices.getUserMedia(CONSTRAINTS)
      .then(async (stream) => {
        if (videoRef.current) videoRef.current.srcObject = stream;

        await rtc.connect(stream);

        ws.connect((data) => {
          if (data.action === "draw") onDraw(data.coordinates);
          else if (data.action === "erase") onErase(data.coordinates);
          else onReset();
        });

        onReady?.();
      })
      .catch((err) => {
        console.error("Camera error:", err);
        onError?.(err);
      });

    return () => {
      rtc.close();
      ws.disconnect();
    };
  }, []);

  return { videoRef };
}