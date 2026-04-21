import './Canvas.css';
import { useState } from "react";
import LoadingGuard from "./LoadingGuard";
import { useCanvasDrawing } from '../Hooks/useCanvasDrawing';
import { useMediaStream } from '../Hooks/useMediaStream';

function Canvas() {
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState(null);

  const { mainCanvasRef, overlayCanvasRef, drawFingerTips, drawPoint, clearRectArea, resetStroke } = useCanvasDrawing();

  const { videoRef } = useMediaStream({
    onFingers: drawFingerTips,
    onDraw:    drawPoint,
    onErase:   clearRectArea,
    onReset:   resetStroke,
    onReady:   () => setStatus("ready"),
    onError:   (err) => { setError(err); setStatus("error"); },
  });

  return (
    <div className="App">
      <div className="CanvasWrapper">
        <canvas ref={overlayCanvasRef} className="OverlayCanvas" />
        <canvas ref={mainCanvasRef} className="MainCanvas" />
        <video ref={videoRef} autoPlay playsInline className="CameraFeed" />
        <LoadingGuard status={status} error={error} />
      </div>
    </div>
  );
}

export default Canvas;