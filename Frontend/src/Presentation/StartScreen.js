import './StartScreen.css';


function StartScreen({ onStart }) {
  return (
    <div className="StartScreen">
      <div className="StartCard">
        <h1 className="StartTitle">Hand Drawing</h1>

        <p className="StartText">
          To draw, use your <strong>index finger</strong>. Make sure it is clearly visible.
        </p>

        <p className="StartText">
          Avoid pointing directly at the camera — tracking may be lost.
        </p>

        <p className="StartText">
          To erase, show your <strong>open hand</strong> and move over the drawing.
        </p>

        <button className="StartButton" onClick={onStart}>
          Start
        </button>

        <p className="StartHint">
          You will be asked to allow camera access
        </p>
      </div>
    </div>
  );
}

export default StartScreen
