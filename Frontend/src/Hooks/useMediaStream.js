import { useRef, useEffect } from "react";
import ConnectionManager from "../Logic/ConnectionManager";

const CONSTRAINTS = {
    video: { width: { ideal: 160 }, height: { ideal: 100 }, frameRate: { ideal: 20 } },
    audio: false,
};

async function acquireStream(streamRef, videoRef) {
    if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
    }
    streamRef.current = await navigator.mediaDevices.getUserMedia(CONSTRAINTS);
    if (videoRef.current) {
        videoRef.current.srcObject = streamRef.current;
    }
    return streamRef.current;
}

function releaseStream(streamRef) {
    if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop());
        streamRef.current = null;
    }
}

function makeMessageHandler({ onFingers, onDraw, onErase, onReset }) {
    return (data) => {
        onFingers(data.finger_tips);
        if (data.action === "draw") onDraw(data.coordinates);
        else if (data.action === "erase") onErase(data.coordinates);
        else onReset();
    };
}

function makeStateHandler({ onReady, onError }) {
    return (state, message) => {
        if (state === "connected") onReady();
        else if (state === "fatal") onError({ type: "fatal", message });
        else if (state === "error") onError({ type: "error", message });
        else if (state === "reconnecting") onError({ type: "reconnecting", message });
    };
}

function makeRestartHandler(manager, streamRef, videoRef, onError) {
    return async () => {
        try {
            await acquireStream(streamRef, videoRef);
            await manager.reconnectWithStream(streamRef.current);
        } catch (err) {
            onError({ type: "fatal", message: "Could not restart camera." });
        }
    };
}

export function useMediaStream({ onFingers, onDraw, onErase, onReset, onReady, onError }) {
    const videoRef = useRef(null);
    const streamRef = useRef(null);

    useEffect(() => {
        const manager = new ConnectionManager();

        async function start() {
            try {
                const stream = await acquireStream(streamRef, videoRef);

                await manager.connect(
                    stream,
                    makeMessageHandler({ onFingers, onDraw, onErase, onReset }),
                    makeStateHandler({ onReady, onError }),
                    makeRestartHandler(manager, streamRef, videoRef, onError)
                );
            } catch (err) {
                onError({
                    type: "fatal",
                    message:
                        err.name === "NotAllowedError" ? "Camera access was denied." :
                        err.name === "NotFoundError"   ? "No camera found on this device." :
                        "Could not access camera.",
                });
            }
        }

        start();

        return () => {
            manager.disconnect();
            releaseStream(streamRef);
        };
    }, []);

    return { videoRef };
}