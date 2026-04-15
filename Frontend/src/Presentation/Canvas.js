import './Canvas.css';
import CoordsStreamLog from '../Logic/CoordsStreamLog'
import VideoStreamLog from '../Logic/VideoStreamLog'
import { useRef, useEffect } from "react";

function Canvas() {
  const videoRef = useRef(null);
  const pcRef = useRef(null);
  
  const mainCanvas = useRef(null);
  const ctxRef = useRef(null);
  const prevPointRef = useRef(null);

  const clearRectArea = (rect) => {
    const canvas = mainCanvas.current;
    const ctx = ctxRef.current;

    if (!canvas || !ctx || !rect) return;

    const { ru_corner, ld_corner } = rect;

    // Calculate rectangle bounds
    const x1 = ld_corner.x * canvas.width;
    const y1 = ld_corner.y * canvas.height;

    const x2 = ru_corner.x * canvas.width;
    const y2 = ru_corner.y * canvas.height;

    const width = x2 - x1;
    const height = y2 - y1;

    ctx.clearRect(x1, y1, width, height);

    // reset drawing so lines don't connect across erased area
    prevPointRef.current = null;
  };
  
  const drawPoint = (point) => {
    const canvas = mainCanvas.current;
    const ctx = ctxRef.current;

    if (!canvas || !ctx || !point) return;

    const x = point.x * canvas.width;
    const y = point.y * canvas.height;

    const prev = prevPointRef.current;

    if (prev) {
      ctx.beginPath();
      ctx.moveTo(prev.x, prev.y);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    prevPointRef.current = { x, y };
  };

  useEffect(() => {
    const canvas = mainCanvas.current;
    const ctx = canvas.getContext("2d");

    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;

    ctx.lineWidth = 3;
    ctx.lineCap = "round";
    ctx.strokeStyle = "white";

    ctxRef.current = ctx;
  }, []);

  useEffect(() => {
    const videoSocket = new CoordsStreamLog();

    videoSocket.connect((data) => {
      console.log(data.action);
      if (data.action === "draw") {
        drawPoint(data.coordinates);
      }
      else if (data.action === "erase") {
        clearRectArea(data.coordinates);
      }
      else {
        prevPointRef.current = null;
      }
    });

    return () => videoSocket.disconnect();
  }, []);

  useEffect(() => {
    const rtc = new VideoStreamLog()

    const constraints = {
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30 },
      },
      audio: false,
    };

    navigator.mediaDevices.getUserMedia(constraints)
      .then((stream) => {
        rtc.connect(stream);
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error("Camera error:", err);
      });

    return () => rtc.close();
  }, []);

  return (
    <div className="App">
      <div className="CanvasWrapper">
        <canvas ref={mainCanvas} className="MainCanvas" />

        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="CameraFeed"
        />
      </div>
    </div>
  );
}

export default Canvas;