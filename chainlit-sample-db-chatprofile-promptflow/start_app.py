#!/usr/bin/env python3
"""
Startup script for Chainlit app with Promptflow integration

This script handles environment validation and starts the application.
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Check if environment is properly configured."""
    load_dotenv()
    
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create/update your .env file with the required values.")
        print("Run: python setup_promptflow.py to create a template.")
        return False
    
    print("✅ Environment variables are configured")
    return True

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import chainlit
        import openai
        import dotenv
        import sqlalchemy
        import asyncpg
        print("✅ Core dependencies are installed")
        
        # Check promptflow (optional)
        try:
            import promptflow
            print("✅ Promptflow is available")
            return True, True
        except ImportError:
            print("⚠️  Promptflow not installed - some features will be unavailable")
            return True, False
            
    except ImportError as e:
        print(f"❌ Missing required dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False, False

def check_database():
    """Check if database is accessible."""
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres", "--format", "table {{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if "postgres" in result.stdout:
            print("✅ PostgreSQL database is running")
            return True
        else:
            print("⚠️  PostgreSQL database not detected")
            print("   You can start it with: docker-compose up -d postgres")
            return True  # Not fatal, app can still start
            
    except Exception:
        print("⚠️  Could not check database status")
        return True  # Not fatal

def start_application():
    """Start the Chainlit application."""
    print("\n🚀 Starting Chainlit application...")
    print("   Access the app at: http://localhost:8000")
    print("   Press Ctrl+C to stop\n")
    
    try:
        subprocess.run(["chainlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except FileNotFoundError:
        print("❌ Chainlit not found. Install with: pip install chainlit")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Application failed to start: {e}")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🔥 Chainlit + Promptflow Application Startup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        print("\n💡 Tip: Run 'python setup_promptflow.py' to set up the environment")
        return 1
    
    # Check dependencies
    deps_ok, promptflow_ok = check_dependencies()
    if not deps_ok:
        return 1
    
    # Check database
    check_database()
    
    # Show available features
    print(f"\n📋 Available Features:")
    print(f"   🤖 Standard chat profiles: ✅")
    print(f"   🔄 Promptflow enhanced profiles: {'✅' if promptflow_ok else '❌'}")
    print(f"   📄 Document Q&A: {'✅' if promptflow_ok else '❌'}")
    print(f"   💾 Chat persistence: ✅")
    
    if not promptflow_ok:
        print(f"\n💡 To enable Promptflow features, install dependencies:")
        print(f"   pip install promptflow-azure promptflow[azure]")
    
    # Start the application
    if start_application():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 