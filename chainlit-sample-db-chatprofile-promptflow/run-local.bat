@echo off
echo Setting up Chainlit Application with Promptflow Integration...

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo # Azure OpenAI Configuration > .env
    echo AZURE_OPENAI_API_KEY=your_actual_api_key >> .env
    echo AZURE_OPENAI_ENDPOINT=https://your_resource_name.openai.azure.com/ >> .env
    echo AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name >> .env
    echo AZURE_OPENAI_API_VERSION=2023-07-01-preview >> .env
    echo. >> .env
    echo # Database Configuration >> .env
    echo DATABASE_URL=postgresql://postgres:password@localhost:5432/chainlit_db >> .env
    echo POSTGRES_USER=postgres >> .env
    echo POSTGRES_PASSWORD=password >> .env
    echo POSTGRES_DB=chainlit_db >> .env
    echo.
    echo .env file created! Please edit it with your actual Azure OpenAI credentials.
) else (
    echo .env file already exists.
)

REM Start PostgreSQL database with Docker
echo Starting PostgreSQL database...
docker-compose up -d postgres

REM Wait for database to be ready
echo Waiting for database to be ready...
timeout /t 10 /nobreak > nul

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your actual Azure OpenAI credentials
echo 2. Create and activate a Python virtual environment:
echo    python -m venv venv
echo    venv\Scripts\activate
echo 3. Install dependencies:
echo    pip install -r requirements.txt
echo 4. Run the application:
echo    chainlit run app.py
echo.
echo Access the application at: http://localhost:8000 