"""
AURA MEDIX — Quick Launch Script
Run: python run.py
FIXED: Proper error handling and startup sequence
"""
import os
import sys
import logging

# Configure logging BEFORE importing Flask
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure we're in the right directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

logger.info("="*70)
logger.info("AURA MEDIX — Healthcare AI Platform v2.1.0")
logger.info("="*70)

try:
    from nexus_core import create_nexus_app, socketio

    logger.info("Creating Flask application...")
    app = create_nexus_app()
    logger.info("Flask application created successfully")

    if __name__ == '__main__':
        print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║            A U R A   M E D I X   v 2 . 1 . 0               ║
║            The Future of Healthcare Intelligence             ║
║                                                              ║
║  🌐  http://localhost:5000                                   ║
║  🔐  Demo: demo@auramedix.ai / Demo@2024                     ║
║  👤  Or click "Continue as Guest"                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        logger.info("Starting AURA MEDIX server...")
        logger.info("Listening on http://localhost:5000")
        logger.info("Press CTRL+C to stop the server")
        
        try:
            socketio.run(
                app,
                debug=True,
                host='0.0.0.0',
                port=5000,
                allow_unsafe_werkzeug=True
            )
        except KeyboardInterrupt:
            logger.info("Server shutdown initiated by user")
            print("\n✓ Server stopped gracefully")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            print(f"\n✗ Server error: {e}")
            sys.exit(1)

except ImportError as e:
    logger.error(f"Import error: {e}", exc_info=True)
    print(f"✗ Import error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    logger.error(f"Startup error: {e}", exc_info=True)
    print(f"✗ Startup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)