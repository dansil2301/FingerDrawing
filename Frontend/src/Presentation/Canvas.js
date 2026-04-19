import './Canvas.css';
import { useCanvasDrawing } from '../Hooks/useCanvasDrawing';
import { useMediaStream } from '../Hooks/useMediaStream';

function Canvas() {
  const { mainCanvas, drawPoint, clearRectArea, resetStroke } = useCanvasDrawing();

  const { videoRef } = useMediaStream({
    onDraw:  drawPoint,
    onErase: clearRectArea,
    onReset: resetStroke,
  });

  return (
    <div className="App">
      <div className="CanvasWrapper">
        <canvas ref={mainCanvas} className="MainCanvas" />
        <video ref={videoRef} autoPlay playsInline className="CameraFeed" />
      </div>
    </div>
  );
}

export default Canvas;