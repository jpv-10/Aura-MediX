"""
AURA MEDIX — WSGI Entry Point
For production deployment with gunicorn:
  gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""
from nexus_core import create_nexus_app, socketio
import os

env = os.getenv('FLASK_ENV', 'production')
app = create_nexus_app(env)

if __name__ == '__main__':
    socketio.run(app)
