import os
import chainlit as cl
from openai import AzureOpenAI
from dotenv import load_dotenv
from chainlit.data.sql_alchemy import SQLAlchemyDataLayer
from typing import Optional
from chainlit.types import ThreadDict

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)

MODEL_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

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
        
        "Business": "You are a business consultant AI assistant with expertise in strategy, market analysis, and professional guidance. Focus on business insights, strategic thinking, and professional communication."
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
        "Business": 0.6
    }
    
    return temperatures.get(chat_profile, 0.7)

@cl.on_chat_start
async def start():
    """
    Initialize the chat session and send a welcome message.
    """
    user = cl.user_session.get("user")
    chat_profile = cl.user_session.get("chat_profile")
    username = user.identifier if user else "Guest"
    
    # Initialize conversation history in user session with profile-specific system prompt
    system_prompt = get_system_prompt(chat_profile)
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": system_prompt}
    ])
    
    profile_descriptions = {
        "Assistant": "I'm ready to help you with any questions or tasks you have!",
        "Creative": "I'm excited to help you explore creative ideas and bring your imagination to life!",
        "Analytical": "I'm here to help you analyze data, solve problems, and think through complex issues systematically.",
        "Technical": "I'm ready to dive into technical discussions, code reviews, and system architecture!",
        "Business": "I'm here to provide strategic insights and professional guidance for your business needs."
    }
    
    profile_message = profile_descriptions.get(chat_profile, profile_descriptions["Assistant"])
    
    await cl.Message(
        content=f"Hello {username}! Welcome to the **{chat_profile}** chat profile. {profile_message}",
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
    
    # Initialize conversation history when resuming a chat with profile-specific system prompt
    # Note: In a full implementation, you might want to reconstruct the conversation
    # history from the database thread messages
    system_prompt = get_system_prompt(chat_profile)
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": system_prompt}
    ])
    
    await cl.Message(
        content=f"Welcome back {username}! Resuming our **{chat_profile}** conversation...",
        author=f"AI {chat_profile}",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle user messages and generate AI responses while maintaining conversation context.
    
    Args:
        message: User message object
    """
    # Get the current chat profile
    chat_profile = cl.user_session.get("chat_profile", "Assistant")
    
    # Get the user's message
    user_message = message.content
    
    # Get conversation history from user session
    conversation_history = cl.user_session.get("conversation_history", [
        {"role": "system", "content": get_system_prompt(chat_profile)}
    ])
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Create a message placeholder for loading state
    msg = cl.Message(content="", author=f"AI {chat_profile}")
    await msg.send()
    
    # Get profile-specific configuration
    temperature = get_model_temperature(chat_profile)
    
    # Stream the response from Azure OpenAI
    response_text = []
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation_history,
            temperature=temperature,
            stream=True,
        )
        
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                response_text.append(content)
                await msg.stream_token(content)
        
        # Update the final message
        full_response = "".join(response_text)
        msg.content = full_response
        await msg.update()
        
        # Add assistant response to conversation history
        conversation_history.append({"role": "assistant", "content": full_response})
        
        # Update conversation history in user session
        cl.user_session.set("conversation_history", conversation_history)
        
    except Exception as e:
        error_message = f"Sorry, I encountered an error: {str(e)}"
        msg.content = error_message
        await msg.update()
        
        # Don't add error messages to conversation history to avoid confusing the AI
