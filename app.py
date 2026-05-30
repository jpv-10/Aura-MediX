"""
AURA MEDIX — Application Entry Point
FIXED: Proper imports and initialization
"""
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from nexus_core import create_nexus_app, socketio

    logger.info("Creating Flask application...")
    app = create_nexus_app()
    logger.info("Application created successfully")

    if __name__ == '__main__':
        logger.info("Starting AURA MEDIX application...")
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)

except Exception as e:
    logger.error(f"Failed to start application: {e}", exc_info=True)
    raise