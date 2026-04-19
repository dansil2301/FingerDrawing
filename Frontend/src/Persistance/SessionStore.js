class SessionStore {
    static instance = null;
    
    constructor() {
        this.sessionId = null;
    }

    static getInstance() {
        if (!SessionStore.instance) {
            SessionStore.instance = new SessionStore();
        }
        return SessionStore.instance;
    }

    set(sessionId) {
        this.sessionId = sessionId;
    }

    get() {
        return this.sessionId;
    }

    clear() {
        this.sessionId = null;
    }
}

export default SessionStore.getInstance();