"""Application entry point."""
import os
from app import create_app, db, socketio

app = create_app(os.environ.get('FLASK_ENV', 'production'))

@app.shell_context_processor
def make_shell_context():
    """Shell context for Flask shell."""
    return {'db': db, 'app': app}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=os.environ.get('FLASK_ENV') == 'development')
