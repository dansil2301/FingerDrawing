class SessionStore {
    static instance = null;

    constructor() {
        const existing = localStorage.getItem("session_id");
        this.sessionId = existing || crypto.randomUUID();

        if (!existing) {
            localStorage.setItem("session_id", this.sessionId);
        }
    }

    static getInstance() {
        if (!SessionStore.instance) {
            SessionStore.instance = new SessionStore();
        }
        return SessionStore.instance;
    }

    get() {
        return this.sessionId;
    }

    clear() {
        this.sessionId = null;
        localStorage.removeItem("session_id");
    }
}

export default SessionStore.getInstance();