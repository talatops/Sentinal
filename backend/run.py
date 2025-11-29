"""Application entry point."""

import os
from app import create_app, db, socketio

# Create app instance at module level for gunicorn
# This is required for gunicorn to work properly
app = create_app(os.environ.get("FLASK_ENV", "production"))

# SocketIO is already initialized in create_app(), no need to init again


@app.shell_context_processor
def make_shell_context():
    """Shell context for Flask shell."""
    return {"db": db, "app": app}


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_ENV") == "development")
