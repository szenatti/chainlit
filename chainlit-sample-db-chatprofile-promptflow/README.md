# Chainlit Application with Chat Profiles, Authentication, Data Persistence and Promptflow Integration

This is an enhanced chat application built using Chainlit, Azure OpenAI, and **Azure Promptflow** that works seamlessly on **macOS**, **Windows**, and **Linux** with the following features:

- **Chat Profiles**: Multiple AI personalities with different capabilities and specializations
- **Password Authentication**: Secure login system with role-based access
- **Chat History**: Persistent chat conversations with resume capability
- **Human Feedback**: Thumbs up/down rating system with comments
- **SQLAlchemy Data Layer**: PostgreSQL database integration
- **Docker Support**: Easy local deployment with Docker Compose
- **🆕 Promptflow Integration**: Two advanced AI workflows using Azure Promptflow
  - **Enhanced Chat Assistant**: Advanced conversational AI with sophisticated prompt engineering
  - **Document Q&A**: Upload documents and get intelligent answers with citations and relevance scoring

## 🚀 New Promptflow Features

### 1. Promptflow Chat Assistant
- **Advanced Prompt Engineering**: Sophisticated system prompts tailored for each chat profile
- **Context Management**: Intelligent handling of conversation history
- **Flow Orchestration**: Multi-step processing for enhanced responses
- **Profile-Specific Responses**: Customized AI behavior based on selected profile

### 2. Document Q&A with Promptflow
- **Document Upload**: Support for text file uploads or direct content pasting
- **Intelligent Chunking**: Automatic document preprocessing and segmentation
- **Context Extraction**: Smart retrieval of relevant document sections
- **Relevance Scoring**: AI-powered assessment of answer quality and relevance
- **Source Citations**: Automatic generation of source references and citations
- **Multi-step Analysis**: Document preprocessing → Context extraction → Answer generation → Quality assessment

## Features

### 👥 Chat Profiles

**Standard Profiles (All Users):**
- 🤖 **Assistant**: General-purpose AI for everyday tasks and questions
- 🎨 **Creative**: Enhanced creativity for storytelling and artistic content  
- 📊 **Analytical**: Logical, structured responses for data analysis and problem-solving

**🆕 Promptflow-Enhanced Profiles:**
- 🔄 **PromptFlow-Assistant**: Advanced chat responses using Azure Promptflow orchestration
- 📄 **Document-QA**: Upload documents and ask questions using Promptflow document analysis

**Admin-Only Profiles:**
- ⚙️ **Technical**: Advanced technical discussions, coding, and system architecture
- 💼 **Business**: Strategic business advice and professional guidance

### 🔐 Authentication
- Password-based authentication system with role-based access control
- User session management with profile preferences
- Multiple user accounts support (admin/user roles)

### 💾 Data Persistence
- Chat history stored in PostgreSQL database
- Resume previous conversations with profile context
- Human feedback collection (thumbs up/down with comments)
- SQLAlchemy ORM integration

### 🐳 Docker Support
- Containerized application
- PostgreSQL database container
- Docker Compose for easy setup

## Prerequisites

- **Docker and Docker Compose** installed
- An **Azure account** with access to Azure OpenAI
- **Azure OpenAI resource** provisioned with a model deployment
- **Python 3.9+** for local development

## Platform Support

✅ **macOS** - Fully supported  
✅ **Windows** - Fully supported  
✅ **Linux** - Fully supported

## Quick Start (Recommended: Local App + Docker PostgreSQL)

This setup runs the Chainlit application locally while using Docker only for the PostgreSQL database.

1. **Clone and navigate to the directory**:
   ```bash
   cd chainlit-sample-db-chatprofile-promptflow
   ```

2. **Run the setup script** (creates .env and starts database):
   
   **On macOS/Linux:**
   ```bash
   ./run-local.sh
   ```
   
   **On Windows:**
   ```cmd
   run-local.bat
   ```

3. **Configure your Azure OpenAI credentials** in the generated `.env` file:
   ```bash
   # Edit these values in .env
   AZURE_OPENAI_API_KEY=your_actual_api_key
   AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
   AZURE_OPENAI_API_VERSION=2023-07-01-preview
   ```

