# Dynamic Chainlit Configuration System

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment
```bash
cd chainlit-sample-db-chatprofile-promptflow-YAML
cp .env.example .env
```

### Step 2: Configure Credentials
Edit the generated `.env` file:
```bash
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2023-07-01-preview
```

### Step 3: Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Start Database (Optional)
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres
# Or use the convenience script
./run.sh  # macOS/Linux
# run-local.bat  # Windows
```

### Step 5: Start Application
```bash
chainlit run app_dynamic.py
# Or with custom port:
chainlit run app_dynamic.py --port 8000
```

### Step 6: Test Features
1. **Login**: Use `admin/admin123` or `user/user123` or `demo/demo123`
2. **Basic Chat**: Try "Assistant" profile
3. **Enhanced Chat**: Try "PromptFlow-Assistant" profile  
4. **Document Q&A**: Select "Document-QA" profile, upload a document and ask questions
5. **Role-Based Access**: Login as admin to see Technical and Business profiles

### 🎯 What You Get
- ✅ **7 Chat Profiles**: Assistant, Creative, Analytical, Technical, Business + Promptflow profiles
- ✅ **YAML Configuration**: All profiles defined in `config/profiles.yaml`
- ✅ **Role-Based Access**: Admin vs user permissions via `config/auth.yaml`
- ✅ **Persistent Chat**: All conversations saved to database
- ✅ **File Upload**: Document analysis with citations
- ✅ **Dynamic Configuration**: Add new profiles without code changes

### 🔧 Quick Troubleshooting

**Configuration validation:**
```bash
python config/config_validator.py
```

**Database issues:**
```bash
docker-compose up -d postgres
```

**Missing dependencies:**
```bash
pip install promptflow-azure promptflow[azure] azure-ai-ml azure-identity
```

**Test configuration loading:**
```bash
python -c "from config.config_loader import get_config_loader; print('✅ Configuration loaded successfully')"
```

---

A powerful, YAML-driven configuration system that makes your Chainlit application completely data-driven and reusable across multiple use cases without code duplication.

## 🎯 Overview

This dynamic configuration system transforms your Chainlit application from hardcoded profiles to a flexible, YAML-based approach where you can:

- **Define chat profiles in YAML** - No more hardcoded profile definitions
- **Configure authentication and roles** - Flexible user management
- **Set up promptflow integrations** - Dynamic flow execution
- **Customize model settings** - Per-profile model configurations
- **Add new use cases instantly** - Just edit YAML files, no code changes

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or navigate to the project
cd chainlit-sample-db-chatprofile-promptflow-YAML

# Update .env with your credentials
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Validate configuration (optional)
python config/config_validator.py

# Start the application
chainlit run app_dynamic.py
```

## 📁 Project Structure

```
chainlit-sample-db-chatprofile-promptflow-YAML/
├── 🔧 Configuration System
│   ├── config/
│   │   ├── profiles.yaml              # Chat profiles definition
│   │   ├── auth.yaml                  # Authentication & roles
│   │   ├── promptflows.yaml           # Promptflow configurations
│   │   ├── config_loader.py           # Configuration loader
│   │   ├── promptflow_executor.py     # Dynamic flow executor
│   │   ├── config_validator.py        # Validation utilities
│   │   └── examples/
│   │       └── custom_profiles.yaml   # Example configurations
│   │
├── 📱 Application
│   ├── app_dynamic.py                 # Main dynamic configuration app
│   │
├── 📚 Documentation
│   ├── README_DYNAMIC.md              # This file
│   ├── docs/DYNAMIC_CONFIGURATION.md  # Detailed usage guide
│   │
└── 🔄 Promptflows
    ├── promptflows/
    │   ├── chat_assistant/            # Enhanced chat flow
    │   └── document_qa/               # Document Q&A flow
```

## ⚙️ Configuration Files

### 1. Chat Profiles (`config/profiles.yaml`)

Define all your chat profiles with their behavior:

```yaml
profiles:
  # Standard profiles
  Assistant:
    name: "Assistant"
    markdown_description: "**General AI Assistant** - Helpful for everyday tasks"
    icon: "/public/icons/robot.svg"
    temperature: 0.7
    system_prompt: "You are a helpful AI assistant..."
    enabled: true
    requires_role: null  # Available to all users
    model_settings:
      max_tokens: 1000
      top_p: 1.0

  # Custom business profile
  CustomerSupport:
    name: "CustomerSupport"
    markdown_description: "**Customer Support** - Friendly customer service"
    icon: "/public/icons/support.svg"
    temperature: 0.5
    system_prompt: "You are a customer support assistant..."
    enabled: true
    requires_role: "support_agent"
    model_settings:
      max_tokens: 1200
      top_p: 0.9

# Promptflow-enhanced profiles
promptflow_profiles:
  Document-QA:
    name: "Document-QA"
    markdown_description: "**Document Q&A** - Upload and analyze documents"
    icon: "/public/icons/document.svg"
    temperature: 0.3
    system_prompt: "You are a document analysis assistant..."
    enabled: true
    requires_role: null
    requires_promptflow: true
    supports_file_upload: true
    flow_config:
      flow_path: "promptflows/document_qa"
      flow_type: "document_qa"
```

