import { useRef, useEffect } from "react";

export function useCanvasDrawing() {
  const overlayCanvasRef = useRef(null);
  const overCtxRef = useRef(null);

  const mainCanvasRef = useRef(null);
  const mainCtxRef = useRef(null);
  const prevPointRef = useRef(null);

    useEffect(() => {
      const mainCanvas = mainCanvasRef.current;
      const mainCtx = mainCanvas.getContext("2d");
      mainCanvas.width = mainCanvas.offsetWidth;
      mainCanvas.height = mainCanvas.offsetHeight;
      mainCtx.lineWidth = 3;
      mainCtx.lineCap = "round";
      mainCtx.strokeStyle = "white";
      mainCtxRef.current = mainCtx;

      const overlayCanvas = overlayCanvasRef.current;
      const overCtx = overlayCanvas.getContext("2d");
      overlayCanvas.width = overlayCanvas.offsetWidth;
      overlayCanvas.height = overlayCanvas.offsetHeight;
      overCtx.lineWidth = 2;
      overCtx.lineCap = "round";
      overCtx.strokeStyle = "rgba(255,255,255,0.6)";
      overCtxRef.current = overCtx;
    }, []);

  const drawFingerTips = (tips) => {
    const canvas = overlayCanvasRef.current;
    const ctx = overCtxRef.current;
    if (!canvas || !ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!tips) return;
    
    tips.forEach(tip => {
      const x = tip.x * canvas.width;
      const y = tip.y * canvas.height;

      ctx.beginPath();
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.stroke();
    });
  }

  const drawPoint = (point) => {
    const canvas = mainCanvasRef.current;
    const ctx = mainCtxRef.current;
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

  const clearRectArea = (rect) => {
    const canvas = mainCanvasRef.current;
    const ctx = mainCtxRef.current;
    if (!canvas || !ctx || !rect) return;

    const { ru_corner, ld_corner } = rect;
    const x1 = ld_corner.x * canvas.width;
    const y1 = ld_corner.y * canvas.height;
    const x2 = ru_corner.x * canvas.width;
    const y2 = ru_corner.y * canvas.height;

    ctx.clearRect(x1, y1, x2 - x1, y2 - y1);
    prevPointRef.current = null;
  };

  const resetStroke = () => {
    prevPointRef.current = null;
  };

  return { mainCanvasRef, overlayCanvasRef, drawFingerTips, drawPoint, clearRectArea, resetStroke };
}