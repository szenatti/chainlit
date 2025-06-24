# Chainlit Solutions Collection

A comprehensive collection of **6 progressive Chainlit applications** showcasing different levels of complexity and features, from basic chat to enterprise-ready solutions with advanced document search and dynamic configuration systems.

## 🎯 Overview

This repository demonstrates the evolution of Chainlit applications, starting from a simple chat interface and progressing to sophisticated, enterprise-ready solutions with advanced features like authentication, database persistence, chat profiles, AI workflows, intelligent document search, and dynamic YAML-driven configurations.

## 📁 Solutions Overview

### 1. [🤖 Basic Chainlit App](./chainlit-sample/)
**The Foundation - Simple Chat Interface**

A straightforward chat application using Chainlit and Azure OpenAI, perfect for getting started.

**Features:**
- ✅ Simple chat interface with Azure OpenAI
- ✅ Cross-platform support (macOS, Windows, Linux)
- ✅ Environment variable configuration
- ✅ Virtual environment setup

**Best for:** Learning Chainlit basics, proof of concepts, simple chatbots

---

### 2. [🔐 Chainlit with Database](./chainlit-sample-db/)
**Adding Persistence - Authentication & Data Storage**

Enhanced version with user authentication and persistent chat history using PostgreSQL.

**Features:**
- ✅ **Password-based authentication** with demo accounts
- ✅ **PostgreSQL database integration** with SQLAlchemy
- ✅ **Persistent chat history** - resume conversations
- ✅ **Human feedback collection** - thumbs up/down with comments
- ✅ **Docker support** for easy deployment
- ✅ **Cross-platform compatibility**

**Best for:** Applications requiring user management, chat history, and feedback collection

---

### 3. [👥 Chainlit with Chat Profiles](./chainlit-sample-db-chatprofile/)
**Multiple AI Personalities - Specialized Assistants**

Adds multiple AI personalities with role-based access and specialized capabilities.

**Features:**
- ✅ **5 Specialized Chat Profiles:**
  - 🤖 Assistant (General purpose)
  - 🎨 Creative (Storytelling & artistic)
  - 📊 Analytical (Data analysis & logic)
  - ⚙️ Technical (Admin only - coding & architecture)
  - 💼 Business (Admin only - strategic advice)
- ✅ **Role-based access control** (admin vs user profiles)
- ✅ **Profile-specific system prompts** and temperature settings
- ✅ **All database and authentication features** from solution #2

**Best for:** Multi-purpose applications, different AI personalities, role-based user access

---

### 4. [🔄 Chainlit with Promptflow Integration](./chainlit-sample-db-chatprofile-promptflow/)
**Advanced AI Workflows - Enterprise Features**

Integrates Azure Promptflow for sophisticated AI workflows and document analysis capabilities.

**Features:**
- ✅ **Azure Promptflow integration** with advanced AI workflows
- ✅ **Enhanced Chat Assistant** - multi-step AI processing
- ✅ **Document Q&A system:**
  - Upload documents or paste content
  - Intelligent document chunking
  - Context extraction and relevance scoring
  - Source citations and references
- ✅ **Advanced prompt engineering** with flow orchestration
- ✅ **All chat profiles and database features** from solution #3

**Best for:** Enterprise applications, document analysis, advanced AI workflows, complex use cases

---

### 5. [⚙️ Dynamic YAML-Driven Chainlit](./chainlit-sample-db-chatprofile-promptflow-YAML/)
**🌟 Revolutionary Configuration System - Zero-Code Customization**

The most advanced solution featuring a **complete YAML-based configuration system** that eliminates the need for code changes when adding new features.

**🚀 Revolutionary Features:**
- ✅ **100% Configuration-Driven Architecture**
  - Add new chat profiles without code changes
  - Configure users, roles, and permissions via YAML
  - Set up AI workflows through configuration
- ✅ **Dynamic Configuration Files:**
  - `config/profiles.yaml` - Chat profile definitions
  - `config/auth.yaml` - User management and roles
  - `config/promptflows.yaml` - AI workflow configurations
- ✅ **Built-in Configuration Validation** with error handling
- ✅ **Instant Deployment** of new AI personalities
- ✅ **All enterprise features** from solution #4

**Best for:** Enterprise solutions, multi-tenant applications, rapid deployment, maintenance-free scaling

---

### 6. [🔍 Azure AI Search Assistant](./chainlit-sample-azure-ai-search/)
**🌟 Intelligent Document Search & Enterprise Security**

A production-ready Azure AI Search integration with enterprise-grade authentication, in-app document viewers, and seamless citation system.

**🚀 Advanced Features:**
- ✅ **Azure AI Search Integration** - Intelligent document retrieval with semantic/hybrid search
- ✅ **Enterprise Authentication** - Service Principal, Storage Account Key, and Managed Identity support
- ✅ **Smart Citation System** - Token-embedded URLs for secure document access
- ✅ **Advanced Document Viewers:**
  - PDF viewer with page navigation, zoom, print
  - Word documents rendered as formatted HTML
  - Excel/CSV interactive tables with sorting
  - Markdown formatted text with syntax highlighting
  - Images & videos with native preview
  - 10+ file types supported
- ✅ **Folder Structure Support** - Handles nested blob storage organization
- ✅ **Dual Architecture Options:**
  - Simple Chainlit app for development
  - Full FastAPI + Chainlit integration for production
- ✅ **Production-Ready Security:**
  - JWT-based API authentication
  - Document-level authorization
  - Range request support for large files
  - Comprehensive audit logging

