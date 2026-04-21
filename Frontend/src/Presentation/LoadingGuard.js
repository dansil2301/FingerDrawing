import './LoadingGuard.css';
import { ERROR_MESSAGES } from '../Constants/ErrorMessages';


function LoadingGuard({ status, error }) {
    if (status === "ready") return null;

    if (status === "loading" || error?.type === "reconnecting") {
        return (
            <div className="overlay">
                <img src="/Eye.png" alt="Loading" className="pulse" />
                {error?.message && <p className="overlay-hint">{error.message}</p>}
            </div>
        );
    }

    const { title, hint } = ERROR_MESSAGES[error?.message] ?? ERROR_MESSAGES.default;

    return (
        <div className="overlay">
            <h2 className="overlay-title">{title}</h2>
            <p className="overlay-hint">{hint}</p>
            <button className="overlay-btn" onClick={() => window.location.reload()}>
                Reload
            </button>
        </div>
    );
}

export default LoadingGuard
