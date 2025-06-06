# Chainlit Application with Azure OpenAI

This is a simple chat application built using Chainlit and Azure OpenAI that works seamlessly on **macOS**, **Windows**, and **Linux**.

## Prerequisites

- **Python 3.9+** installed
- An **Azure account** with access to Azure OpenAI
- **Azure OpenAI resource** provisioned with a model deployment

## Platform Support

✅ **macOS** - Fully supported  
✅ **Windows** - Fully supported  
✅ **Linux** - Fully supported  

## Setup

### 1. Clone or Download Repository
```bash
# Clone if using git
git clone <repository-url>
cd chainlit-sample

# Or download and extract the files
```

### 2. Create and Activate Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate
```

**On Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

**Option A: Using .env file (Recommended)**
1. Copy the example file:
   ```bash
   # macOS/Linux
   cp .env.example .env
   
   # Windows
   copy .env.example .env
   ```

2. Edit the `.env` file with your Azure OpenAI credentials:
   ```env
   AZURE_OPENAI_API_KEY=your_actual_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-07-01-preview
   ```

**Option B: Set Environment Variables Directly**

**macOS/Linux:**
```bash
export AZURE_OPENAI_API_KEY="your_actual_api_key_here"
export AZURE_OPENAI_ENDPOINT="https://your_resource_name.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
```

**Windows (Command Prompt):**
```cmd
set AZURE_OPENAI_API_KEY=your_actual_api_key_here
set AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/
set AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

**Windows (PowerShell):**
```powershell
$env:AZURE_OPENAI_API_KEY="your_actual_api_key_here"
$env:AZURE_OPENAI_ENDPOINT="https://your_resource_name.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="your_deployment_name"
```

## Running the Application

To start the Chainlit application:

```bash
chainlit run app.py
```

The application will start and be accessible at [http://localhost:8000](http://localhost:8000)

## Cross-Platform Notes

### Python Command
- **macOS/Linux**: Use `python3` if `python` doesn't work
- **Windows**: Usually `python` works, but try `python3` if needed

### Virtual Environment Activation
- The activation commands differ between platforms (see setup section above)
- Always ensure your virtual environment is activated before running the app

### Path Separators
- The application automatically handles path differences between platforms
- No manual adjustments needed for file paths

## Configuration

You can customize the application by modifying:
- **`chainlit.md`**: Application styling and welcome message
- **`app.py`**: Application logic and AI behavior
- **`.env`**: Environment variables and API credentials

## Troubleshooting

### Common Issues

**1. Python Not Found**
```bash
# Try different Python commands
python --version
python3 --version
py --version  # Windows only
```

**2. Virtual Environment Issues**
- Make sure you're in the project directory
- Check if virtual environment is activated (you should see `(venv)` in your terminal)
- Try deactivating and reactivating: `deactivate` then activate again

**3. Package Installation Issues**
```bash
# Upgrade pip first
pip install --upgrade pip

# Then install requirements
pip install -r requirements.txt
```

**4. Azure OpenAI Connection Issues**
- Verify your API key and endpoint in the `.env` file
- Check that your Azure OpenAI deployment is active
- Ensure your Azure subscription has sufficient credits

### Platform-Specific Issues

**macOS:**
- If you get SSL certificate errors, try: `pip install --upgrade certifi`

**Windows:**
- If PowerShell execution policy prevents script running:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## License

This project is licensed under the **MIT License** by **Sergio Zenatti Filho**.

### MIT License

```
MIT License

Copyright (c) 2025 Sergio Zenatti Filho

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```


