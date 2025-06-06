# Dynamic Configuration System

This document explains how to use the YAML-based dynamic configuration system for the Chainlit application.

## Overview

The dynamic configuration system allows you to:
- Define chat profiles in YAML files
- Configure authentication and user roles
- Set up promptflow integrations
- Customize model settings
- Add new use cases without code changes

## Configuration Files

### 1. Profiles Configuration (`config/profiles.yaml`)

Defines all chat profiles and their behavior:

```yaml
profiles:
  MyCustomProfile:
    name: "MyCustomProfile"
    markdown_description: "**Custom Profile** - Description of what this profile does."
    icon: "/public/icons/custom.svg"
    temperature: 0.7
    system_prompt: "You are a custom AI assistant..."
    enabled: true
    requires_role: null  # or specific role like "admin"
    model_settings:
      max_tokens: 1000
      top_p: 1.0

promptflow_profiles:
  MyPromptflowProfile:
    name: "MyPromptflowProfile"
    markdown_description: "**Promptflow Profile** - Uses custom promptflow."
    icon: "/public/icons/flow.svg"
    temperature: 0.5
    system_prompt: "You are a promptflow-powered assistant..."
    enabled: true
    requires_role: null
    requires_promptflow: true
    supports_file_upload: true  # For document processing
    flow_config:
      flow_path: "promptflows/my_custom_flow"
      flow_type: "my_custom_flow"
    model_settings:
      max_tokens: 1500
      top_p: 0.9
```

### 2. Authentication Configuration (`config/auth.yaml`)

Manages users, roles, and authentication:

```yaml
auth:
  enabled: true
  auth_type: "password"
  session_timeout: 3600

users:
  myuser:
    password: "mypassword"
    role: "user"
    metadata:
      full_name: "My User"
      email: "user@example.com"
    enabled: true

roles:
  user:
    description: "Standard user"
    permissions:
      - "view_standard_profiles"
    profile_access:
      - "Assistant"
      - "Creative"
      - "MyCustomProfile"
  
  admin:
    description: "Administrator"
    permissions:
      - "view_all_profiles"
      - "manage_users"
    profile_access:
      - "*"  # Access to all profiles
```

### 3. Promptflow Configuration (`config/promptflows.yaml`)

Defines promptflow integrations:

```yaml
promptflows:
  my_custom_flow:
    name: "My Custom Flow"
    description: "Custom business logic flow"
    flow_path: "promptflows/my_custom_flow"
    flow_file: "flow.dag.yaml"
    enabled: true
    inputs:
      - name: "question"
        type: "string"
        required: true
      - name: "context"
        type: "string"
        required: false
    outputs:
      - name: "answer"
        type: "string"
        description: "Generated response"

connections:
  Default_AzureOpenAI:
    type: "AzureOpenAI"
    api_base: "${AZURE_OPENAI_ENDPOINT}"
    api_key: "${AZURE_OPENAI_API_KEY}"
    api_version: "${AZURE_OPENAI_API_VERSION}"
    deployment_name: "${AZURE_OPENAI_DEPLOYMENT_NAME}"
```

## Creating New Use Cases

### Step 1: Define Your Profile

Create or modify `config/profiles.yaml`:

```yaml
profiles:
  # Your new use case
  DataAnalyst:
    name: "DataAnalyst"
    markdown_description: "**Data Analyst** - Specialized in data analysis and visualization."
    icon: "/public/icons/data.svg"
    temperature: 0.3
    system_prompt: "You are a data analyst AI assistant. Help users with data analysis, statistics, and creating insights from data."
    enabled: true
    requires_role: "analyst"
    model_settings:
      max_tokens: 2000
      top_p: 0.9
```

### Step 2: Configure User Access

Update `config/auth.yaml`:

```yaml
roles:
  analyst:
    description: "Data analyst role"
    permissions:
      - "view_standard_profiles"
      - "access_data_tools"
    profile_access:
      - "Assistant"
      - "DataAnalyst"

users:
  data_user:
    password: "analyst123"
    role: "analyst"
    metadata:
      full_name: "Data User"
      department: "Analytics"
    enabled: true
```

### Step 3: (Optional) Create Custom Promptflow

If you need advanced processing, create a promptflow:

1. Create directory: `promptflows/data_analysis/`
2. Add `flow.dag.yaml`
3. Add Python modules for processing
4. Update `config/promptflows.yaml`

### Step 4: Test Your Configuration

```bash
# Validate configuration
python config/config_validator.py

# Start the application
python app_dynamic.py
```

## Profile Configuration Options

### Basic Settings

