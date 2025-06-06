from typing import List, Dict, Any

# For direct usage without promptflow runtime, we don't need the @tool decorator
def prepare_prompt(chat_history: List[Dict[str, Any]], question: str, profile_name: str) -> Dict[str, str]:
    """
    Prepare system prompt and user message based on the chat profile and history.
    
    Args:
        chat_history: List of previous messages
        question: Current user question
        profile_name: Selected chat profile name
    
    Returns:
        Dictionary with system_prompt and user_message
    """
    
    # Define profile-specific system prompts
    profile_prompts = {
        "Assistant": "You are a helpful AI assistant. Provide balanced, informative, and friendly responses to help users with their questions and tasks.",
        
        "Creative": "You are a creative AI assistant with enhanced imagination and artistic flair. Focus on storytelling, brainstorming, creative writing, and artistic content. Be expressive, innovative, and inspire creativity in your responses.",
        
        "Analytical": "You are an analytical AI assistant focused on logical reasoning, data analysis, and structured problem-solving. Provide clear, methodical, and evidence-based responses. Break down complex problems into manageable steps.",
        
        "Technical": "You are a technical expert AI assistant specializing in software development, system architecture, and technical problem-solving. Provide detailed technical explanations, code examples, and best practices.",
        
        "Business": "You are a business consultant AI assistant with expertise in strategy, market analysis, and professional guidance. Focus on business insights, strategic thinking, and professional communication."
    }
    
    # Get the system prompt for the selected profile
    system_prompt = profile_prompts.get(profile_name, profile_prompts["Assistant"])
    
    # Build conversation context from chat history
    conversation_context = ""
    if chat_history:
        conversation_context = "\n\nPrevious conversation:\n"
        for message in chat_history[-5:]:  # Use last 5 messages for context
            role = message.get("role", "user")
            content = message.get("content", "")
            conversation_context += f"{role.title()}: {content}\n"
    
    # Prepare the user message with context
    user_message = f"{conversation_context}\n\nCurrent question: {question}"
    
    return {
        "system_prompt": system_prompt,
        "user_message": user_message.strip()
    } 