import { useState } from "react";
import Canvas from "./Presentation/Canvas";
import StartScreen from "./Presentation/StartScreen";

function App() {
  const [started, setStarted] = useState(false);

  if (!started) {
    return <StartScreen onStart={() => setStarted(true)} />;
  }

  return <Canvas />;
}

export default App;