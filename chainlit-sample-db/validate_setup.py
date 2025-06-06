#!/usr/bin/env python3
"""
Validation script for Chainlit application setup.
This script checks if all components are properly configured.
"""

import os
import sys
from dotenv import load_dotenv

def check_env_variables():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_DEPLOYMENT_NAME',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var) or os.environ.get(var) == f'your_{var.lower()}_here':
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or unconfigured environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables are configured")
        return True

def check_dependencies():
    """Check if all required Python packages are installed."""
    print("🔍 Checking Python dependencies...")
    
    required_packages = [
        'chainlit',
        'openai',
        'python-dotenv',
        'asyncpg',
        'sqlalchemy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing Python packages: {', '.join(missing_packages)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All Python dependencies are installed")
        return True

def check_database_connection():
    """Check if database connection is working."""
    print("🔍 Checking database connection...")
    
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            db_url = os.environ.get('DATABASE_URL', '')
            if not db_url:
                return False
            
            # Parse the URL to extract connection parameters
            if 'postgresql+asyncpg://' in db_url:
                db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
            
            try:
                conn = await asyncpg.connect(db_url)
                await conn.close()
                return True
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
        
        result = asyncio.run(test_connection())
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {str(e)}")
        return False

def main():
    """Main validation function."""
    print("🚀 Chainlit Application Validation")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    checks = [
        check_dependencies(),
        check_env_variables(),
        check_database_connection()
    ]
    
    print("\n" + "=" * 40)
    
    if all(checks):
        print("✅ All checks passed! Your Chainlit application is ready to run.")
        print("🚀 Run: docker-compose up --build")
        print("🌐 Access: http://localhost:8000")
        print("\n🔑 Demo credentials:")
        print("   - admin / admin123")
        print("   - user / user123")
        print("   - demo / demo123")
        return 0
    else:
        print("❌ Some checks failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 