# Dynamic Chainlit Application with YAML Configuration System

🎯 **A completely data-driven Chainlit application** where all chat profiles, authentication, and AI behaviors are configured through YAML files - **no code changes needed** for new use cases!

This enhanced chat application features a **revolutionary YAML-based configuration system** that eliminates code duplication and makes the application instantly adaptable to any use case through simple configuration changes.

## 🌟 **NEW: Dynamic Configuration System**

### ✨ **Zero Code Changes for New Use Cases**
- Add new chat profiles by editing YAML files
- Configure user authentication and roles through YAML
- Set up promptflow integrations via configuration
- Deploy multiple specialized AI assistants without touching code

### 📁 **Configuration-Driven Architecture**
- **`config/profiles.yaml`** - Define all chat profiles and their behaviors
- **`config/auth.yaml`** - Manage users, roles, and permissions
- **`config/promptflows.yaml`** - Configure AI workflow integrations
- **Dynamic validation** - Built-in configuration validation system

### 🚀 **What This Means for You**
Instead of hardcoded profiles, you can now:
1. **Create specialized AI assistants** (Legal, Medical, Financial) by editing YAML
2. **Deploy different versions** for different clients with different configurations
3. **Scale effortlessly** - add 10 new AI personalities in 10 minutes
4. **Maintain easily** - all customization in configuration files, not code

## 🎯 Features

### 👥 **Dynamic Chat Profiles**
**Profiles are now configured in `config/profiles.yaml`:**

**Standard Profiles (Available to All Users):**
- 🤖 **Assistant**: General-purpose AI for everyday tasks
- 🎨 **Creative**: Enhanced creativity for storytelling and content
- 📊 **Analytical**: Logical responses for data analysis and problem-solving

**🆕 Promptflow-Enhanced Profiles:**
- 🔄 **PromptFlow-Assistant**: Advanced conversational AI with flow orchestration
- 📄 **Document-QA**: Intelligent document analysis with citations

**Admin-Only Profiles:**
- ⚙️ **Technical**: Advanced technical discussions and system architecture
- 💼 **Business**: Strategic business advice and professional guidance

**➕ Easy to Add More:**
Add any specialized profile (Medical, Legal, Financial, etc.) by editing the YAML configuration!

### 🔐 **Dynamic Authentication**
- **Role-based access control** configured in `config/auth.yaml`
- **User management** through configuration files
- **Profile access control** - different users see different profiles
- **Flexible permissions** system

### 💾 **Data Persistence & Advanced Features**
- **Chat History**: Persistent conversations with PostgreSQL
- **Human Feedback**: Thumbs up/down rating system
- **File Uploads**: Document analysis capabilities  
- **Promptflow Integration**: Advanced AI workflows
- **Docker Support**: Easy deployment

## 🚀 Quick Start

### 1. **Setup Environment**

```bash
# Navigate to the project directory
cd chainlit-sample-db-chatprofile-promptflow-YAML

# Create environment file
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
# AZURE_OPENAI_API_KEY=your_actual_api_key
# AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### 2. **Start Database** (Optional - uses Docker)

**On macOS/Linux:**
```bash
./run.sh
```

**On Windows:**
```cmd
run-local.bat
```

**Or manually start PostgreSQL:**
```bash
docker-compose up -d postgres
```

### 3. **Setup Python Environment**

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 4. **Run the Dynamic Application**

```bash
chainlit run app_dynamic.py
```

**Or with custom port:**
```bash
chainlit run app_dynamic.py --port 8000
```

### 5. **Access the Application**

- Open [http://localhost:8000](http://localhost:8000)
- Login with demo credentials:
  - **Admin**: `admin` / `admin123` (access to all profiles)
  - **User**: `user` / `user123` (standard profiles only)
  - **Demo**: `demo` / `demo123` (standard profiles only)

## 🔧 Configuration Guide

### Adding a New Chat Profile

**Example: Add a "Legal Assistant" profile**

Edit `config/profiles.yaml`:
```yaml
profiles:
  Legal:
    name: "Legal"
    markdown_description: "**Legal Assistant** - Specialized legal research and analysis"
    icon: "/public/icons/legal.svg"
    temperature: 0.3
    system_prompt: "You are a legal AI assistant with expertise in law, regulations, and legal research. Provide accurate legal information while reminding users to consult qualified attorneys."
    enabled: true
    requires_role: "lawyer"  # Only users with 'lawyer' role can access
    model_settings:
      max_tokens: 2000
      top_p: 0.9
```

### Adding a New User

Edit `config/auth.yaml`:
```yaml
users:
  legal_user:
    password: "legal123"
    role: "lawyer"
    metadata:
      full_name: "Legal Professional"
      department: "Legal"
    enabled: true

roles:
  lawyer:
    description: "Legal professional with access to legal tools"
    permissions:
      - "view_legal_profiles"
    profile_access:
      - "Assistant"
      - "Legal"
      - "Analytical"
