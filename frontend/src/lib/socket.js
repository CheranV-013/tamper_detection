import { io } from "socket.io-client";

const rawBase = import.meta.env.VITE_API_BASE_URL || "https://tamper-detection-2.onrender.com";
const SOCKET_URL = rawBase.replace(/\/+$/, "");

export function createSocket() {
  return io(SOCKET_URL, {
    transports: ["websocket", "polling"],
    upgrade: true,
    reconnection: true
  });
}

export { SOCKET_URL };
