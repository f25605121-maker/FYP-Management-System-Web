"""
Production Entry Point for FYP Management System.
Configured for Railway deployment with WebSocket support.
"""
import os
import sys
from backend.app import app, socketio

if __name__ == '__main__':
    # Production mode detection
    is_production = os.environ.get('FLASK_ENV') == 'production'
    is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
    
    # Port from environment or default
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Listen on all interfaces
    
    # Logging
    print(f"[FYP] Starting application...")
    print(f"[FYP] Environment: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")
    print(f"[FYP] Running on Railway: {is_railway}")
    print(f"[FYP] Listening on {host}:{port}")
    print(f"[FYP] Debug mode: {not is_production}")
    
    # Run with SocketIO (handles WebSockets properly)
    socketio.run(
        app,
        host=host,
        port=port,
        debug=not is_production,
        use_reloader=False,  # Important: disable reloader in production
        log_output=True
    )
