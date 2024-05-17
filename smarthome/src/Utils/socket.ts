export const ws = new WebSocket(
    `ws://${import.meta.env.VITE_FASTAPI_HOST}:${
        import.meta.env.VITE_FASTAPI_PORT
    }/ws`
);
