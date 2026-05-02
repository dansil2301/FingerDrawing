import { useRef, useEffect } from "react";

export function useCanvasDrawing() {
  const missingFramesRef = useRef(0);
  const MAX_MISSING = 3

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

  const _preprocessing = (point) => {
      const cutX = 0.01;
      const cutYTop = 0.01;
      const cutYBottom = 0.25;

      if (point.x <= cutX || point.x >= 1 - cutX ||
          point.y <= cutYTop || point.y >= 1 - cutYBottom) {
          return null;
      }

      return {
          x: (point.x - cutX) / (1 - 2 * cutX),
          y: (point.y - cutYTop) / (1 - cutYTop - cutYBottom),
      };
  }

  const drawFingerTips = (tips) => {
    const canvas = overlayCanvasRef.current;
    const ctx = overCtxRef.current;
    if (!canvas || !ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!tips) return;
    
    tips.forEach(tip => {
      tip = _preprocessing(tip);
      if (!tip) return;

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

    point = _preprocessing(point);
    if (!point) return;

    const x = point.x * canvas.width;
    const y = point.y * canvas.height;
    const prev = prevPointRef.current;

    if (prev) {
      ctx.beginPath();
      ctx.moveTo(prev.x, prev.y);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    missingFramesRef.current = 0;
    prevPointRef.current = { x, y };
  };

  const clearRectArea = (rect) => {
      const canvas = mainCanvasRef.current;
      const ctx = mainCtxRef.current;
      if (!canvas || !ctx || !rect) return;

      const { ru_corner, ld_corner } = rect;

      const processedLd = _preprocessing(ld_corner) ?? ld_corner;
      const processedRu = _preprocessing(ru_corner) ?? ru_corner;

      const x1 = processedLd.x * canvas.width;
      const y1 = processedLd.y * canvas.height;
      const x2 = processedRu.x * canvas.width;
      const y2 = processedRu.y * canvas.height;

      ctx.clearRect(x1, y1, x2 - x1, y2 - y1);
      prevPointRef.current = null;
  };

  const resetStroke = () => {
    missingFramesRef.current++;
    if (missingFramesRef.current > MAX_MISSING) {
        prevPointRef.current = null;
    }
  };

  return { mainCanvasRef, overlayCanvasRef, drawFingerTips, drawPoint, clearRectArea, resetStroke };
}