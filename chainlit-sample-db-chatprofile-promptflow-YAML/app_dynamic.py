import os
import sys
import asyncio
import logging
import chainlit as cl
from openai import AzureOpenAI
from dotenv import load_dotenv
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from typing import Optional, Dict, List, Any
from chainlit.types import ThreadDict

# Add current directory to Python path for promptflows module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import dynamic configuration system
from config.config_loader import get_config_loader, ProfileConfig
from config.promptflow_executor import get_promptflow_executor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PDF processing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")

# Promptflow imports
try:
    from promptflow.client import PFClient
    from promptflow.core import Flow
    PROMPTFLOW_AVAILABLE = True
except ImportError:
    PROMPTFLOW_AVAILABLE = False
    logger.warning("Promptflow not available. Install with: pip install promptflow-azure")

# Load environment variables
load_dotenv()

# Initialize configuration loader
config_loader = get_config_loader()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)

MODEL_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

# Initialize Promptflow client if available
pf_client = None
if PROMPTFLOW_AVAILABLE:
    try:
        pf_client = PFClient()
    except Exception as e:
        logger.warning(f"Could not initialize Promptflow client: {e}")

# Initialize promptflow executor
try:
    promptflow_executor = get_promptflow_executor()
except Exception as e:
    logger.warning(f"Promptflow executor initialization failed: {e}")
    promptflow_executor = None

# Configure SQLAlchemy Data Layer for PostgreSQL
@cl.data_layer
def get_data_layer():
    """
    Configure and return the SQLAlchemy data layer for chat persistence.
    """
    db_url = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/chainlit_db")
    return SQLAlchemyDataLayer(conninfo=db_url)

@cl.set_chat_profiles
async def chat_profile(current_user: cl.User):
    """
    Define available chat profiles based on user role and configuration.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        List of available chat profiles or None if not authorized
    """
    if not current_user:
        return None
    
    # Get user role
    user_role = current_user.metadata.get("role")
    
    # Get available profiles for this user
    available_profiles = config_loader.get_profiles_for_user(
        user_role=user_role, 
        has_promptflow=PROMPTFLOW_AVAILABLE
    )
    
    # Convert to Chainlit ChatProfile objects
    profiles = []
    for profile_name, profile_config in available_profiles.items():
        profiles.append(cl.ChatProfile(
            name=profile_config.name,
            markdown_description=profile_config.markdown_description,
            icon=profile_config.icon,
        ))
    
    logger.info(f"User {current_user.identifier} has access to {len(profiles)} profiles")
    return profiles

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    Handle password authentication using configuration.
    
    Args:
        username: The username provided by the user
        password: The password provided by the user
        
    Returns:
        cl.User object if authentication successful, None otherwise
    """
    auth_config = config_loader.get_auth_config()
    
    if not auth_config or not auth_config.enabled:
        # Authentication disabled, allow all
        return cl.User(
            identifier=username,
            metadata={"role": "user", "provider": "none"}
        )
    
    # Validate credentials
    if not config_loader.validate_user_credentials(username, password):
        return None
    
    # Get user metadata
    user_role = config_loader.get_user_role(username)
    user_metadata = config_loader.get_user_metadata(username)
    
    return cl.User(
        identifier=username,
        metadata={
            "role": user_role,
            "provider": "credentials",
            **user_metadata
        }
    )

def get_system_prompt(chat_profile: str) -> str:
    """
    Get the system prompt based on the selected chat profile from configuration.
    
    Args:
        chat_profile: The name of the selected chat profile
        
    Returns:
        System prompt string for the selected profile
    """
    profile_config = config_loader.get_profile_config(chat_profile)
    if profile_config:
        return profile_config.system_prompt
    
    # Fallback to default
    default_config = config_loader.get_profile_config("Assistant")
    return default_config.system_prompt if default_config else "You are a helpful AI assistant."

def get_model_temperature(chat_profile: str) -> float:
    """
    Get the temperature setting based on the selected chat profile from configuration.
    
    Args:
        chat_profile: The name of the selected chat profile
        
    Returns:
        Temperature value for the model
    """
    profile_config = config_loader.get_profile_config(chat_profile)
    if profile_config:
        return profile_config.temperature
    
    # Fallback to default
    return 0.7

def get_model_settings(chat_profile: str) -> Dict[str, Any]:
    """
    Get all model settings for a chat profile from configuration.
    
    Args:
        chat_profile: The name of the selected chat profile
        
    Returns:
        Dictionary of model settings
    """
    profile_config = config_loader.get_profile_config(chat_profile)
    if profile_config and profile_config.model_settings:
        return profile_config.model_settings
    
    # Return default settings
    global_settings = config_loader.settings.get("default_model_settings", {})
    return global_settings

async def run_promptflow_chat_assistant(message: str, chat_history: List[Dict], profile_name: str) -> str:
    """
    Run the chat assistant promptflow using dynamic executor.
    """
    try:
        if not promptflow_executor:
            raise ValueError("Promptflow executor not available")
        
        # Prepare inputs
        inputs = {
            "question": message,
            "chat_history": chat_history,
            "profile_name": profile_name
        }
        
        # Execute flow
        result = await promptflow_executor.execute_flow("chat_assistant", inputs)
        
        return result.get("answer", "No response generated")
        
    except Exception as e:
        logger.error(f"Promptflow chat assistant error: {e}")
        return f"Promptflow processing error: {str(e)}"

async def run_promptflow_document_qa(message: str, document_content: str, chat_history: List[Dict]) -> Dict[str, str]:
    """
    Run the document Q&A promptflow using dynamic executor.
    """
    try:
        if not promptflow_executor:
            raise ValueError("Promptflow executor not available")
        
        # Prepare inputs
        inputs = {
            "question": message,
            "document_content": document_content,
            "chat_history": chat_history
        }
        
        # Execute flow
        result = await promptflow_executor.execute_flow("document_qa", inputs)
        
        return {
            "answer": result.get("answer", "No answer generated"),
            "relevance_score": result.get("relevance_score", "Unknown"),
            "sources": result.get("sources", "No sources found")
        }
        
    except Exception as e:
        logger.error(f"Promptflow document Q&A error: {e}")
        return {
            "answer": f"Error processing document: {str(e)}",
            "relevance_score": "0",
            "sources": "Error"
        }

def extract_text_from_pdf(pdf_file_path: str) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        pdf_file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    if not PDF_AVAILABLE:
        return "PDF processing not available. Please install PyPDF2."
    
    try:
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return f"Error reading PDF: {str(e)}"

def read_text_file(file_path: str) -> str:
    """
    Read content from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading text file: {e}")
        return f"Error reading file: {str(e)}"