4. **Set up Python environment**:
   
   **On macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   
   **On Windows (Command Prompt):**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   chainlit run app.py
   ```

6. **Access the application**:
   - Open your web browser and go to [http://localhost:8000](http://localhost:8000)
   - Use one of the demo credentials to login:
     - Username: `admin`, Password: `admin123`
     - Username: `user`, Password: `user123`
     - Username: `demo`, Password: `demo123`

## 🔄 Using Promptflow Features

### Enhanced Chat Assistant
1. Select the **"PromptFlow-Assistant"** profile after logging in
2. Start chatting - your messages will be processed through the advanced promptflow pipeline
3. Experience enhanced responses with sophisticated prompt engineering and context management

### Document Q&A
1. Select the **"Document-QA"** profile after logging in
2. Upload a document by:
   - Clicking the attachment button and selecting a text file
   - Or pasting document content directly in your message
3. Ask questions about the document content
4. Receive answers with:
   - **Relevance scoring** showing how well the answer matches your question
   - **Source citations** indicating which parts of the document were used
   - **Context grounding** showing how the answer relates to the document

### Sample Questions for Document Q&A
Try uploading the sample document (`sample_documents/sample_company_policy.txt`) and ask:
- "What is the remote work policy?"
- "How many vacation days do employees get?"
- "What are the health insurance benefits?"
- "When are performance reviews conducted?"

## 📁 Project Structure

```
chainlit-sample-db-chatprofile-promptflow/
├── app.py                          # Main Chainlit application
├── promptflow_config.py            # Promptflow configuration
├── requirements.txt                # Python dependencies
├── promptflows/                    # Promptflow definitions
│   ├── chat_assistant/            # Enhanced chat assistant flow
│   │   ├── flow.dag.yaml         # Flow definition
│   │   ├── prepare_prompt.py     # Prompt preparation logic
│   │   ├── llm_prompt.jinja2     # LLM prompt template
│   │   ├── format_response.py    # Response formatting
│   │   └── requirements.txt      # Flow-specific dependencies
│   └── document_qa/               # Document Q&A flow
│       ├── flow.dag.yaml         # Flow definition
│       ├── preprocess_document.py # Document preprocessing
│       ├── extract_context.py    # Context extraction
│       ├── qa_prompt.jinja2      # Q&A prompt template
│       ├── calculate_relevance.py # Relevance scoring
│       ├── extract_sources.py    # Source citation
│       └── requirements.txt      # Flow-specific dependencies
├── sample_documents/              # Sample documents for testing
│   └── sample_company_policy.txt # Sample company policy document
├── docker-compose.yml            # Docker services configuration
├── init.sql                      # Database initialization
└── README.md                     # This file
```

## 🛠️ Promptflow Development

### Understanding the Flows

#### Chat Assistant Flow (`promptflows/chat_assistant/`)
1. **prepare_prompt.py**: Processes chat history and profile settings to create optimized prompts
2. **llm_prompt.jinja2**: Template for structuring the LLM request
3. **format_response.py**: Adds profile-specific formatting and citations

#### Document Q&A Flow (`promptflows/document_qa/`)
1. **preprocess_document.py**: Cleans and chunks the document content
2. **extract_context.py**: Finds relevant document sections based on the question
3. **qa_prompt.jinja2**: Template for document-based question answering
4. **calculate_relevance.py**: Scores the relevance of the generated answer
5. **extract_sources.py**: Generates citations and source references

### Customizing Flows

To modify the promptflow behaviors:

1. **Edit the Python functions** in each flow directory to change processing logic
2. **Modify the Jinja2 templates** to adjust prompt structures
3. **Update flow.dag.yaml** to change the flow orchestration
4. **Test locally** using the Promptflow CLI:
   ```bash
   pf flow test --flow ./promptflows/chat_assistant --inputs question="Hello"
   ```

## Environment Variables

### Required Azure OpenAI Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_API_VERSION`: API version (default: 2023-07-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your model deployment name

### Optional Database Variables
- `DATABASE_URL`: PostgreSQL connection string (default: local Docker instance)

## User Accounts

The application comes with pre-configured demo accounts:

| Username | Password  | Role  | Access |
|----------|-----------|-------|--------|
| admin    | admin123  | admin | All profiles including Technical & Business |
| user     | user123   | user  | Standard + Promptflow profiles |
| demo     | demo123   | user  | Standard + Promptflow profiles |

> **⚠️ Security Warning**: These are demo credentials. In production, implement proper password hashing and user management.

## Troubleshooting

### Promptflow Issues

1. **"Promptflow not available" warning**:
   ```bash
   pip install promptflow-azure promptflow[azure]
   ```

2. **Flow execution errors**:
   - Check that all environment variables are set correctly
   - Verify Azure OpenAI deployment name matches your actual deployment
   - Ensure the flow files are in the correct directory structure

3. **Document upload issues**:
   - Supported file types: .txt, .md, .csv
   - Maximum file size: 10MB
   - Ensure the file contains readable text content

### General Issues

1. **Database connection errors**:
   ```bash
   docker-compose up postgres  # Start only the database
   ```

2. **Azure OpenAI authentication errors**:
   - Verify your API key and endpoint in the `.env` file
   - Check that your deployment name is correct
   - Ensure your Azure OpenAI resource has the required model deployed

## 🔧 Development and Testing

### Running Tests
```bash
# Test promptflow flows individually
pf flow test --flow ./promptflows/chat_assistant --inputs question="Hello" profile_name="Assistant"
pf flow test --flow ./promptflows/document_qa --inputs question="What is this about?" document_content="Sample content"

# Test the full application
chainlit run app.py
```

### Adding New Flows
1. Create a new directory under `promptflows/`
2. Add the required files: `flow.dag.yaml`, Python functions, and templates
3. Update `app.py` to integrate the new flow
4. Add a new chat profile in the `chat_profile()` function

## 📚 Additional Resources

- [Azure Promptflow Documentation](https://microsoft.github.io/promptflow/)
- [Chainlit Documentation](https://docs.chainlit.io/)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with both standard and promptflow profiles
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.


