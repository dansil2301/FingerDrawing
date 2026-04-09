import './App.css';

import { useEffect, useRef } from "react";


function App() {
  const canvasRef = useRef(null);
  
  useEffect(() => {
  if (canvasRef.current) {
  const ctx = canvasRef.current.getContext("2d");
      ctx?.strokeRect(200, 200, 40, 50);
    }
  }, []);

  return (
    <div className="App">
         <canvas
          ref={canvasRef}
          width="400"
          height="350"
          style={{ border: "2px solid black" }}
        />
    </div>
  );
}

export default App;
