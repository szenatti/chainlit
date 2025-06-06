import os
import sys
import asyncio
import chainlit as cl
from openai import AzureOpenAI
from dotenv import load_dotenv
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from typing import Optional, Dict, List, Any
from chainlit.types import ThreadDict

# Add current directory to Python path for promptflows module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# PDF processing imports
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("Warning: PyPDF2 not available. Install with: pip install PyPDF2")

# Promptflow imports
try:
    from promptflow import PFClient
    from promptflow.core import Flow
    PROMPTFLOW_AVAILABLE = True
except ImportError:
    PROMPTFLOW_AVAILABLE = False
    print("Warning: Promptflow not available. Install with: pip install promptflow-azure")

# Load environment variables
load_dotenv()

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
        print(f"Warning: Could not initialize Promptflow client: {e}")

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
    Define available chat profiles based on user role.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        List of available chat profiles or None if not authorized
    """
    if not current_user:
        return None
    
    # Base profiles available to all users
    profiles = [
        cl.ChatProfile(
            name="Assistant",
            markdown_description="**General AI Assistant** - Balanced and helpful responses for everyday tasks and questions.",
            icon="/public/icons/robot.svg",
        ),
        cl.ChatProfile(
            name="Creative",
            markdown_description="**Creative Writer** - Enhanced creativity for storytelling, brainstorming, and artistic content.",
            icon="/public/icons/creative.svg",
        ),
        cl.ChatProfile(
            name="Analytical",
            markdown_description="**Data Analyst** - Logical and structured responses for analysis, research, and problem-solving.",
            icon="/public/icons/analytical.svg",
        ),
    ]
    
    # Add Promptflow-enhanced profiles if available
    if PROMPTFLOW_AVAILABLE:
        profiles.extend([
            cl.ChatProfile(
                name="PromptFlow-Assistant",
                markdown_description="**Promptflow Chat Assistant** - Advanced chat responses using Azure Promptflow orchestration.",
                icon="/public/icons/promptflow.svg",
            ),
            cl.ChatProfile(
                name="Document-QA",
                markdown_description="**Document Q&A** - Upload documents and ask questions using Promptflow document analysis.",
                icon="/public/icons/document.svg",
            ),
        ])
    
    # Admin-only profiles
    if current_user.metadata.get("role") == "admin":
        profiles.extend([
            cl.ChatProfile(
                name="Technical",
                markdown_description="**Technical Expert** - Advanced technical discussions, coding, and system architecture.",
                icon="/public/icons/technical.svg",
            ),
            cl.ChatProfile(
                name="Business",
                markdown_description="**Business Consultant** - Strategic business advice, market analysis, and professional guidance.",
                icon="/public/icons/business.svg",
            ),
        ])
    
    return profiles

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
    """
    Handle password authentication.
    
    Args:
        username: The username provided by the user
        password: The password provided by the user
        
    Returns:
        cl.User object if authentication successful, None otherwise
    """
    # For demonstration purposes, using simple hardcoded credentials
    # In production, you should verify against a database with hashed passwords
    valid_users = {
        "admin": "admin123",
        "user": "user123",
        "demo": "demo123"
    }
    
    if username in valid_users and valid_users[username] == password:
        return cl.User(
            identifier=username,
            metadata={
                "role": "admin" if username == "admin" else "user",
                "provider": "credentials"
            }
        )
    return None

def get_system_prompt(chat_profile: str) -> str:
    """
    Get the system prompt based on the selected chat profile.
    
    Args:
        chat_profile: The name of the selected chat profile
        
    Returns:
        System prompt string for the selected profile
    """
    prompts = {
        "Assistant": "You are a helpful AI assistant. Provide balanced, informative, and friendly responses to help users with their questions and tasks.",
        
        "Creative": "You are a creative AI assistant with enhanced imagination and artistic flair. Focus on storytelling, brainstorming, creative writing, and artistic content. Be expressive, innovative, and inspire creativity in your responses.",
        
        "Analytical": "You are an analytical AI assistant focused on logical reasoning, data analysis, and structured problem-solving. Provide clear, methodical, and evidence-based responses. Break down complex problems into manageable steps.",
        
        "Technical": "You are a technical expert AI assistant specializing in software development, system architecture, and technical problem-solving. Provide detailed technical explanations, code examples, and best practices.",
        
        "Business": "You are a business consultant AI assistant with expertise in strategy, market analysis, and professional guidance. Focus on business insights, strategic thinking, and professional communication.",
        
        "PromptFlow-Assistant": "You are an advanced AI assistant powered by Azure Promptflow. You provide enhanced conversational experiences with sophisticated prompt engineering and flow orchestration.",
        
        "Document-QA": "You are a document analysis assistant powered by Azure Promptflow. You help users analyze documents and answer questions based on document content with detailed citations and relevance scoring."
    }
    
    return prompts.get(chat_profile, prompts["Assistant"])

def get_model_temperature(chat_profile: str) -> float:
    """
    Get the temperature setting based on the selected chat profile.
    
    Args:
        chat_profile: The name of the selected chat profile
        
    Returns:
        Temperature value for the model
    """
    temperatures = {
        "Assistant": 0.7,
        "Creative": 0.9,
        "Analytical": 0.3,
        "Technical": 0.5,
        "Business": 0.6,
        "PromptFlow-Assistant": 0.7,
        "Document-QA": 0.3
    }
    
    return temperatures.get(chat_profile, 0.7)

async def run_promptflow_chat_assistant(message: str, chat_history: List[Dict], profile_name: str) -> str:
    """
    Run the chat assistant promptflow.
    """
    try:
        # For now, use a simplified promptflow-style processing without actual flow execution
        # This avoids complex connection setup while demonstrating the concept
        
        # Simulate the prepare_prompt step
        from promptflows.chat_assistant.prepare_prompt import prepare_prompt
        prompt_result = prepare_prompt(chat_history, message, profile_name)
        
        # Use Azure OpenAI directly with the prepared prompts
        system_prompt = prompt_result["system_prompt"]
        user_message = prompt_result["user_message"]
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        llm_output = response.choices[0].message.content
        
        # Simulate the format_response step
        from promptflows.chat_assistant.format_response import format_response
        formatted_result = format_response(llm_output, profile_name)
        
        return formatted_result
        
    except Exception as e:
        return f"Promptflow processing error: {str(e)}"

async def run_promptflow_document_qa(message: str, document_content: str, chat_history: List[Dict]) -> Dict[str, str]:
    """
    Run the document Q&A promptflow.
    """
    try:
        # Simulate the document processing pipeline
        
        # Step 1: Preprocess document
        from promptflows.document_qa.preprocess_document import preprocess_document
        processed_doc = preprocess_document(document_content, message)
        
        # Step 2: Extract context
        from promptflows.document_qa.extract_context import extract_context
        context_result = extract_context(processed_doc, message, chat_history)
        
        # Step 3: Generate answer using Azure OpenAI
        system_prompt = """You are an expert document analyst. Your task is to answer questions based solely on the provided document context. 