```

**That's it!** Restart the application and the new profile and user are available.

## 📁 Project Structure

```
chainlit-sample-db-chatprofile-promptflow-YAML/
├── 🎯 Main Application
│   └── app_dynamic.py                 # Dynamic configuration-driven app
│
├── ⚙️ Configuration System
│   ├── config/
│   │   ├── profiles.yaml              # 👥 Chat profiles definition
│   │   ├── auth.yaml                  # 🔐 Users, roles & permissions  
│   │   ├── promptflows.yaml           # 🔄 AI workflow configurations
│   │   ├── config_loader.py           # 📥 Configuration loader
│   │   ├── promptflow_executor.py     # 🚀 Dynamic flow executor
│   │   ├── config_validator.py        # ✅ Configuration validation
│   │   └── examples/
│   │       └── custom_profiles.yaml   # 📋 Example configurations
│   │
├── 🤖 AI Workflows  
│   ├── promptflows/
│   │   ├── chat_assistant/            # Enhanced chat flow
│   │   └── document_qa/               # Document analysis flow
│   │
├── 📚 Documentation
│   ├── README.md                      # This file
│   ├── README_DYNAMIC.md              # Detailed configuration guide
│   ├── docs/DYNAMIC_CONFIGURATION.md  # Complete documentation
│   └── CLEANUP_SUMMARY.md             # Recent changes summary
│   │
├── 🛠️ Setup & Deployment
│   ├── requirements.txt               # Python dependencies
│   ├── docker-compose.yml             # Database setup
│   ├── run.sh / run-local.bat        # Quick start scripts
│   └── .env.example                   # Environment template
```

## 🎮 Usage Examples

### 1. **Enhanced Chat Assistant**
1. Login and select **"PromptFlow-Assistant"** profile
2. Experience advanced AI responses with sophisticated prompt engineering

### 2. **Document Analysis**
1. Select **"Document-QA"** profile
2. Upload a document or paste content
3. Ask questions about the document
4. Get answers with relevance scoring and citations

### 3. **Role-Based Access**
- **Admin users** see all profiles including Technical and Business
- **Regular users** see standard profiles only
- **Specialized roles** (if configured) see domain-specific profiles

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Required: Azure OpenAI
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your_resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_model_deployment
AZURE_OPENAI_API_VERSION=2023-07-01-preview

# Optional: Database (defaults to Docker PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/chainlit_db
```

### Configuration Validation
```bash
# Validate all configuration files
python config/config_validator.py

# Check specific configuration
python -c "from config.config_loader import get_config_loader; loader = get_config_loader(); print('✅ Configuration loaded successfully')"
```

### Custom Profiles Examples

See `config/examples/custom_profiles.yaml` for ready-to-use profiles:
- **Medical Assistant** - Healthcare specialized AI
- **Financial Advisor** - Financial planning and analysis
- **Code Reviewer** - Software development assistance
- **Research Assistant** - Academic and scientific research
- **Tutor** - Educational content and explanations

## 🚀 Benefits of Dynamic Configuration

### ✅ **For Developers**
- **No code duplication** - One codebase, infinite configurations  
- **Easy maintenance** - All customization in YAML files
- **Version control friendly** - Track configuration changes easily
- **Testing simplified** - Test different configurations without code changes

### ✅ **For Businesses**  
- **Rapid deployment** - New use cases in minutes, not days
- **Client customization** - Deploy different versions per client
- **Cost effective** - One solution for multiple use cases
- **Future proof** - Add new AI capabilities through configuration

### ✅ **For Operations**
- **Configuration validation** - Built-in error checking
- **Hot reloading** - Update configurations without restarts
- **Security control** - Role-based access through configuration
- **Monitoring ready** - All configurations auditable

## 🔍 Troubleshooting

### Configuration Issues
```bash
# Validate configuration files
python config/config_validator.py

# Check if profiles load correctly
python -c "from config.config_loader import get_config_loader; print(list(get_config_loader().get_profiles().keys()))"
```

### Common Issues

1. **Profile not showing**: Check `requires_role` in profile configuration
2. **User can't login**: Verify user credentials in `config/auth.yaml`
3. **Promptflow errors**: Ensure Azure OpenAI credentials are correct
4. **Database connection**: Make sure PostgreSQL is running (`docker-compose up postgres`)

## 📚 Documentation

- **`README_DYNAMIC.md`** - Complete configuration system guide
- **`docs/DYNAMIC_CONFIGURATION.md`** - Detailed technical documentation  
- **`config/examples/`** - Ready-to-use configuration examples

## Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose** (for database)
- **Azure OpenAI** account and API credentials
- **Modern web browser**

## Platform Support

✅ **macOS** - Fully supported  
✅ **Windows** - Fully supported  
✅ **Linux** - Fully supported

## 🤝 Contributing

1. Fork the repository
2. Create configurations in `config/examples/` for new use cases
3. Update documentation for new features
4. Test with `python config/config_validator.py`
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

---

## 🎉 **Ready to Get Started?**

```bash
# Quick start in 3 commands:
cd chainlit-sample-db-chatprofile-promptflow-YAML
cp .env.example .env
# Edit .env with your Azure OpenAI credentials, then:
chainlit run app_dynamic.py
```

**Transform your AI application with the power of dynamic configuration!** 🚀


