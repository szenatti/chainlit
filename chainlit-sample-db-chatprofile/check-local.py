#!/usr/bin/env python3
"""
Quick validation script for local Chainlit development setup.
Checks if PostgreSQL Docker container and local environment are ready.
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def check_docker_postgres():
    """Check if PostgreSQL Docker container is running."""
    print("🔍 Checking PostgreSQL Docker container...")
    
    try:
        # Check if container exists and is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=chainlit_postgres", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if "Up" in result.stdout:
            print("✅ PostgreSQL container is running")
            return True
        else:
            print("❌ PostgreSQL container is not running")
            print("💡 Run: docker-compose up -d postgres")
            return False
            
    except subprocess.CalledProcessError:
        print("❌ Docker command failed")
        print("💡 Make sure Docker is installed and running")
        return False
    except FileNotFoundError:
        print("❌ Docker not found")
        print("💡 Install Docker first")
        return False

def check_local_env():
    """Check if local environment is properly set up."""
    print("🔍 Checking local Python environment...")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment is active")
        venv_active = True
    else:
        print("⚠️  Virtual environment not detected")
        print("💡 Recommended: source venv/bin/activate")
        venv_active = False
    
    # Check required packages
    required_packages = ['chainlit', 'openai', 'asyncpg', 'sqlalchemy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("🔍 Checking .env configuration...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("💡 Run: ./run-local.sh")
        return False
    
    load_dotenv()
    
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT', 
        'AZURE_OPENAI_DEPLOYMENT_NAME',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.environ.get(var, '')
        if not value or 'your_' in value.lower():
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or unconfigured: {', '.join(missing_vars)}")
        print("💡 Edit .env file with your Azure OpenAI credentials")
        return False
    else:
        print("✅ Environment variables configured")
        return True

def main():
    """Main validation function."""
    print("🚀 Local Development Setup Check")
    print("=" * 35)
    
    checks = [
        check_docker_postgres(),
        check_env_file(),
        check_local_env()
    ]
    
    print("\n" + "=" * 35)
    
    if all(checks):
        print("✅ Local development setup is ready!")
        print("🚀 Run: chainlit run app.py")
        print("🌐 Access: http://localhost:8000")
        print("\n🔑 Demo credentials:")
        print("   - admin / admin123")
        print("   - user / user123") 
        print("   - demo / demo123")
        return 0
    else:
        print("❌ Some checks failed. Please review the issues above.")
        print("\n💡 Quick setup:")
        print("   1. ./run-local.sh")
        print("   2. Edit .env with your Azure OpenAI credentials")
        print("   3. source venv/bin/activate")
        print("   4. pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 