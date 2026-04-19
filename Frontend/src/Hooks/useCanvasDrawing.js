import { useRef, useEffect } from "react";

export function useCanvasDrawing() {
  const mainCanvas = useRef(null);
  const ctxRef = useRef(null);
  const prevPointRef = useRef(null);

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

  const clearRectArea = (rect) => {
    const canvas = mainCanvas.current;
    const ctx = ctxRef.current;
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

  return { mainCanvas, drawPoint, clearRectArea, resetStroke };
}