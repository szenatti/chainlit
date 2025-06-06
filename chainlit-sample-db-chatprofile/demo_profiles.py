#!/usr/bin/env python3
"""
Demo script to showcase Chat Profiles functionality in Chainlit.

This script demonstrates the different chat profiles available in the application,
their system prompts, and temperature settings.
"""

def get_system_prompt(chat_profile: str) -> str:
    """Get the system prompt based on the selected chat profile."""
    prompts = {
        "Assistant": "You are a helpful AI assistant. Provide balanced, informative, and friendly responses to help users with their questions and tasks.",
        
        "Creative": "You are a creative AI assistant with enhanced imagination and artistic flair. Focus on storytelling, brainstorming, creative writing, and artistic content. Be expressive, innovative, and inspire creativity in your responses.",
        
        "Analytical": "You are an analytical AI assistant focused on logical reasoning, data analysis, and structured problem-solving. Provide clear, methodical, and evidence-based responses. Break down complex problems into manageable steps.",
        
        "Technical": "You are a technical expert AI assistant specializing in software development, system architecture, and technical problem-solving. Provide detailed technical explanations, code examples, and best practices.",
        
        "Business": "You are a business consultant AI assistant with expertise in strategy, market analysis, and professional guidance. Focus on business insights, strategic thinking, and professional communication."
    }
    
    return prompts.get(chat_profile, prompts["Assistant"])

def get_model_temperature(chat_profile: str) -> float:
    """Get the temperature setting based on the selected chat profile."""
    temperatures = {
        "Assistant": 0.7,
        "Creative": 0.9,
        "Analytical": 0.3,
        "Technical": 0.5,
        "Business": 0.6
    }
    
    return temperatures.get(chat_profile, 0.7)

def demo_chat_profiles():
    """Demonstrate the different chat profiles available."""
    print("=" * 80)
    print("CHAINLIT CHAT PROFILES DEMONSTRATION")
    print("=" * 80)
    
    profiles = {
        "🤖 Assistant": {
            "access": "All Users",
            "description": "General AI Assistant - Balanced and helpful responses for everyday tasks and questions."
        },
        "🎨 Creative": {
            "access": "All Users", 
            "description": "Creative Writer - Enhanced creativity for storytelling, brainstorming, and artistic content."
        },
        "📊 Analytical": {
            "access": "All Users",
            "description": "Data Analyst - Logical and structured responses for analysis, research, and problem-solving."
        },
        "⚙️ Technical": {
            "access": "Admin Only",
            "description": "Technical Expert - Advanced technical discussions, coding, and system architecture."
        },
        "💼 Business": {
            "access": "Admin Only",
            "description": "Business Consultant - Strategic business advice, market analysis, and professional guidance."
        }
    }
    
    for profile_name, info in profiles.items():
        profile_key = profile_name.split(" ", 1)[1]  # Remove emoji
        temperature = get_model_temperature(profile_key)
        system_prompt = get_system_prompt(profile_key)
        
        print(f"\n{profile_name}")
        print("-" * 60)
        print(f"Access Level: {info['access']}")
        print(f"Description: {info['description']}")
        print(f"Temperature: {temperature}")
        print(f"System Prompt: {system_prompt[:100]}...")
    
    print("\n" + "=" * 80)
    print("USAGE INSTRUCTIONS")
    print("=" * 80)
    print("1. Start the application: chainlit run app.py")
    print("2. Login with one of the demo accounts:")
    print("   - admin/admin123 (access to all 5 profiles)")
    print("   - user/user123 (access to 3 basic profiles)")  
    print("   - demo/demo123 (access to 3 basic profiles)")
    print("3. Select your preferred chat profile from the dropdown")
    print("4. Start chatting - the AI will respond according to the selected profile")
    print("=" * 80)

if __name__ == "__main__":
    demo_chat_profiles() 