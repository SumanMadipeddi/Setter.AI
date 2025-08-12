#!/usr/bin/env python3
"""
Setter.AI - Main Entry Point
============================

Main entry point for the Setter.AI application using the organized package structure.
"""

from setter_ai.web.app import create_app
from setter_ai.utils.config import get_environment_help
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        logger.info("🚀 Starting Setter.AI System...")
        logger.info("📞 AI Lead Calling System with Professional Female Voice")
        
        # Check if we're running in development mode
        if os.getenv('FLASK_ENV') == 'development':
            logger.info("🔧 Development mode detected")
        
        # Create Flask application
        app = create_app()
        
        # Start the application
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except RuntimeError as e:
        if "Missing required API keys" in str(e):
            logger.error("❌ Configuration Error:")
            logger.error(str(e))
            logger.info("\n" + get_environment_help())
            logger.info("\n💡 Quick Setup:")
            logger.info("1. Create a .env file in the project root")
            logger.info("2. Add your API keys (see .env.example)")
            logger.info("3. Restart the application")
        else:
            logger.error(f"Configuration error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to start Setter.AI: {str(e)}")
        raise

if __name__ == '__main__':
    main()
