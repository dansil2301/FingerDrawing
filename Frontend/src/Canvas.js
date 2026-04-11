import './Canvas.css';
import { useRef, useEffect, useCallback } from "react";

function Canvas() {
  const videoRef = useRef(null);
  const captureCanvasRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
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
    }, 300);

    return () => clearInterval(interval);
  }, [sendFrame]);

  return (
    <div className="App">
      <div className="CanvasWrapper">
        <canvas className="MainCanvas" />

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