#!/usr/bin/env python3
"""
Setup script for Promptflow integration

This script helps set up the promptflow environment and connections.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"⚙️  {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Python 3.9 or higher is required for Promptflow")
        return False
    print(f"✅ Python {version.major}.{version.minor} is compatible")
    return True

def install_promptflow():
    """Install promptflow packages."""
    packages = [
        "promptflow-azure>=1.18.0",
        "promptflow[azure]>=1.17.0",
        "azure-ai-ml>=1.21.0",
        "azure-identity>=1.19.0"
    ]
    
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            return False
    return True

def create_connections_config():
    """Create a promptflow connections configuration file."""
    config_content = """# Promptflow Connections Configuration
# This file contains connection templates for Azure OpenAI

connections:
  azure_openai_connection:
    type: AzureOpenAI
    api_key: ${AZURE_OPENAI_API_KEY}
    api_base: ${AZURE_OPENAI_ENDPOINT}
    api_version: ${AZURE_OPENAI_API_VERSION}
    api_type: azure

# To create the connection, run:
# pf connection create --file connections.yaml
"""
    
    config_path = Path("promptflow_connections.yaml")
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"✅ Created promptflow connections config: {config_path}")
    return True

def create_env_template():
    """Create a .env template if it doesn't exist."""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    env_template = """# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# Database Configuration (Optional - defaults to Docker PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chainlit_db
"""
    
    with open(env_path, "w") as f:
        f.write(env_template)
    
    print(f"✅ Created .env template: {env_path}")
    print("⚠️  Please edit .env with your actual Azure OpenAI credentials")
    return True

def validate_flow_structure():
    """Validate that promptflow directories and files exist."""
    flows = {
        "chat_assistant": [
            "flow.dag.yaml",
            "prepare_prompt.py",
            "llm_prompt.jinja2",
            "format_response.py"
        ],
        "document_qa": [
            "flow.dag.yaml",
            "preprocess_document.py",
            "extract_context.py",
            "qa_prompt.jinja2",
            "calculate_relevance.py",
            "extract_sources.py"
        ]
    }
    
    all_valid = True
    for flow_name, files in flows.items():
        flow_dir = Path(f"promptflows/{flow_name}")
        if not flow_dir.exists():
            print(f"❌ Flow directory missing: {flow_dir}")
            all_valid = False
            continue
        
        for file_name in files:
            file_path = flow_dir / file_name
            if not file_path.exists():
                print(f"❌ Flow file missing: {file_path}")
                all_valid = False
    
    if all_valid:
        print("✅ All promptflow files are present")
    
    return all_valid

def create_sample_data():
    """Ensure sample documents directory exists."""
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    
    if not (sample_dir / "sample_company_policy.txt").exists():
        print("⚠️  Sample document not found. You can add documents to sample_documents/ for testing")
    else:
        print("✅ Sample documents are available")
    
    return True

def main():
    """Main setup function."""
    print("🚀 Promptflow Integration Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_python_version():
        return 1
    
    # Setup steps
    steps = [
        (install_promptflow, "Install Promptflow packages"),
        (create_env_template, "Create environment template"),
        (create_connections_config, "Create connections configuration"),
        (validate_flow_structure, "Validate flow structure"),
        (create_sample_data, "Check sample data")
    ]
    
    success_count = 0
    for step_func, description in steps:
        print(f"\n📋 {description}")
        if step_func():
            success_count += 1
        else:
            print(f"❌ Setup step failed: {description}")
    
    print("\n" + "=" * 50)
    print(f"Setup Results: {success_count}/{len(steps)} steps completed")
    
    if success_count == len(steps):
        print("\n🎉 Promptflow setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit .env with your Azure OpenAI credentials")
        print("2. Run: python test_promptflow.py")
        print("3. Start the application: chainlit run app.py")
        return 0
    else:
        print("\n❌ Some setup steps failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 