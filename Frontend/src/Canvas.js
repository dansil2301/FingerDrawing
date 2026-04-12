import './Canvas.css';
import { useRef, useEffect, useCallback } from "react";

function Canvas() {
  const videoRef = useRef(null);
  const captureCanvasRef = useRef(null);
  
  const mainCanvas = useRef(null);
  const ctxRef = useRef(null);
  const prevPointRef = useRef(null);

  const socketRef = useRef(null);

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
    const socket = new WebSocket("ws://localhost:8000/ws");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.action === "draw") {
        console.log(data.action);
        drawPoint(data.coordinates);
      }

      if (data.action === "erase") {
        clearRectArea(data.coordinates);
      }
      
      console.log("From backend:", event.data);
    };

    socket.onclose = () => {
      console.log("WebSocket closed");
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => socket.close();
  }, []);

  const captureFrame = useCallback(() => {
    const video = videoRef.current;
    const canvas = captureCanvasRef.current;

    if (!video || !canvas || video.videoWidth === 0) return null;

    const ctx = canvas.getContext("2d");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    ctx.drawImage(video, 0, 0);

    return canvas;
  }, []);

  const sendFrame = useCallback(() => {
    const canvas = captureFrame();
    if (!canvas) return;

    const socket = socketRef.current;
    if (!socket || socket.readyState !== 1) return;

    canvas.toBlob((blob) => {
      if (blob) {
        socket.send(blob);
      }
    }, "image/jpeg", 0.5);
  }, [captureFrame]);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error("Camera error:", err);
      });

    const interval = setInterval(() => {
      sendFrame();
    }, 100);

    return () => clearInterval(interval);
  }, [sendFrame]);

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

        <canvas ref={captureCanvasRef} style={{ display: "none" }} />
      </div>
    </div>
  );
}

export default Canvas;