@cl.on_chat_start
async def start():
    """
    Initialize the chat session with dynamic configuration.
    """
    # Get current chat profile
    chat_profile = cl.user_session.get("chat_profile", "Assistant")
    
    # Get profile configuration
    profile_config = config_loader.get_profile_config(chat_profile)
    
    if not profile_config:
        logger.warning(f"Profile configuration not found: {chat_profile}")
        chat_profile = "Assistant"
        profile_config = config_loader.get_profile_config(chat_profile)
    
    # Set chat profile in session
    cl.user_session.set("chat_profile", chat_profile)
    
    # Display welcome message
    welcome_message = f"👋 Welcome to **{profile_config.name}**!\n\n{profile_config.markdown_description}"
    
    # Add file upload capability for document profiles
    if profile_config.supports_file_upload:
        welcome_message += "\n\n📁 **You can upload documents** (PDF, TXT, DOCX, MD) and ask questions about them!"
    
    await cl.Message(content=welcome_message).send()
    
    logger.info(f"Chat session started with profile: {chat_profile}")

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict): 
    """
    Handle chat session resume with dynamic configuration.
    
    Args:
        thread: The thread dictionary containing chat history
    """
    # Get chat profile from thread metadata or default
    chat_profile = thread.get("metadata", {}).get("chat_profile", "Assistant")
    
    # Validate profile still exists and is enabled
    profile_config = config_loader.get_profile_config(chat_profile)
    if not profile_config or not profile_config.enabled:
        chat_profile = "Assistant"
        profile_config = config_loader.get_profile_config(chat_profile)
    
    # Set chat profile in session
    cl.user_session.set("chat_profile", chat_profile)
    
    logger.info(f"Chat session resumed with profile: {chat_profile}")

