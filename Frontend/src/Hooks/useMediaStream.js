import { useRef, useEffect } from "react";
import ConnectionManager from "../Logic/ConnectionManager";


const CONSTRAINTS = {
  video: { width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 30 } },
  audio: false,
};

export function useMediaStream({ onFingers, onDraw, onErase, onReset, onReady, onError }) {
  const videoRef = useRef(null);

  useEffect(() => {
    const manager = new ConnectionManager();

    navigator.mediaDevices.getUserMedia(CONSTRAINTS)
      .then(async (stream) => {
        if (videoRef.current) videoRef.current.srcObject = stream;

        manager.connect(          
          stream,
          (data) => {
              onFingers(data.finger_tips);
              if (data.action === "draw") onDraw(data.coordinates);
              else if (data.action === "erase") onErase(data.coordinates);
              else onReset();
          },
          (state, message) => {
              if (state === "connected") onReady();
              else if (state === "fatal") onError({ type: "fatal", message });
              else if (state === "error") onError({ type: "error", message });
              else if (state === "reconnecting") onError({ type: "reconnecting", message });
          }
        );
      })
      .catch((err) => {
          onError({
              type: "fatal",
              message:
                  err.name === "NotAllowedError" ? "Camera access was denied." :
                  err.name === "NotFoundError"   ? "No camera found on this device." :
                  "Could not access camera.",
          });
      });

      return () => manager.disconnect();
  }, []);

  return { videoRef };
}