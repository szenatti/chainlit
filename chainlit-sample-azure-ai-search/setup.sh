#!/bin/bash

# Azure AI Search Chainlit Setup Script
# This script helps you set up the development environment

echo "🔍 Azure AI Search Chainlit Setup"
echo "=================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9.0"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python $python_version is not compatible. Please install Python 3.9+ and try again."
    exit 1
fi

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created from template"
    echo ""
    echo "🔧 Please edit the .env file with your Azure credentials:"
    echo "   - AZURE_OPENAI_API_KEY"
    echo "   - AZURE_OPENAI_ENDPOINT" 
    echo "   - AZURE_OPENAI_DEPLOYMENT_NAME"
    echo "   - AZURE_SEARCH_SERVICE_ENDPOINT"
    echo "   - AZURE_SEARCH_API_KEY"
    echo "   - AZURE_SEARCH_INDEX_NAME"
    echo "   - AZURE_STORAGE_ACCOUNT_NAME"
    echo "   - AZURE_STORAGE_CONTAINER_NAME"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo "🎉 Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit the .env file with your Azure credentials"
echo "2. Run the application:"
echo "   • For development: chainlit run app.py"
echo "   • For full features: python main.py"
echo ""
echo "🔗 The application will be available at:"
echo "   • Chat Interface: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs (FastAPI mode only)"
echo ""
echo "💡 Don't forget to activate your virtual environment in future sessions:"
echo "   source venv/bin/activate" 