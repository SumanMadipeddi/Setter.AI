#!/usr/bin/env python3
"""
Setter.AI Startup Script
========================

Simple script to start the Setter.AI application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Start the Setter.AI application"""
    try:
        from setter_ai.web.app import create_app
        
        print("🚀 Starting Setter.AI...")
        print("📞 AI Lead Calling System")
        print("=" * 40)
        
        # Create and run the Flask application
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you have installed all dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting Setter.AI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