### 2. Authentication (`config/auth.yaml`)

Manage users, roles, and permissions:

```yaml
auth:
  enabled: true
  auth_type: "password"
  session_timeout: 3600

users:
  admin:
    password: "admin123"
    role: "admin"
    metadata:
      full_name: "Administrator"
      email: "admin@company.com"
    enabled: true

  support_user:
    password: "support123"
    role: "support_agent"
    metadata:
      full_name: "Support Agent"
      department: "Customer Service"
    enabled: true

roles:
  admin:
    description: "Administrator with full access"
    permissions:
      - "view_all_profiles"
      - "manage_users"
    profile_access:
      - "*"  # Access to all profiles

  support_agent:
    description: "Customer support agent"
    permissions:
      - "view_standard_profiles"
    profile_access:
      - "Assistant"
      - "CustomerSupport"
```

### 3. Promptflows (`config/promptflows.yaml`)

Configure advanced AI flows:

```yaml
promptflows:
  document_qa:
    name: "Document Q&A Flow"
    description: "Intelligent document analysis with citations"
    flow_path: "promptflows/document_qa"
    enabled: true
    inputs:
      - name: "question"
        type: "string"
        required: true
      - name: "document_content"
        type: "string"
        required: true

connections:
  Default_AzureOpenAI:
    type: "AzureOpenAI"
    api_base: "${AZURE_OPENAI_ENDPOINT}"
    api_key: "${AZURE_OPENAI_API_KEY}"
    api_version: "${AZURE_OPENAI_API_VERSION}"
    deployment_name: "${AZURE_OPENAI_DEPLOYMENT_NAME}"
```

## 🎮 Usage Examples

### Adding a New Use Case

**Scenario**: Add a "Legal Assistant" profile for law firms

1. **Add the profile** to `config/profiles.yaml`:
```yaml
profiles:
  Legal:
    name: "Legal"
    markdown_description: "**Legal Assistant** - Legal research and analysis"
    icon: "/public/icons/legal.svg"
    temperature: 0.2
    system_prompt: "You are a legal AI assistant specializing in legal research..."
    enabled: true
    requires_role: "lawyer"
    model_settings:
      max_tokens: 2500
      top_p: 0.85
```

2. **Add the role** to `config/auth.yaml`:
```yaml
roles:
  lawyer:
    description: "Legal professional"
    permissions:
      - "view_standard_profiles"
      - "access_legal_profile"
    profile_access:
      - "Assistant"
      - "Legal"

users:
  lawyer1:
    password: "legal123"
    role: "lawyer"
    metadata:
      full_name: "John Lawyer"
      bar_number: "12345"
    enabled: true
```

3. **Restart the application** - that's it! No code changes needed.

### Creating Custom Promptflows

1. **Create flow directory**: `promptflows/legal_research/`
2. **Add flow definition**: `flow.dag.yaml`
3. **Add Python modules**: `research.py`, `analyze.py`, etc.
4. **Update configuration**: Add to `config/promptflows.yaml`
5. **Create profile**: Reference the flow in `config/profiles.yaml`

## 🛠️ Development Workflow

### 1. Configuration Development

```bash
# Edit configurations
vim config/profiles.yaml
vim config/auth.yaml

# Validate changes
python config/config_validator.py

# Test loading
python -c "from config.config_loader import get_config_loader; print('OK')"

# Restart application
python start_dynamic.py
```

### 2. Adding New Features

```bash
# Create new profile type
cp config/examples/custom_profiles.yaml config/my_profiles.yaml
# Edit my_profiles.yaml

# Merge into main config
# Copy desired profiles to config/profiles.yaml

# Validate and test
python config/config_validator.py
python start_dynamic.py
```

### 3. Environment Management

```bash
# Development environment
cp .env.example .env.dev
# Edit .env.dev

# Production environment  
cp .env.example .env.prod
# Edit .env.prod

# Switch environments
cp .env.dev .env  # or .env.prod
```

## 🔧 Advanced Configuration

### Multi-tenant Setup

