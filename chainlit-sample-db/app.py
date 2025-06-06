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

@cl.on_chat_start
async def start():
    """
    Initialize the chat session and send a welcome message.
    """
    user = cl.user_session.get("user")
    username = user.identifier if user else "Guest"
    
    # Initialize conversation history in user session
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ])
    
    await cl.Message(
        content=f"Hello {username}! I'm your AI assistant powered by Azure OpenAI. How can I help you today?",
        author="AI Assistant",
    ).send()

@cl.on_chat_resume
async def on_chat_resume(thread: ThreadDict): 
    """
    Handle chat resume when a user continues a previous conversation.
    
    Args:
        thread: The persisted thread being resumed
    """
    user = cl.user_session.get("user")
    username = user.identifier if user else "Guest"
    
    # Initialize conversation history when resuming a chat
    # Note: In a full implementation, you might want to reconstruct the conversation
    # history from the database thread messages
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ])
    
    await cl.Message(
        content=f"Welcome back {username}! Resuming our previous conversation...",
        author="AI Assistant",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """
    Handle user messages and generate AI responses while maintaining conversation context.
    
    Args:
        message: User message object
    """
    # Get the user's message
    user_message = message.content
    
    # Get conversation history from user session
    conversation_history = cl.user_session.get("conversation_history", [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ])
    
    # Add user message to conversation history
    conversation_history.append({"role": "user", "content": user_message})
    
    # Create a message placeholder for loading state
    msg = cl.Message(content="", author="AI Assistant")
    await msg.send()
    
    # Stream the response from Azure OpenAI
    response_text = []
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=conversation_history,
            temperature=0.7,
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
