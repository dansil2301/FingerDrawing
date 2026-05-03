import './StartScreen.css';


function StartScreen({ onStart }) {
  return (
    <div className="StartScreen">
      <div className="StartCard">
        <h1 className="StartTitle">Hand Drawing</h1>

        <div className="GestureGuide">
          <div className="GestureItem">
            <img src="/finger-up.jpg" alt="Correct finger position" />
            <span>Correct</span>
          </div>

          <div className="GestureItem wrong">
            <img src="/finger-forward.jpg" alt="Wrong finger position" />
            <span>Not detected</span>
          </div>
        </div>

        <p className="StartText">
          Your finger must be <strong>fully visible</strong> and clearly separated from your hand.
        </p>

        <p className="StartText warning">
          Do NOT point directly at the screen — this will <strong>not be detected</strong>.
        </p>

        <p className="StartText success">
          Keep your finger <strong>upright (facing up)</strong> for best tracking.
        </p>

        <p className="StartText">
          To erase, show your <strong>open hand</strong> and move it over the drawing.
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
