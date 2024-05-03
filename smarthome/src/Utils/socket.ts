import io from "socket.io-client";

export const socket = io(
    `${import.meta.env.VITE_FLASK_HOST}:${import.meta.env.VITE_FLASK_PORT}`
);
socket.on("connect", () => {
    console.log("Connected to server");
});

socket.on("disconnect", () => {
    console.log("Disconnected from server");
});
