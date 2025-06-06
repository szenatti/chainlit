# Chainlit Application with Authentication and Data Persistence

This is an enhanced chat application built using Chainlit and Azure OpenAI that works seamlessly on **macOS**, **Windows**, and **Linux** with the following features:

- **Password Authentication**: Secure login system
- **Chat History**: Persistent chat conversations with resume capability
- **Human Feedback**: Thumbs up/down rating system with comments
- **SQLAlchemy Data Layer**: PostgreSQL database integration
- **Docker Support**: Easy local deployment with Docker Compose

## Features

### 🔐 Authentication
- Password-based authentication system
- User session management
- Multiple user accounts support

### 💾 Data Persistence
- Chat history stored in PostgreSQL database
- Resume previous conversations
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

## Platform Support

✅ **macOS** - Fully supported  
✅ **Windows** - Fully supported  
✅ **Linux** - Fully supported

## Quick Start (Recommended: Local App + Docker PostgreSQL)

This setup runs the Chainlit application locally while using Docker only for the PostgreSQL database.

1. **Clone and navigate to the directory**:
   ```bash
   cd chainlit-sample-db
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
   
   *Note: If you don't have the Windows batch file, you can run the commands manually (see Manual Setup section)*

3. **Configure your Azure OpenAI credentials** in the generated `.env` file:
   ```bash
   # Edit these values in .env
   AZURE_OPENAI_API_KEY=your_actual_api_key
   AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
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
   
   **On Windows (PowerShell):**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
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

## Alternative: Full Docker Setup

If you prefer to run everything in Docker containers:

1. **Start both services**:
   ```bash
   # Restore the chainlit service in docker-compose.yml first
   docker-compose up --build
   ```

## Manual Setup (without any Docker)

### Prerequisites
- Python 3.11+ installed
- PostgreSQL database server installed and running locally

### Installation Steps

1. **Create and activate a virtual environment**:
   
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

2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database**:
   - Install PostgreSQL server locally
   - Create a database named `chainlit_db`
   - Run the SQL script from `init.sql` to create the required tables:
     ```bash
     psql -U postgres -d chainlit_db -f init.sql
     ```

4. **Configure environment variables**:
   - Create a `.env` file with your credentials:
     ```bash
     DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/chainlit_db
     AZURE_OPENAI_API_KEY=your_api_key
     AZURE_OPENAI_ENDPOINT=https://your_resource.openai.azure.com/
     AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
     ```

5. **Run the application**:
   ```bash
   chainlit run app.py
   ```

## User Accounts

The application comes with pre-configured demo accounts:

| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| user     | user123   | user  |
| demo     | demo123   | user  |

> **⚠️ Security Warning**: These are demo credentials. In production, implement proper password hashing and user management.

## Features Usage

### Chat History
- After authentication, all your conversations are automatically saved
- Access previous conversations through the sidebar
- Resume any previous conversation seamlessly

### Human Feedback
- Rate AI responses with thumbs up/down icons
- Add optional text comments for detailed feedback
- Feedback is stored for analysis and improvement

### Authentication
- Login required to access the chat
- User sessions are maintained
- Personalized welcome messages

## Database Schema

The application uses the following PostgreSQL tables:

- `users`: Store user information and metadata
- `threads`: Chat conversation threads
- `steps`: Individual messages and steps in conversations
- `elements`: File attachments and media elements
- `feedbacks`: User feedback on AI responses

## Docker Services

The Docker Compose setup includes:

- **chainlit**: The main application container
- **postgres**: PostgreSQL database container
- **postgres_data**: Persistent volume for database storage

## Environment Variables

### Required Azure OpenAI Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI service endpoint
- `AZURE_OPENAI_API_VERSION`: API version (default: 2023-07-01-preview)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your model deployment name

### Database Variables
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_USER`: Database username (Docker only)
- `POSTGRES_PASSWORD`: Database password (Docker only)
- `POSTGRES_DB`: Database name (Docker only)

## Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure PostgreSQL is running
   - Check database credentials in `.env`
   - Verify database exists and tables are created

2. **Azure OpenAI Authentication Error**:
   - Verify API key is correct
   - Check endpoint URL format
   - Ensure deployment name matches your Azure resource

3. **Docker Issues**:
   - Run `docker-compose down -v` to reset volumes
   - Check Docker service logs: `docker-compose logs`

### Useful Commands

```bash
# For Local Development (Docker PostgreSQL only)
# Start database
docker-compose up -d postgres

# Stop database
docker-compose down

# Reset database (removes all data)
docker-compose down -v
docker-compose up -d postgres

# Access database directly
docker exec -it chainlit_postgres psql -U postgres -d chainlit_db

# Check database status
docker-compose ps

# View database logs
docker-compose logs postgres

# For Full Docker Setup
# View all logs
docker-compose logs -f

# Reset everything
docker-compose down -v
docker-compose up --build
```

## Security Considerations

- **Production Deployment**: 
  - Replace demo credentials with secure authentication
  - Use environment variables for sensitive data
  - Implement password hashing (bcrypt recommended)
  - Use HTTPS in production
  - Set up proper database access controls

- **Database Security**:
  - Use strong database passwords
  - Restrict database access to application only
  - Regular database backups

## Customization

You can customize the application by:

- Modifying `chainlit.md` for custom styling
- Adding more user accounts in the `auth_callback` function
- Extending the database schema for additional features
- Customizing the Docker configuration

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

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


