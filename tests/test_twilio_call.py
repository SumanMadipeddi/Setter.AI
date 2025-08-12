#!/usr/bin/env python3
"""
Test Twilio Calling Functionality
Simple script to test Twilio phone calls
"""

import json
import requests
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

def load_config():
    """Load configuration using the new config system"""
    import sys
    import os
    sys.path.append('..')
    from src.setter_ai.utils.config import load_config as load_app_config
    return load_app_config()

def test_twilio_call():
    """Test making a Twilio call"""
    config = load_config()
    
    # Initialize Twilio client
    account_sid = config['twilio']['account_sid']
    auth_token = config['twilio']['auth_token']
    phone_number = config['twilio']['phone_number']
    
    client = Client(account_sid, auth_token)
    
    # Test phone number (replace with your number)
    test_number = input("Enter phone number to test (e.g., +16025659192): ")
    
    if not test_number.startswith('+1'):
        test_number = f"+1{test_number}"
    
    print(f"🔔 Making test call to {test_number}...")
    
    try:
        # Make the call
        call = client.calls.create(
            to=test_number,
            from_=phone_number,
            url=f"{config['webhook_base_url']}/test_webhook",
            record=True,
            status_callback=f"{config['webhook_base_url']}/call_status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"📞 Call SID: {call.sid}")
        print(f"📱 Status: {call.status}")
        print(f"⏱️  Duration: {call.duration if call.duration else 'N/A'}")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ Error making call: {str(e)}")
        return None

def test_webhook_response():
    """Test webhook response"""
    config = load_config()
    
    # Create a simple TwiML response
    response = VoiceResponse()
    response.say(
        "Hello! This is a test call from Setter.AI. Thank you for testing our system.",
        voice="en-US-Neural2-F",
        speech_rate="1.0"
    )
    
    print("🎤 Test webhook response created:")
    print(response)
    
    return str(response)

def check_call_status(call_sid):
    """Check the status of a call"""
    config = load_config()
    client = Client(config['twilio']['account_sid'], config['twilio']['auth_token'])
    
    try:
        call = client.calls(call_sid).fetch()
        print(f"📊 Call Status: {call.status}")
        print(f"⏱️  Duration: {call.duration} seconds")
        print(f"📞 From: {call.from_}")
        print(f"📱 To: {call.to}")
        
        if call.recording_url:
            print(f"🎵 Recording: {call.recording_url}")
        
        return call.status
        
    except Exception as e:
        print(f"❌ Error checking call status: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🧪 Twilio Call Test")
    print("=" * 40)
    
    while True:
        print("\nChoose an option:")
        print("1. Make a test call")
        print("2. Test webhook response")
        print("3. Check call status")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            call_sid = test_twilio_call()
            if call_sid:
                print(f"\n💡 Call SID for status check: {call_sid}")
        
        elif choice == '2':
            test_webhook_response()
        
        elif choice == '3':
            call_sid = input("Enter Call SID: ")
            if call_sid:
                check_call_status(call_sid)
        
        elif choice == '4':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 