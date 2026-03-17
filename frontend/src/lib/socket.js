import { io } from "socket.io-client";

const SOCKET_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "https://tamper-detection-2.onrender.com";

export function createSocket() {
  return io(SOCKET_URL, {
    transports: ["websocket", "polling"],
    reconnection: true
  });
}