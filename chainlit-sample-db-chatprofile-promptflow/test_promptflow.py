#!/usr/bin/env python3
"""
Test script for Promptflow integration

This script tests the promptflow flows independently to ensure they work correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    try:
        from promptflow import PFClient
        from promptflow.core import Flow
        print("✅ Promptflow imports successful")
        return True
    except ImportError as e:
        print(f"❌ Promptflow import failed: {e}")
        print("Install with: pip install promptflow-azure promptflow[azure]")
        return False

def test_environment():
    """Test that required environment variables are set."""
    print("\nTesting environment variables...")
    
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
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def test_flow_files():
    """Test that flow files exist."""
    print("\nTesting flow file structure...")
    
    flows = {
        "chat_assistant": [
            "flow.dag.yaml",
            "prepare_prompt.py",
            "llm_prompt.jinja2",
            "format_response.py",
            "requirements.txt"
        ],
        "document_qa": [
            "flow.dag.yaml",
            "preprocess_document.py",
            "extract_context.py",
            "qa_prompt.jinja2",
            "calculate_relevance.py",
            "extract_sources.py",
            "requirements.txt"
        ]
    }
    
    all_files_exist = True
    
    for flow_name, files in flows.items():
        flow_dir = f"./promptflows/{flow_name}"
        print(f"\nChecking {flow_name} flow:")
        
        if not os.path.exists(flow_dir):
            print(f"❌ Flow directory missing: {flow_dir}")
            all_files_exist = False
            continue
        
        for file_name in files:
            file_path = os.path.join(flow_dir, file_name)
            if os.path.exists(file_path):
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} missing")
                all_files_exist = False
    
    return all_files_exist

def test_chat_assistant_flow():
    """Test the chat assistant flow."""
    print("\nTesting chat assistant flow...")
    
    try:
        from promptflow.core import Flow
        
        flow_path = "./promptflows/chat_assistant"
        if not os.path.exists(flow_path):
            print(f"❌ Flow directory not found: {flow_path}")
            return False
        
        # Try to load the flow
        flow = Flow.load(flow_path)
        print("✅ Chat assistant flow loaded successfully")
        
        # Test with sample inputs
        test_inputs = {
            "question": "Hello, how are you?",
            "chat_history": [],
            "profile_name": "Assistant"
        }
        
        print("  Testing with sample inputs...")
        result = flow(test_inputs)
        
        if result and "answer" in result:
            print("✅ Chat assistant flow executed successfully")
            print(f"  Sample response: {result['answer'][:100]}...")
            return True
        else:
            print("❌ Chat assistant flow execution failed - no answer returned")
            return False
            
    except Exception as e:
        print(f"❌ Chat assistant flow test failed: {e}")
        return False

def test_document_qa_flow():
    """Test the document Q&A flow."""
    print("\nTesting document Q&A flow...")
    
    try:
        from promptflow.core import Flow
        
        flow_path = "./promptflows/document_qa"
        if not os.path.exists(flow_path):
            print(f"❌ Flow directory not found: {flow_path}")
            return False
        
        # Try to load the flow
        flow = Flow.load(flow_path)
        print("✅ Document Q&A flow loaded successfully")
        
        # Test with sample inputs
        sample_document = """
        This is a sample document about company policies.
        Employees must follow all safety guidelines.
        Work hours are from 9 AM to 5 PM.
        """
        
        test_inputs = {
            "question": "What are the work hours?",
            "document_content": sample_document,
            "chat_history": []
        }
        
        print("  Testing with sample inputs...")
        result = flow(test_inputs)
        
        if result and "answer" in result:
            print("✅ Document Q&A flow executed successfully")
            print(f"  Sample response: {result['answer'][:100]}...")
            return True
        else:
            print("❌ Document Q&A flow execution failed - no answer returned")
            return False
            
    except Exception as e:
        print(f"❌ Document Q&A flow test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Promptflow Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_environment,
        test_flow_files,
        test_chat_assistant_flow,
        test_document_qa_flow
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Promptflow integration is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 