#!/bin/bash
# This script runs the Chainlit application

# Activate virtual environment
source venv/bin/activate

# Run the Chainlit application
chainlit run app.py --port 8000
