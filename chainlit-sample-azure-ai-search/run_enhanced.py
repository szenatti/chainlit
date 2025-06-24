#!/usr/bin/env python3
"""
Enhanced Azure AI Search Chainlit Application Launcher
This script manages the startup of both the API server and Chainlit application.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def check_env_file():
    """Check if .env file exists and is configured"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  .env file not found. Copying from .env.example...")
            subprocess.run(["cp", ".env.example", ".env"], check=True)
            print("📝 Please edit .env file with your Azure credentials before continuing.")
            return False
        else:
            print("❌ Neither .env nor .env.example found")
            return False
    
    # Check if .env has required values
    with open(env_file) as f:
        content = f.read()
        if "your_azure_openai_api_key" in content or "your-search-service" in content:
            print("⚠️  .env file appears to contain placeholder values.")
            print("📝 Please update .env with your actual Azure credentials.")
            return False
    
    print("✅ Environment configuration appears to be set up")
    return True

def start_api_server():
    """Start the API server in background"""
    print("🚀 Starting Enhanced API Server on port 8001...")
    try:
        api_process = subprocess.Popen([
            sys.executable, "api_server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        if api_process.poll() is None:
            print("✅ API Server started successfully on http://localhost:8001")
            return api_process
        else:
            stdout, stderr = api_process.communicate()
            print(f"❌ API Server failed to start:")
            if stderr:
                print(stderr.decode())
            return None
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_chainlit_app():
    """Start the Chainlit application"""
    print("🚀 Starting Chainlit Application on port 8000...")
    try:
        chainlit_process = subprocess.Popen([
            "chainlit", "run", "app.py", "--port", "8000"
        ])
        return chainlit_process
    except Exception as e:
        print(f"❌ Failed to start Chainlit app: {e}")
        return None

def main():
    """Main function to orchestrate the startup"""
    print("🔍 Enhanced Azure AI Search Assistant - Startup Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("app.py").exists() or not Path("api_server.py").exists():
        print("❌ Please run this script from the chainlit-sample-azure-ai-search directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Check environment configuration
    if not check_env_file():
        print("⚠️  Please configure your .env file before running the application.")
        sys.exit(1)
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Cannot continue without API server")
        sys.exit(1)
    
    # Start Chainlit app
    chainlit_process = start_chainlit_app()
    if not chainlit_process:
        print("❌ Failed to start Chainlit application")
        if api_process:
            api_process.terminate()
        sys.exit(1)
    
    print("\n🎉 Applications started successfully!")
    print("=" * 60)
    print("📱 Chainlit Chat Interface: http://localhost:8000")
    print("🔧 API Server & Documentation: http://localhost:8001/docs")
    print("🏥 Health Check: http://localhost:8001/health")
    print("=" * 60)
    print("\n🔐 Authentication:")
    print("   Demo Username: testuser")
    print("   Demo Password: secret")
    print("\n📋 Features:")
    print("   • Secure document authentication")
    print("   • In-app PDF, Word, Excel viewers")
    print("   • Clickable citations with document preview")
    print("   • Support for 10+ file types")
    print("\n⚠️  Press Ctrl+C to stop both applications")
    print("=" * 60)
    
    # Set up signal handler for graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Shutting down applications...")
        try:
            chainlit_process.terminate()
            api_process.terminate()
            print("✅ Applications stopped successfully")
        except:
            print("⚠️  Some processes may still be running")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Wait for processes
    try:
        chainlit_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main() 