@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages with dynamic profile processing.
    
    Args:
        message: The incoming message object
    """
    try:
        # Get current chat profile
        chat_profile = cl.user_session.get("chat_profile", "Assistant")
        profile_config = config_loader.get_profile_config(chat_profile)
        
        if not profile_config:
            await cl.Message(content="❌ Profile configuration error. Please restart the chat.").send()
            return
        
        # Get chat history
        message_history = cl.user_session.get("message_history", [])
        
        # Handle file uploads for document profiles
        if profile_config.supports_file_upload and message.elements:
            for element in message.elements:
                if isinstance(element, cl.File):
                    # Process uploaded file
                    file_content = await process_uploaded_file(element)
                    
                    if file_content:
                        # Use document Q&A flow
                        if profile_config.flow_config and profile_config.flow_config.get("flow_type") == "document_qa":
                            result = await run_promptflow_document_qa(
                                message.content, 
                                file_content, 
                                message_history
                            )
                            
                            response_text = f"**Answer:** {result['answer']}\n\n**Relevance Score:** {result['relevance_score']}\n\n**Sources:** {result['sources']}"
                        else:
                            # Fallback to regular chat with document context
                            response_text = await generate_response_with_context(
                                message.content, 
                                file_content, 
                                chat_profile, 
                                message_history
                            )
                    else:
                        response_text = "❌ Could not process the uploaded file. Please try again with a supported file format."
        
        # Handle promptflow profiles
        elif profile_config.requires_promptflow and profile_config.flow_config:
            flow_type = profile_config.flow_config.get("flow_type")
            
            if flow_type == "chat_assistant":
                response_text = await run_promptflow_chat_assistant(
                    message.content, 
                    message_history, 
                    chat_profile
                )
            else:
                # Fallback to regular chat
                response_text = await generate_regular_response(
                    message.content, 
                    chat_profile, 
                    message_history
                )
        
        # Handle regular profiles
        else:
            response_text = await generate_regular_response(
                message.content, 
                chat_profile, 
                message_history
            )
        
        # Update message history
        message_history.append({"role": "user", "content": message.content})
        message_history.append({"role": "assistant", "content": response_text})
        
        # Keep only last 10 exchanges
        if len(message_history) > 20:
            message_history = message_history[-20:]
        
        cl.user_session.set("message_history", message_history)
        
        # Send response
        await cl.Message(content=response_text).send()
        
    except Exception as e:
        logger.error(f"Error in main message handler: {e}")
        await cl.Message(content=f"❌ An error occurred: {str(e)}").send()

async def process_uploaded_file(file_element: cl.File) -> Optional[str]:
    """
    Process an uploaded file and extract its content.
    
    Args:
        file_element: The uploaded file element
        
    Returns:
        Extracted file content or None if processing failed
    """
    try:
        file_path = file_element.path
        file_name = file_element.name.lower()
        
        # Get file upload settings from configuration
        promptflow_config = config_loader.get_promptflow_config()
        file_upload_config = promptflow_config.file_upload if promptflow_config else {}
        
        max_size_mb = file_upload_config.get("max_file_size_mb", 10)
        allowed_extensions = file_upload_config.get("allowed_extensions", [".txt", ".pdf", ".md"])
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            logger.warning(f"File too large: {file_size_mb:.2f}MB > {max_size_mb}MB")
            return None
        
        # Check file extension
        file_ext = os.path.splitext(file_name)[1]
        if file_ext not in allowed_extensions:
            logger.warning(f"File extension not allowed: {file_ext}")
            return None
        
        # Extract content based on file type
        if file_ext == ".pdf":
            return extract_text_from_pdf(file_path)
        else:
            return read_text_file(file_path)
            
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        return None

async def generate_response_with_context(
    user_message: str, 
    document_content: str, 
    chat_profile: str, 
    message_history: List[Dict]
) -> str:
    """
    Generate response with document context.
    """
    try:
        system_prompt = get_system_prompt(chat_profile)
        temperature = get_model_temperature(chat_profile)
        model_settings = get_model_settings(chat_profile)
        
        # Build context-aware prompt
        context_prompt = f"""Based on the following document content, please answer the user's question:

Document Content:
{document_content[:3000]}...

User Question: {user_message}

Please provide a detailed answer based only on the information in the document content."""
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context_prompt}
            ],
            temperature=temperature,
            max_tokens=model_settings.get("max_tokens", 1000),
            top_p=model_settings.get("top_p", 1.0)
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating response with context: {e}")
        return f"Error generating response: {str(e)}"

async def generate_regular_response(
    user_message: str, 
    chat_profile: str, 
    message_history: List[Dict]
) -> str:
    """
    Generate regular chat response.
    """
    try:
        system_prompt = get_system_prompt(chat_profile)
        temperature = get_model_temperature(chat_profile)
        model_settings = get_model_settings(chat_profile)
        
        # Build message list
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history (last 5 exchanges)
        recent_history = message_history[-10:] if len(message_history) > 10 else message_history
        messages.extend(recent_history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=model_settings.get("max_tokens", 1000),
            top_p=model_settings.get("top_p", 1.0)
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error generating regular response: {e}")
        return f"Error generating response: {str(e)}"

if __name__ == "__main__":
    # Load configuration at startup
    logger.info("Starting Chainlit application with dynamic configuration")
    logger.info(f"Loaded {len(config_loader.get_all_profiles())} profiles")
    logger.info(f"Promptflow available: {PROMPTFLOW_AVAILABLE}")
    logger.info(f"PDF processing available: {PDF_AVAILABLE}") 