Guidelines:
- Answer questions using only the information provided in the context
- If the context doesn't contain enough information to answer the question, clearly state this
- Provide specific quotes or references when possible
- Be precise and avoid speculation beyond the given context
- If asked about information not in the context, explain what information is missing"""
        
        user_prompt = f"""Context from document:
{context_result['context']}

{context_result['formatted_history']}

Question: {message}

Please provide a comprehensive answer based on the context above. If the context is insufficient to fully answer the question, please explain what additional information would be needed."""
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        answer = response.choices[0].message.content
        
        # Step 4: Calculate relevance
        from promptflows.document_qa.calculate_relevance import calculate_relevance
        relevance_score = calculate_relevance(message, answer, context_result['context'])
        
        # Step 5: Extract sources
        from promptflows.document_qa.extract_sources import extract_sources
        sources = extract_sources(processed_doc, context_result['context'], answer)
        
        return {
            "answer": answer,
            "relevance_score": relevance_score,
            "sources": sources
        }
        
    except Exception as e:
        return {
            "answer": f"Document Q&A processing error: {str(e)}",
            "relevance_score": "Error occurred",
            "sources": "Could not extract sources due to error"
        }

@cl.on_chat_start
async def start():
    """
    Initialize the chat session and send a welcome message.
    """
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    username = user.identifier if user else "Guest"
    
    # Initialize session variables
    cl.user_session.set("chat_history", [])
    cl.user_session.set("document_content", "")
    
    profile_descriptions = {
        "Assistant": "I'm ready to help you with any questions or tasks you have!",
        "Creative": "I'm excited to help you explore creative ideas and bring your imagination to life!",
        "Analytical": "I'm here to help you analyze data, solve problems, and think through complex issues systematically.",
        "Technical": "I'm ready to dive into technical discussions, code reviews, and system architecture!",
        "Business": "I'm here to provide strategic insights and professional guidance for your business needs.",
        "PromptFlow-Assistant": "I'm powered by Azure Promptflow for enhanced conversational AI. Let's have an intelligent conversation!",
        "Document-QA": "I can analyze documents and answer questions about their content. Please upload a document to get started!"
    }
    
    profile_message = profile_descriptions.get(chat_profile, profile_descriptions["Assistant"])
    
    welcome_msg = f"Hello {username}! Welcome to the **{chat_profile}** chat profile. {profile_message}"
    
    # Add special instructions for Document Q&A
    if chat_profile == "Document-QA":
        welcome_msg += "\n\n📎 **To upload a document:** Click the attachment button below and upload a document (PDF, TXT, MD, CSV, JSON, XML, HTML), or paste document content directly in your message."
    
    await cl.Message(
        content=welcome_msg,
        author=f"AI {chat_profile}",
    ).send()

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict): 
    """
    Handle chat resume when a user continues a previous conversation.
    
    Args:
        thread: The persisted thread being resumed
    """
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    username = user.identifier if user else "Guest"
    
    # Restore session variables
    cl.user_session.set("chat_history", [])
    cl.user_session.set("document_content", "")
    
    await cl.Message(
        content=f"Welcome back {username}! Resuming our **{chat_profile}** conversation...",
        author=f"AI {chat_profile}",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle user messages and generate AI responses.
    
    Args:
        message: User message object
    """
    # Get the current chat profile
    chat_profile = cl.user_session.get("chat_profile", "Assistant")
    
    # Get the user's message
    user_message = message.content
    
    # Handle file uploads for Document Q&A
    document_content = cl.user_session.get("document_content", "")
    if message.elements:
        for element in message.elements:
            if isinstance(element, cl.File):
                try:
                    # Check file extension to determine how to read it
                    file_extension = os.path.splitext(element.name.lower())[1]
                    
                    if file_extension == '.pdf':
                        # Handle PDF files
                        if not PDF_AVAILABLE:
                            await cl.Message(
                                content=f"❌ PDF support not available. Please install PyPDF2: pip install PyPDF2",
                                author=f"AI {chat_profile}"
                            ).send()
                            continue
                            
                        document_content = ""
                        with open(element.path, 'rb') as f:
                            pdf_reader = PyPDF2.PdfReader(f)
                            for page in pdf_reader.pages:
                                document_content += page.extract_text() + "\n"
                                
                    elif file_extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html']:
                        # Handle text-based files
                        try:
                            with open(element.path, 'r', encoding='utf-8') as f:
                                document_content = f.read()
                        except UnicodeDecodeError:
                            # Try with different encoding if UTF-8 fails
                            with open(element.path, 'r', encoding='latin-1') as f:
                                document_content = f.read()
                    else:
                        # Try to read as text file anyway
                        try:
                            with open(element.path, 'r', encoding='utf-8') as f:
                                document_content = f.read()
                        except UnicodeDecodeError:
                            with open(element.path, 'r', encoding='latin-1') as f:
                                document_content = f.read()
                    
                    if document_content.strip():
                        cl.user_session.set("document_content", document_content)
                        file_type = "PDF" if file_extension == '.pdf' else "document"
                        await cl.Message(
                            content=f"📄 {file_type.capitalize()} '{element.name}' uploaded successfully! You can now ask questions about its content.",
                            author=f"AI {chat_profile}"
                        ).send()
                    else:
                        await cl.Message(
                            content=f"❌ The file '{element.name}' appears to be empty or could not be read.",
                            author=f"AI {chat_profile}"
                        ).send()
                        
                except Exception as e:
                    await cl.Message(
                        content=f"❌ Error processing file '{element.name}': {str(e)}. Supported formats: PDF, TXT, MD, CSV, JSON, XML, HTML",
                        author=f"AI {chat_profile}"
                    ).send()
    
    # Create a message placeholder for loading state
    msg = cl.Message(content="", author=f"AI {chat_profile}")
    await msg.send()
    
    # Get chat history
    chat_history = cl.user_session.get("chat_history", [])
    
    try:
        # Handle different chat profiles
        if chat_profile == "PromptFlow-Assistant" and PROMPTFLOW_AVAILABLE:
            # Use Promptflow for enhanced chat
            response_text = await run_promptflow_chat_assistant(
                user_message, 
                chat_history, 
                chat_profile.replace("PromptFlow-", "")
            )
            
        elif chat_profile == "Document-QA" and PROMPTFLOW_AVAILABLE:
            # Use Promptflow for document Q&A
            if not document_content:
                response_text = "Please upload a document first before asking questions. You can attach a file or paste document content in your message."
            else:
                qa_result = await run_promptflow_document_qa(user_message, document_content, chat_history)
                response_text = f"{qa_result['answer']}\n\n{qa_result['relevance_score']}\n\n{qa_result['sources']}"
        
        else:
            # Use standard Azure OpenAI for other profiles
            system_prompt = get_system_prompt(chat_profile)
            temperature = get_model_temperature(chat_profile)
            
            # Build messages array with chat history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history to messages
            messages.extend(chat_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            
            response_parts = []
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    response_parts.append(content)
                    await msg.stream_token(content)
            
            response_text = "".join(response_parts)
        
        # Update the message with final response
        msg.content = response_text
        await msg.update()
        
        # Update chat history
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": response_text})
        cl.user_session.set("chat_history", chat_history[-10:])  # Keep last 10 messages
        
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        msg.content = error_message
        await msg.update()
