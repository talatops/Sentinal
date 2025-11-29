import { io } from "socket.io-client";

const WS_URL = import.meta.env.VITE_WS_URL || "http://localhost";

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
    this.listeners = new Map();
  }

  connect() {
    if (this.socket?.connected) {
      return;
    }

    this.socket = io(WS_URL, {
      transports: ["websocket", "polling"],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
    });

    this.socket.on("connect", () => {
      console.log("WebSocket connected");
      this.connected = true;
      this.emit("connected", {});
    });

    this.socket.on("disconnect", () => {
      console.log("WebSocket disconnected");
      this.connected = false;
    });

    this.socket.on("connect_error", (error) => {
      console.error("WebSocket connection error:", error);
      this.connected = false;
    });

    // Subscribe to dashboard updates by default
    this.socket.emit("subscribe_dashboard");
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }

  subscribeToScan(runId) {
    if (this.socket && this.connected) {
      this.socket.emit("subscribe_scan", { run_id: runId });
    }
  }

  unsubscribeFromScan(runId) {
    if (this.socket && this.connected) {
      this.socket.emit("unsubscribe_scan", { run_id: runId });
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  off(event, callback) {
    const listeners = this.listeners.get(event);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }

    if (this.socket) {
      this.socket.off(event, callback);
    }
  }

  emit(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data);
    }
  }

  isConnected() {
    return this.connected;
  }
}

// Create singleton instance
const wsService = new WebSocketService();

export default wsService;
