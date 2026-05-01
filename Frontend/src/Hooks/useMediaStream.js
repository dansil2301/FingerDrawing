import { useRef, useEffect, useState } from "react";
import ConnectionManager from "../Logic/ConnectionManager";

const CONSTRAINTS = {
    video: { width: { ideal: 160 }, height: { ideal: 100 }, frameRate: { ideal: 15 } },
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

export function useMediaStream({
    onFingers,
    onDraw,
    onErase,
    onReset,
    onReady,
    onError,
    onQueueUpdate
}) {
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const managerRef = useRef(null);

    const [status, setStatus] = useState("loading");

    useEffect(() => {
        const manager = new ConnectionManager();
        managerRef.current = manager;

        async function start() {
            try {
                const stream = await acquireStream(streamRef, videoRef);

                await manager.connect(stream, {
                    onQueueUpdate: (data) => {
                        onQueueUpdate?.(data);

                        // UI state based on queue
                        if (data.allowed) {
                            setStatus("connecting_rtc");
                        } else {
                            setStatus("waiting");
                        }
                    },

                    onStateChange: (state, message) => {
                        if (state === "connected") {
                            setStatus("ready");
                            onReady?.();
                        } else if (state === "rtc_failed") {
                            setStatus("error");
                            onError?.({ type: "error", message: "RTC failed" });
                        } else if (state === "fatal") {
                            setStatus("error");
                            onError?.({ type: "fatal", message });
                        }
                    },

                    onSessionExpired: () => {
                        setStatus("session_expired");
                        onError?.({
                            type: "session_expired",
                            message: "Session expired"
                        });
                    },

                    onData: (data) => {
                        console.log(data);
                        onFingers?.(data.finger_tips);

                        if (data.action === "draw") {
                            onDraw?.(data.coordinates);
                        } else if (data.action === "erase") {
                            onErase?.(data.coordinates);
                        } else {
                            onReset?.();
                        }
                    }
                });

            } catch (err) {
                onError?.({
                    type: "fatal",
                    message:
                        err.name === "NotAllowedError" ? "Camera access was denied." :
                        err.name === "NotFoundError"   ? "No camera found on this device." :
                        "Could not access camera.",
                });

                setStatus("error");
            }
        }

        start();

        return () => {
            manager.disconnect();
            releaseStream(streamRef);
        };
    }, []);

    return { videoRef, status };
}
