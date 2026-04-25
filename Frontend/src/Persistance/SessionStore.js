class SessionStore {
    static instance = null;

    constructor() {
        this.sessionId = localStorage.getItem("session_id") || this._generate();
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
        this.sessionId = this._generate();
    }

    _generate() {
        const id = crypto.randomUUID();
        localStorage.setItem("session_id", id);
        return id;
    }
}

export default SessionStore.getInstance();