**Best for:** Knowledge base applications, document search systems, enterprise deployments requiring secure document access with advanced viewers

## 🚀 Getting Started

### Prerequisites
- **Python 3.9+**
- **Azure OpenAI account** with API access
- **Docker & Docker Compose** (for database solutions)

### Quick Start Guide

1. **Choose your solution** based on your needs:
   - **Learning/Simple**: Start with [chainlit-sample](./chainlit-sample/)
   - **Need persistence**: Try [chainlit-sample-db](./chainlit-sample-db/)
   - **Multiple AI types**: Use [chainlit-sample-db-chatprofile](./chainlit-sample-db-chatprofile/)
   - **Enterprise features**: Go with [chainlit-sample-db-chatprofile-promptflow](./chainlit-sample-db-chatprofile-promptflow/)
   - **Maximum flexibility**: Choose [chainlit-sample-db-chatprofile-promptflow-YAML](./chainlit-sample-db-chatprofile-promptflow-YAML/)
   - **Document search & enterprise security**: Use [chainlit-sample-azure-ai-search](./chainlit-sample-azure-ai-search/)

2. **Navigate to the chosen solution directory**
3. **Follow the specific README** in that directory
4. **Configure your Azure OpenAI credentials**
5. **Run the application**

## 📊 Feature Comparison Matrix

| Feature | Basic | +Database | +Profiles | +Promptflow | +YAML Config | +AI Search |
|---------|-------|-----------|-----------|-------------|-------------|------------|
| **Basic Chat** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Authentication** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Chat History** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Human Feedback** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Database Integration** | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Multiple AI Profiles** | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ |
| **Role-Based Access** | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Document Q&A** | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Promptflow Integration** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **YAML Configuration** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Zero-Code Scaling** | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **Azure AI Search** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Document Viewers** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Enterprise Security** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Citation System** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

## 🎯 Use Case Recommendations

### 🎓 **Learning & Development**
- **Start with:** [chainlit-sample](./chainlit-sample/)
- **Progress to:** [chainlit-sample-db](./chainlit-sample-db/)

### 🏢 **Small Business Applications**
- **Recommended:** [chainlit-sample-db-chatprofile](./chainlit-sample-db-chatprofile/)
- **Benefits:** Multiple AI assistants, user management, chat history

### 🏛️ **Enterprise Solutions**
- **Recommended:** [chainlit-sample-db-chatprofile-promptflow-YAML](./chainlit-sample-db-chatprofile-promptflow-YAML/)
- **Benefits:** Maximum flexibility, zero-code scaling, advanced AI workflows

### 🔬 **Research & Document Analysis**
- **Recommended:** [chainlit-sample-db-chatprofile-promptflow](./chainlit-sample-db-chatprofile-promptflow/)
- **Benefits:** Document Q&A, advanced AI workflows, citation tracking

### 🏢 **Knowledge Base & Document Search**
- **Recommended:** [chainlit-sample-azure-ai-search](./chainlit-sample-azure-ai-search/)
- **Benefits:** Intelligent search, secure document access, enterprise authentication, in-app viewers

## 🛠️ Technical Architecture

### Progressive Complexity
1. **Basic** → Simple Chainlit + Azure OpenAI
2. **+Database** → Adds PostgreSQL, SQLAlchemy, Authentication
3. **+Profiles** → Adds multiple AI personalities, role-based access
4. **+Promptflow** → Adds Azure Promptflow, document analysis
5. **+YAML Config** → Adds dynamic configuration system
6. **+AI Search** → Adds Azure AI Search, enterprise security, document viewers

### Common Technologies
- **Frontend:** Chainlit (Python-based web interface)
- **Backend:** FastAPI (integrated with Chainlit)
- **AI:** Azure OpenAI (GPT models)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Deployment:** Docker & Docker Compose
- **Advanced AI:** Azure Promptflow (solutions 4-5)
- **Configuration:** YAML-based (solution 5)
- **Search & Storage:** Azure AI Search + Azure Blob Storage (solution 6)
- **Security:** JWT authentication, Service Principal, Managed Identity (solution 6)

## 🔧 Development & Deployment

### Development Environment Setup
Each solution includes detailed setup instructions, but the general pattern is:

```bash
# 1. Navigate to chosen solution
cd chainlit-sample-[variant]

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 5. Start database (if applicable)
./run-local.sh  # or docker-compose up -d postgres

# 6. Run application
chainlit run app.py
```

### Production Deployment
- **Docker Compose** configurations included
- **Environment variable** management
- **Database migration** scripts provided
- **Health check** utilities included

## 📚 Additional Resources

### Documentation
- Each solution has comprehensive **README.md** with setup instructions
- **QUICKSTART.md** files for rapid deployment
- **Configuration examples** and templates
- **API documentation** and usage guides

### Sample Data
- **Demo user accounts** for testing
- **Sample documents** for Q&A testing
- **Configuration examples** for customization
- **SQL initialization** scripts

## 🤝 Contributing

This collection demonstrates various approaches to building Chainlit applications. Feel free to:
- **Use as templates** for your own projects
- **Extend functionality** based on your needs
- **Contribute improvements** and optimizations
- **Share your own variations** and use cases

## 📄 License

This project is licensed under the **MIT License** - see individual solution directories for specific license details.

---

**Created by Sergio Zenatti Filho**  
Showcasing the evolution from simple chat to enterprise-ready AI applications with Chainlit. 