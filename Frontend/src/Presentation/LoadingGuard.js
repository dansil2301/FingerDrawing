import './LoadingGuard.css';


function LoadingGuard({ status, error }) {
  if (status === "ready") return null;

  return (
    <div className="overlay">
      {status === "loading" && (
        <img src="/Eye.png" alt="Loading" className="pulse" />
      )}
      {status === "error" | error && (
        <>
          <h2>Connection error</h2>
          <p>Something went wrong. Please reload the page.</p>
          <button onClick={() => window.location.reload()}>Reload</button>
        </>
      )}
    </div>
  );
}

export default LoadingGuard
