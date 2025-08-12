#!/usr/bin/env python3
"""
Twilio Integration Module
Handles all Twilio calling functionality and webhook management
"""

import json
import requests
import logging
import uuid
from datetime import datetime
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

logger = logging.getLogger(__name__)

class TwilioIntegration:
    """Twilio API integration class"""
    
    def __init__(self, config):
        """Initialize Twilio integration with config"""
        self.config = config
        self.twilio_config = config.get('twilio', {})
        self.account_sid = self.twilio_config.get('account_sid')
        self.auth_token = self.twilio_config.get('auth_token')
        self.phone_number = self.twilio_config.get('phone_number')
        self.webhook_base_url = config.get('webhook_base_url')
        
        # Initialize Twilio client
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials not configured")
    
    def make_call(self, lead, call_id=None):
        """Make a call to a lead"""
        try:
            if not self.client:
                logger.error("Twilio client not initialized")
                return False
            
            if not call_id:
                call_id = str(uuid.uuid4())
            
            phone_number = lead.get('phone', '')
            
            # Format phone number
            if not phone_number.startswith('+1'):
                phone_number = f"+1{phone_number}"
            
            # Create webhook URLs
            webhook_url = f"{self.webhook_base_url}/handle_call?call_id={call_id}&lead_id={lead.get('id', '')}"
            status_callback_url = f"{self.webhook_base_url}/call_status?call_id={call_id}"
            
            logger.info(f"Making call to {phone_number} with call_id: {call_id}")
            logger.info(f"Webhook URL: {webhook_url}")
            logger.info(f"Status callback URL: {status_callback_url}")
            
            # Make the call
            call = self.client.calls.create(
                to=phone_number,
                from_=self.phone_number,
                url=webhook_url,
                record=True,
                recording_status_callback=status_callback_url,
                status_callback=status_callback_url,
                status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
                timeout=30
            )
            
            logger.info(f"Call initiated successfully: {call.sid}")
            return True, call.sid
            
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            return False, None
    
    def check_call_status(self, call_sid):
        """Check the status of a call"""
        try:
            if not self.client:
                return None
            
            call = self.client.calls(call_sid).fetch()
            return {
                'status': call.status,
                'duration': call.duration,
                'from': call.from_,
                'to': call.to,
                'recording_url': call.recording_url,
                'price': call.price,
                'price_unit': call.price_unit
            }
            
        except Exception as e:
            logger.error(f"Error checking call status: {str(e)}")
            return None
    
    def get_recording_url(self, recording_sid):
        """Get authenticated recording URL"""
        try:
            if not self.account_sid or not self.auth_token:
                return None
            
            # Create authenticated URL with embedded credentials
            auth_url = f"https://{self.account_sid}:{self.auth_token}@api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Recordings/{recording_sid}/Media"
            
            # Also provide a direct URL for fallback
            direct_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Recordings/{recording_sid}/Media"
            
            return {
                'url': auth_url,
                'direct_url': direct_url,
                'recording_sid': recording_sid,
                'account_sid': self.account_sid
            }
            
        except Exception as e:
            logger.error(f"Error creating recording URL: {str(e)}")
            return None
    
    def serve_recording_media(self, recording_sid):
        """Serve recording media with proper authentication"""
        try:
            if not self.account_sid or not self.auth_token:
                return None
            
            # Create the Twilio API URL
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Recordings/{recording_sid}/Media"
            
            # Make authenticated request to Twilio
            response = requests.get(url, auth=(self.account_sid, self.auth_token))
            
            if response.status_code == 200:
                return {
                    'content': response.content,
                    'mimetype': 'audio/mpeg',
                    'filename': f'recording_{recording_sid}.mp3'
                }
            else:
                logger.error(f"Recording not found: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error serving recording media: {str(e)}")
            return None
    
    def create_voice_response(self, message, voice_settings=None):
        """Create a TwiML voice response"""
        try:
            response = VoiceResponse()
            
            if not voice_settings:
                voice_settings = self.config.get('call_settings', {}).get('voice_settings', {})
            
            # Create Gather for speech input
            gather = Gather(
                input='speech',
                timeout=voice_settings.get('gather_timeout', 5),
                speech_timeout=voice_settings.get('speech_timeout_seconds', 1.5),
                language=voice_settings.get('language', 'en-US'),
                speech_model=voice_settings.get('speech_model', 'phone_call')
            )
            
            # Add message with voice settings
            gather.say(
                message,
                voice=voice_settings.get('voice', 'en-US-Neural2-F'),
                speech_rate=voice_settings.get('speech_rate', '1.0'),
                pitch=voice_settings.get('pitch', '1.0')
            )
            
            response.append(gather)
            
            # Add fallback message
            response.say(
                "Thank you for your time. We'll follow up with you soon.",
                voice=voice_settings.get('voice', 'en-US-Neural2-F')
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error creating voice response: {str(e)}")
            # Return simple fallback response
            response = VoiceResponse()
            response.say("Thank you for your time. We'll follow up with you soon.")
            return response
    
    def test_connection(self):
        """Test Twilio connection"""
        try:
            if not self.client:
                return False
            
            # Try to get account info
            account = self.client.api.accounts(self.account_sid).fetch()
            logger.info(f"Twilio connection successful: {account.friendly_name}")
            return True
            
        except Exception as e:
            logger.error(f"Twilio connection failed: {str(e)}")
            return False
    
    def get_account_info(self):
        """Get Twilio account information"""
        try:
            if not self.client:
                return None
            
            account = self.client.api.accounts(self.account_sid).fetch()
            return {
                'account_sid': account.sid,
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type,
                'phone_number': self.phone_number
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def is_configured(self):
        """Check if Twilio is properly configured"""
        return bool(self.account_sid and self.auth_token and self.phone_number)
    
    def get_config_info(self):
        """Get configuration information"""
        return {
            'configured': self.is_configured(),
            'account_sid': self.account_sid,
            'phone_number': self.phone_number,
            'webhook_base_url': self.webhook_base_url
        } 