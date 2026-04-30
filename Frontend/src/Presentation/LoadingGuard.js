import { ERROR_MESSAGES } from '../Constants/ErrorMessages'


function LoadingGuard({ status, error, position }) {
    if (status === "ready") return null;

    if (status === "waiting") {
        return (
            <div className="overlay">
                <img src="/Eye.png" alt="Waiting" className="pulse" />

                <p className="overlay-hint">
                    Waiting for your turn...
                </p>

                {position !== null && (
                    <p className="overlay-position">
                        Position in queue: {position}
                    </p>
                )}
            </div>
        );
    }

    if (status === "connecting_rtc") {
        return (
            <div className="overlay">
                <img src="/Eye.png" alt="Connecting" className="pulse" />
                <p className="overlay-hint">Starting session...</p>
            </div>
        );
    }

    if (status === "loading") {
        return (
            <div className="overlay">
                <img src="/Eye.png" alt="Loading" className="pulse" />
            </div>
        );
    }

    if (error?.type === "session_expired") {
        return (
            <div className="overlay">
                <h2 className="overlay-title">Session ended</h2>
                <p className="overlay-hint">Refresh to continue</p>
                <button onClick={() => window.location.reload()}>
                    Reload
                </button>
            </div>
        );
    }

    const { title, hint } =
        ERROR_MESSAGES[error?.message] ?? ERROR_MESSAGES.default;

    return (
        <div className="overlay">
            <h2 className="overlay-title">{title}</h2>
            <p className="overlay-hint">{hint}</p>
            <button onClick={() => window.location.reload()}>
                Reload
            </button>
        </div>
    );
}

export default LoadingGuard
