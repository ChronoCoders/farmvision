#!/usr/bin/env python3
"""
Farm Vision Application Entry Point
Production-ready Flask application startup with proper logging and configuration
"""
import os
import logging
from app import app

def main():
    """Main application entry point with production-grade startup handling"""
    try:
        # Get environment-specific configuration
        flask_env = os.environ.get('FLASK_ENV', 'development')
        debug_mode = flask_env == 'development'
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        
        # Production environment detection
        if flask_env == 'production':
            debug_mode = False
        
        # Log startup information
        if debug_mode:
            logging.info(f"Starting Farm Vision - Environment: {flask_env}")
            logging.info(f"Server: {host}:{port}")
        
        # Start the application
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True,  # Enable threading for better performance
            use_reloader=debug_mode,  # Only use reloader in development
            use_debugger=debug_mode   # Only use debugger in development
        )
        
    except KeyboardInterrupt:
        logging.info("Application shutdown requested by user")
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        raise
    finally:
        logging.info("Farm Vision application stopped")

if __name__ == '__main__':
    main()