- `name`: Display name for the profile
- `markdown_description`: Rich description shown in UI
- `icon`: Path to icon file (in public directory)
- `temperature`: Model creativity (0.0-2.0)
- `system_prompt`: Instructions for the AI
- `enabled`: Whether profile is active

### Access Control

- `requires_role`: Specific role required (null = all users)
- `requires_promptflow`: Whether promptflow is needed

### Advanced Features

- `supports_file_upload`: Enable file uploads
- `flow_config`: Promptflow integration settings
- `model_settings`: Custom model parameters

### Model Settings

```yaml
model_settings:
  max_tokens: 1500      # Maximum response length
  top_p: 0.9           # Nucleus sampling parameter
  temperature: 0.7     # Override profile temperature
```

## Environment Variables

Required environment variables:

```bash
# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-07-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Database (optional)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
```

## File Structure

```
config/
├── profiles.yaml           # Chat profiles
├── auth.yaml              # Authentication
├── promptflows.yaml       # Promptflow configs
├── config_loader.py       # Configuration loader
├── promptflow_executor.py # Dynamic executor
├── config_validator.py    # Validation utility
└── examples/
    └── custom_profiles.yaml # Example configurations

promptflows/
├── chat_assistant/        # Basic chat flow
├── document_qa/          # Document Q&A flow
└── my_custom_flow/       # Your custom flows

public/
└── icons/                # Profile icons
```

## Validation

Always validate your configuration:

```bash
# Validate all configs
python config/config_validator.py

# Validate specific directory
python config/config_validator.py config/

# Check environment variables
python -c "from config.config_validator import ConfigValidator; print(ConfigValidator.validate_environment_variables())"
```

## Hot Reloading

To reload configuration without restarting:

```python
from config.config_loader import reload_config
reload_config()
```

## Best Practices

### 1. Profile Naming
- Use clear, descriptive names
- Follow PascalCase convention
- Avoid special characters

### 2. Icon Management
- Store icons in `public/icons/`
- Use SVG format for scalability
- Keep icons under 50KB

### 3. Temperature Settings
- `0.0-0.3`: Factual, deterministic
- `0.4-0.7`: Balanced creativity
- `0.8-1.0`: Creative, varied
- `1.0+`: Highly creative/random

### 4. Security
- Use environment variables for secrets
- Hash passwords in production
- Implement proper RBAC

### 5. Model Settings
- Set appropriate `max_tokens` for use case
- Use `top_p` for fine-tuning creativity
- Monitor token usage and costs

## Troubleshooting

### Common Issues

1. **Profile not appearing**
   - Check `enabled: true`
   - Verify user has required role
   - Validate YAML syntax

2. **Promptflow errors**
   - Ensure flow path exists
   - Check flow.dag.yaml syntax
   - Verify environment variables

3. **Authentication failing**
   - Check user credentials in auth.yaml
   - Verify role assignments
   - Ensure auth is enabled

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Configuration Testing

Test individual components:

```python
from config.config_loader import get_config_loader

config = get_config_loader()
print(config.get_all_profiles())
print(config.get_auth_config())
print(config.validate_user_credentials("user", "pass"))
```

## Migration Guide

### From Hardcoded to Dynamic

1. **Extract current profiles** to `config/profiles.yaml`
2. **Move user data** to `config/auth.yaml`
3. **Configure promptflows** in `config/promptflows.yaml`
4. **Update app.py** to use `app_dynamic.py`
5. **Test thoroughly** with validation

### Version Compatibility

- Maintains backward compatibility
- Graceful fallbacks for missing configs
- Environment variable precedence preserved

## Advanced Usage

### Custom Profile Types

Create specialized profile types:

```yaml
profiles:
  APITester:
    name: "APITester"
    # ... other settings
    custom_settings:
      api_endpoints:
        - "https://api.example.com"
      rate_limits:
        requests_per_minute: 60
```

### Multi-tenant Configuration

Support multiple organizations:

```yaml
tenants:
  org1:
    profiles: ["Assistant", "Creative"]
    branding:
      logo: "/public/logos/org1.png"
      theme: "blue"
  org2:
    profiles: ["Technical", "Business"]
    branding:
      logo: "/public/logos/org2.png"
      theme: "green"
```

### Dynamic Flow Generation

Generate flows from templates:

```yaml
flow_templates:
  standard_qa:
    template_path: "templates/qa_template.yaml"
    parameters:
      domain: "medical"
      max_context_length: 2000
```

This dynamic configuration system provides the flexibility to adapt the Chainlit application to any use case without modifying code, making it truly reusable and maintainable. 