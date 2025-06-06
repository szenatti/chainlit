# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Setup Environment
```bash
cd chainlit-sample-db-chatprofile-promptflow
python setup_promptflow.py
```

### Step 2: Configure Credentials
Edit the generated `.env` file:
```bash
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### Step 3: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Start Application
```bash
python start_app.py
```

### Step 5: Test Features
1. **Login**: Use `admin/admin123` or `user/user123`
2. **Basic Chat**: Try "Assistant" profile
3. **Enhanced Chat**: Try "PromptFlow-Assistant" profile  
4. **Document Q&A**: Upload `sample_documents/sample_company_policy.txt` and ask "What is the remote work policy?"

## 🎯 What You Get

- ✅ **5 Chat Profiles**: Assistant, Creative, Analytical, Technical, Business
- ✅ **2 Promptflow Profiles**: Enhanced Assistant + Document Q&A
- ✅ **Persistent Chat**: All conversations saved
- ✅ **File Upload**: Document analysis with citations
- ✅ **Role-Based Access**: Admin vs user permissions

## 🔧 Troubleshooting

**Missing dependencies?**
```bash
pip install promptflow-azure promptflow[azure] azure-ai-ml azure-identity
```

**Database issues?**
```bash
docker-compose up -d postgres
```

**Test everything works?**
```bash
python test_promptflow.py
```

## 📚 Key Files

- `app.py` - Main application
- `promptflows/` - AI flow definitions  
- `start_app.py` - Smart startup
- `README.md` - Full documentation
- `SUMMARY.md` - What was built 