```yaml
# config/tenants.yaml
tenants:
  company_a:
    name: "Company A"
    profiles: ["Assistant", "CustomerSupport"]
    branding:
      logo: "/public/logos/company_a.png"
      theme: "blue"
  
  company_b:
    name: "Company B" 
    profiles: ["Assistant", "Technical", "Legal"]
    branding:
      logo: "/public/logos/company_b.png"
      theme: "green"
```

### Custom Model Settings

```yaml
profiles:
  HighCreativity:
    name: "HighCreativity"
    temperature: 1.2
    model_settings:
      max_tokens: 2000
      top_p: 0.95
      frequency_penalty: 0.5
      presence_penalty: 0.3
```

### Conditional Profiles

```yaml
profiles:
  BetaFeature:
    name: "BetaFeature"
    enabled: ${ENABLE_BETA_FEATURES}  # Environment variable
    requires_role: "beta_tester"
```

## 🧪 Testing & Validation

### Configuration Validation

```bash
# Validate all configurations
python config/config_validator.py

# Validate specific config
python config/config_validator.py config/

# Check environment variables
python -c "from config.config_validator import ConfigValidator; print(ConfigValidator().validate_environment_variables())"
```

### Integration Testing

```bash
# Test configuration loading
python -c "
from config.config_loader import get_config_loader
config = get_config_loader()
print(f'Profiles: {len(config.get_all_profiles())}')
print(f'Users: {len(config.get_auth_config().users)}')
"

# Test profile access
python -c "
from config.config_loader import get_config_loader
config = get_config_loader()
profiles = config.get_profiles_for_user('admin', True)
print(f'Admin has access to: {list(profiles.keys())}')
"
```

### Application Testing

```bash
# Start with validation
python start_dynamic.py

# Start without validation (faster)
python app_dynamic.py

# Test specific profile
chainlit run app_dynamic.py --profile Technical
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**:
```bash
# Production .env
AZURE_OPENAI_API_KEY=prod_key_here
AZURE_OPENAI_ENDPOINT=https://prod-resource.openai.azure.com/
DATABASE_URL=postgresql://prod_db_url
ENVIRONMENT=production
```

2. **Security Hardening**:
```yaml
# config/auth.yaml
security:
  password_min_length: 12
  enable_rate_limiting: true
  max_login_attempts: 3
  lockout_duration: 900
  session_token_expiry: 3600
```

3. **Performance Optimization**:
```yaml
# config/profiles.yaml
settings:
  default_model_settings:
    max_tokens: 1000  # Reasonable default
    temperature: 0.7
  enable_caching: true
  cache_ttl: 3600
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Validate configuration on build
RUN python config/config_validator.py

CMD ["python", "start_dynamic.py"]
```

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chainlit-dynamic
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chainlit-dynamic
  template:
    metadata:
      labels:
        app: chainlit-dynamic
    spec:
      containers:
      - name: chainlit
        image: chainlit-dynamic:latest
        env:
        - name: AZURE_OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: azure-openai-secret
              key: api-key
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
      volumes:
      - name: config-volume
        configMap:
          name: chainlit-config
```

## 🔍 Troubleshooting

### Common Issues

1. **Profile not appearing**:
```bash
# Check if enabled
grep -A 5 "ProfileName:" config/profiles.yaml

# Check user role access
python -c "
from config.config_loader import get_config_loader
config = get_config_loader()
print(config.get_profiles_for_user('your_role', True))
"
```

2. **Authentication failing**:
```bash
# Validate credentials
python -c "
from config.config_loader import get_config_loader
config = get_config_loader()
print(config.validate_user_credentials('username', 'password'))
"
```

3. **Promptflow errors**:
```bash
# Check flow configuration
python config/config_validator.py

# Test flow execution
python -c "
from config.promptflow_executor import get_promptflow_executor
executor = get_promptflow_executor()
print(executor.list_available_flows())
"
```

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from config.config_loader import get_config_loader
config = get_config_loader()
"
```

## 📚 Resources

- **[Detailed Configuration Guide](docs/DYNAMIC_CONFIGURATION.md)** - Complete usage documentation
- **[Example Configurations](config/examples/)** - Ready-to-use profile examples
- **[Migration Guide](migrate_to_dynamic.py)** - Automated migration from hardcoded version
- **[Validation Tools](config/config_validator.py)** - Configuration validation utilities

## 🤝 Contributing

1. **Add new profile types** to `config/examples/`
2. **Improve validation** in `config/config_validator.py`
3. **Enhance documentation** in `docs/`
4. **Create new promptflows** in `promptflows/`

## 📄 License

This project maintains the same license as the original Chainlit sample.

---

**🎉 Congratulations!** You now have a completely dynamic, data-driven Chainlit application that can be customized for any use case without touching a single line of code. Just edit YAML files and restart! 