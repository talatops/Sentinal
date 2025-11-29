"""WebSocket handlers for real-time updates."""

from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio


def register_websocket_handlers(socketio_instance):
    """Register WebSocket event handlers."""

    @socketio_instance.on("connect")
    def handle_connect():
        """Handle client connection."""
        print(f"Client connected: {request.sid}")
        emit("connected", {"message": "Connected to Sentinel WebSocket"})

    @socketio_instance.on("disconnect")
    def handle_disconnect():
        """Handle client disconnection."""
        print(f"Client disconnected: {request.sid}")

    @socketio_instance.on("subscribe_scan")
    def handle_subscribe_scan(data):
        """Subscribe to scan updates for a specific run."""
        run_id = data.get("run_id")
        if run_id:
            room = f"scan_{run_id}"
            join_room(room)
            emit("subscribed", {"run_id": run_id, "room": room})
            print(f"Client {request.sid} subscribed to scan {run_id}")

    @socketio_instance.on("unsubscribe_scan")
    def handle_unsubscribe_scan(data):
        """Unsubscribe from scan updates."""
        run_id = data.get("run_id")
        if run_id:
            room = f"scan_{run_id}"
            leave_room(room)
            emit("unsubscribed", {"run_id": run_id})
            print(f"Client {request.sid} unsubscribed from scan {run_id}")

    @socketio_instance.on("subscribe_dashboard")
    def handle_subscribe_dashboard():
        """Subscribe to dashboard updates."""
        join_room("dashboard")
        emit("subscribed", {"room": "dashboard"})
        print(f"Client {request.sid} subscribed to dashboard")


def emit_scan_update(run_id, update_type, data):
    """Emit scan update to subscribed clients.

    Args:
        run_id: CI/CD run ID
        update_type: Type of update (progress, completed, failed, etc.)
        data: Update data
    """
    room = f"scan_{run_id}"
    socketio.emit("scan_update", {"run_id": run_id, "type": update_type, "data": data}, room=room)
    print(f"Emitted {update_type} update for scan {run_id} to room {room}")


def emit_dashboard_update(update_type, data):
    """Emit dashboard update to all subscribed clients.

    Args:
        update_type: Type of update (new_run, scan_completed, etc.)
        data: Update data
    """
    socketio.emit("dashboard_update", {"type": update_type, "data": data}, room="dashboard")
    print(f"Emitted {update_type} update to dashboard")
