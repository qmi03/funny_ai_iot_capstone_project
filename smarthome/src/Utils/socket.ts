import ReconnectingWebSocket from "reconnecting-websocket";

export const ws = new ReconnectingWebSocket(
    `ws://${import.meta.env.VITE_FASTAPI_HOST}:${
        import.meta.env.VITE_FASTAPI_PORT
    }/connect`
);
ws.onopen = () => {
    console.log("Connected to server");
};

ws.onclose = () => {
    console.log("Disconnected from server");
};
