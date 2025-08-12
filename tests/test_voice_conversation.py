#!/usr/bin/env python3
"""
Test Voice Conversation Functionality
Interactive test for AI voice conversations
"""

import json
import openai
from datetime import datetime

def load_config():
    """Load configuration using the new config system"""
    import sys
    import os
    sys.path.append('..')
    from src.setter_ai.utils.config import load_config as load_app_config
    return load_app_config()

def test_ai_conversation():
    """Test AI conversation generation"""
    config = load_config()
    
    # Initialize OpenAI
    openai.api_key = config['openai']['api_key']
    
    # Test lead information
    test_lead = {
        'firstName': 'John',
        'lastName': 'Doe',
        'companyName': 'Test Company',
        'email': 'john@testcompany.com',
        'phone': '6025659192'
    }
    
    print("🎤 Testing AI Conversation Generation")
    print("=" * 50)
    
    # Test different conversation stages
    stages = [
        "Initial greeting",
        "Qualification questions", 
        "Interest assessment",
        "Meeting scheduling"
    ]
    
    for i, stage in enumerate(stages):
        print(f"\n📝 Stage {i+1}: {stage}")
        print("-" * 30)
        
        # Generate AI response
        context = f"Conversation stage: {stage}"
        response = generate_ai_response(test_lead, context, "test_call")
        
        print(f"🤖 AI Response: {response}")
        print(f"⏱️  Generated at: {datetime.now().strftime('%H:%M:%S')}")
        
        # Simulate user response
        user_response = input(f"\n💬 Simulate user response (or press Enter to continue): ")
        if user_response.lower() in ['quit', 'exit', 'q']:
            break

def generate_ai_response(lead_info, context="", call_id=""):
    """Generate AI response (simplified version)"""
    config = load_config()
    
    lead_name = f"{lead_info.get('firstName', '')} {lead_info.get('lastName', '')}".strip()
    conversation_length = 0  # Simplified for testing
    
    # Get AI settings
    agent_name = config['ai_settings']['agent_name']
    company_name = config['ai_settings']['company_name']
    contact_person = config['ai_settings']['contact_person']
    
    if conversation_length == 0:
        system_prompt = f"""You are {agent_name}, calling on behalf of {contact_person} from {company_name}.
        
        Start with a brief, warm introduction: "Hi {lead_name}, this is {agent_name} calling on behalf of {contact_person} from {company_name}."
        Then ask if they have a quick moment to discuss business financing.
        
        Keep it short and natural - like a real person talking.
        Don't give long speeches. Just introduce yourself and ask for their time.
        Speak quickly and efficiently - no gaps or delays.
        Respond immediately without hesitation."""
    
    elif conversation_length <= 2:
        system_prompt = f"""You are {agent_name} from {company_name}. Keep responses short and conversational.
        
        Ask ONE question at a time:
        - "What type of financing are you looking for?"
        - "What's the purpose of the loan?"
        - "What amount are you considering?"
        
        Listen to their response and ask follow-up questions naturally.
        If they ask about {company_name}, give brief, helpful answers:
        - "We offer business loans from $5K to $500K"
        - "Rates start at 8%"
        - "Approval in 24-48 hours"
        
        Be conversational, not scripted. Speak quickly and efficiently.
        Respond immediately without delays."""
    
    else:
        system_prompt = f"""You are {agent_name} from {company_name}. {lead_name} is interested.
        
        Move to scheduling naturally:
        - "When would be a good time for {contact_person} to call you?"
        - Don't ask for email - use the email from their lead profile
        - Schedule the meeting and say {contact_person} will send calendar invite
        
        Keep it simple and direct.
        Don't over-explain.
        Speak quickly and efficiently.
        Respond immediately without delays."""
    
    # Create messages for OpenAI
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}. Generate a natural response."}
    ]
    
    try:
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model=config['ai_settings']['model'],
            messages=messages,
            max_tokens=config['ai_settings']['max_tokens'],
            temperature=config['ai_settings']['temperature']
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error generating response: {str(e)}"

def test_voice_settings():
    """Test different voice settings"""
    config = load_config()
    
    print("\n🎵 Testing Voice Settings")
    print("=" * 30)
    
    voice_settings = config['call_settings']['voice_settings']
    
    print(f"🔊 Voice: {voice_settings['voice']}")
    print(f"⚡ Speech Rate: {voice_settings['speech_rate']}")
    print(f"🎚️  Pitch: {voice_settings['pitch']}")
    print(f"🔊 Volume: {voice_settings['volume']}")
    print(f"👤 Gender: {voice_settings.get('gender', 'Not specified')}")
    
    # Test different speech rates
    test_phrases = [
        "Hello, this is a test of the voice system.",
        "We offer business loans from five thousand to five hundred thousand dollars.",
        "Our approval process takes twenty-four to forty-eight hours."
    ]
    
    print(f"\n📝 Test Phrases:")
    for i, phrase in enumerate(test_phrases, 1):
        print(f"{i}. {phrase}")

def test_conversation_flow():
    """Test complete conversation flow"""
    config = load_config()
    
    print("\n🔄 Testing Complete Conversation Flow")
    print("=" * 40)
    
    # Simulate a complete conversation
    conversation = [
        ("AI", "Hi John, this is Maayaa calling on behalf of Ryan from LoanCater. Do you have a quick moment to discuss business financing?"),
        ("User", "Yes, I'm interested in a business loan."),
        ("AI", "Great! What type of financing are you looking for?"),
        ("User", "I need equipment financing for my restaurant."),
        ("AI", "Equipment financing might be perfect for you. What amount are you considering?"),
        ("User", "Around $50,000 for kitchen equipment."),
        ("AI", "That's a good amount. When would be a good time for Ryan to call you to discuss the details?"),
        ("User", "Tomorrow at 3 PM would work."),
        ("AI", "Perfect! I've scheduled your meeting with Ryan for 3:00 PM MST tomorrow. You'll receive a calendar invite shortly.")
    ]
    
    print("📞 Simulated Conversation:")
    for speaker, message in conversation:
        print(f"\n{speaker}: {message}")
    
    print(f"\n✅ Conversation completed successfully!")
    print(f"📅 Meeting scheduled for tomorrow at 3:00 PM MST")

def main():
    """Main test function"""
    config = load_config()
    
    print("🎤 Voice Conversation Test")
    print("=" * 40)
    print(f"🤖 AI Agent: {config['ai_settings']['agent_name']}")
    print(f"🏢 Company: {config['ai_settings']['company_name']}")
    print(f"👤 Contact: {config['ai_settings']['contact_person']}")
    
    while True:
        print("\nChoose a test:")
        print("1. Test AI conversation generation")
        print("2. Test voice settings")
        print("3. Test complete conversation flow")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            test_ai_conversation()
        
        elif choice == '2':
            test_voice_settings()
        
        elif choice == '3':
            test_conversation_flow()
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 