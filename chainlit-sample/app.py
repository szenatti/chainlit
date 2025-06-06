import os
import chainlit as cl
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
)

MODEL_NAME = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")

@cl.on_chat_start
async def start():
    """
    Initialize the chat session and send a welcome message.
    """
    # Initialize conversation history in user session
    cl.user_session.set("conversation_history", [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ])
    
    await cl.Message(
        content="Hello! I'm your AI assistant powered by Azure OpenAI. How can I help you today?",
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
