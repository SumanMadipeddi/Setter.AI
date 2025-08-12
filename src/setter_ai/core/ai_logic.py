#!/usr/bin/env python3
"""
AI Logic Module
Handles all AI conversation generation and response logic
"""

import json
import logging
import openai
from datetime import datetime

logger = logging.getLogger(__name__)

class AILogic:
    """AI conversation logic class"""
    
    def __init__(self, config):
        """Initialize AI logic with config"""
        self.config = config
        self.ai_config = config.get('ai_settings', {})
        self.openai_api_key = config.get('openai', {}).get('api_key')
        
        # Initialize OpenAI
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        else:
            logger.warning("OpenAI API key not configured")
        
        # AI settings
        self.model = self.ai_config.get('model', 'gpt-4')
        self.max_tokens = self.ai_config.get('max_tokens', 150)
        self.temperature = self.ai_config.get('temperature', 0.7)
        self.conversation_memory_turns = self.ai_config.get('conversation_memory_turns', 5)
        
        # Agent settings
        self.agent_name = self.ai_config.get('agent_name', 'Maayaa')
        self.company_name = self.ai_config.get('company_name', 'LoanCater')
        self.contact_person = self.ai_config.get('contact_person', 'Ryan')
        self.contact_email = self.ai_config.get('contact_email', 'ryan@loancater.com')
        
        # Conversation memory
        self.conversation_memory = {}
    
    def generate_response(self, lead_info, context="", call_id=""):
        """Generate AI response based on conversation context"""
        try:
            lead_name = f"{lead_info.get('firstName', '')} {lead_info.get('lastName', '')}".strip()
            conversation_history = self.conversation_memory.get(call_id, [])
            conversation_length = len(conversation_history)
            
            # Build system prompt based on conversation stage
            system_prompt = self._build_system_prompt(lead_name, conversation_length)
            
            # Build conversation context
            messages = self._build_messages(system_prompt, context, conversation_history)
            
            # Generate response
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Store in conversation memory
            if call_id:
                if call_id not in self.conversation_memory:
                    self.conversation_memory[call_id] = []
                
                self.conversation_memory[call_id].append({
                    'speaker': self.agent_name,
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"Generated AI response for {lead_name}: {ai_response[:50]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I apologize, but I'm having trouble processing that right now. Could you please repeat?"
    
    def _build_system_prompt(self, lead_name, conversation_length):
        """Build system prompt based on conversation stage"""
        if conversation_length == 0:
            # Initial greeting
            return f"""You are {self.agent_name}, calling on behalf of {self.contact_person} from {self.company_name}.
            
            Start with a brief, warm introduction: "Hi {lead_name}, this is {self.agent_name} calling on behalf of {self.contact_person} from {self.company_name}."
            Then ask if they have a quick moment to discuss business financing.
            
            Keep it short and natural - like a real person talking.
            Don't give long speeches. Just introduce yourself and ask for their time.
            Speak quickly and efficiently - no gaps or delays.
            Respond immediately without hesitation."""
        
        elif conversation_length <= 2:
            # Qualification stage
            return f"""You are {self.agent_name} from {self.company_name}. Keep responses short and conversational.
            
            Ask ONE question at a time:
            - "What type of financing are you looking for?"
            - "What's the purpose of the loan?"
            - "What amount are you considering?"
            
            Listen to their response and ask follow-up questions naturally.
            If they ask about {self.company_name}, give brief, helpful answers:
            - "We offer business loans from $5K to $500K"
            - "Rates start at 8%"
            - "Approval in 24-48 hours"
            
            Be conversational, not scripted. Speak quickly and efficiently.
            Respond immediately without delays."""
        
        else:
            # Scheduling stage
            return f"""You are {self.agent_name} from {self.company_name}. {lead_name} is interested.
            
            Move to scheduling naturally:
            - "When would be a good time for {self.contact_person} to call you?"
            - Don't ask for email - use the email from their lead profile
            - Schedule the meeting and say {self.contact_person} will send calendar invite
            
            Keep it simple and direct.
            Don't over-explain.
            Speak quickly and efficiently.
            Respond immediately without delays."""
    
    def _build_messages(self, system_prompt, context, conversation_history):
        """Build messages for OpenAI API"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last few exchanges)
        for msg in conversation_history[-self.conversation_memory_turns * 2:]:
            role = "assistant" if msg['speaker'] == self.agent_name else "user"
            messages.append({"role": role, "content": msg['content']})
        
        # Add current context
        if context:
            messages.append({"role": "user", "content": f"Context: {context}"})
        
        return messages
    
    def store_user_response(self, call_id, user_response):
        """Store user response in conversation memory"""
        if call_id:
            if call_id not in self.conversation_memory:
                self.conversation_memory[call_id] = []
            
            self.conversation_memory[call_id].append({
                'speaker': 'Caller',
                'content': user_response,
                'timestamp': datetime.now().isoformat()
            })
    
    def analyze_conversation_outcome(self, call_id):
        """Analyze conversation for positive/negative outcomes"""
        try:
            conversation = self.conversation_memory.get(call_id, [])
            
            # Keywords for analysis
            positive_keywords = [
                'interested', 'yes', 'sure', 'okay', 'good', 'great', 'perfect',
                'meeting', 'schedule', 'tomorrow', 'call back', 'definitely',
                'absolutely', 'of course', 'sounds good', 'that works'
            ]
            
            negative_keywords = [
                'not interested', 'no thanks', 'busy', 'not now', 'later',
                'not available', 'don\'t call', 'stop calling', 'not interested',
                'no time', 'too busy', 'maybe later'
            ]
            
            meeting_keywords = [
                'meeting', 'schedule', 'tomorrow', '3 p.m.', '3 pm', 'appointment',
                'call back', 'follow up', 'set up', 'book'
            ]
            
            # Analyze user responses
            user_responses = [msg['content'].lower() for msg in conversation if msg['speaker'] == 'Caller']
            
            positive_response = any(
                any(keyword in response for keyword in positive_keywords)
                for response in user_responses
            )
            
            negative_response = any(
                any(keyword in response for keyword in negative_keywords)
                for response in user_responses
            )
            
            meeting_scheduled = any(
                any(keyword in msg['content'].lower() for keyword in meeting_keywords)
                for msg in conversation if msg['speaker'] == self.agent_name
            )
            
            # Determine outcome
            if positive_response and meeting_scheduled:
                outcome = 'positive_meeting'
            elif positive_response:
                outcome = 'positive'
            elif negative_response:
                outcome = 'negative'
            else:
                outcome = 'neutral'
            
            return {
                'outcome': outcome,
                'positive_response': positive_response,
                'negative_response': negative_response,
                'meeting_scheduled': meeting_scheduled,
                'conversation_length': len(conversation)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing conversation outcome: {str(e)}")
            return {
                'outcome': 'unknown',
                'positive_response': False,
                'negative_response': False,
                'meeting_scheduled': False,
                'conversation_length': 0
            }
    
    def extract_meeting_details(self, call_id):
        """Extract meeting details from conversation"""
        try:
            conversation = self.conversation_memory.get(call_id, [])
            meeting_time = None
            
            # Look for time mentions in conversation
            for msg in conversation:
                if msg['speaker'] == 'Caller':
                    content = msg['content'].lower()
                    if any(time_word in content for time_word in ['pm', 'am', 'o\'clock', 'hour', 'tomorrow', 'today', 'week', '3 p.m.', '3 pm', '3:00']):
                        meeting_time = msg['content']
                        break
            
            # Also check agent's messages for meeting confirmations
            for msg in conversation:
                if msg['speaker'] == self.agent_name:
                    content = msg['content'].lower()
                    if any(keyword in content for keyword in ['tomorrow', '3 p.m.', '3 pm', 'schedule', 'meeting']):
                        if '3 p.m.' in content or '3 pm' in content:
                            meeting_time = '3:00 PM MST'
                        elif 'tomorrow' in content:
                            meeting_time = 'Tomorrow (Time TBD)'
                        break
            
            return meeting_time
            
        except Exception as e:
            logger.error(f"Error extracting meeting details: {str(e)}")
            return None
    
    def get_conversation_history(self, call_id):
        """Get conversation history for a call"""
        return self.conversation_memory.get(call_id, [])
    
    def clear_conversation(self, call_id):
        """Clear conversation memory for a call"""
        if call_id in self.conversation_memory:
            del self.conversation_memory[call_id]
    
    def is_configured(self):
        """Check if AI is properly configured"""
        return bool(self.openai_api_key)
    
    def get_config_info(self):
        """Get configuration information"""
        return {
            'configured': self.is_configured(),
            'model': self.model,
            'agent_name': self.agent_name,
            'company_name': self.company_name,
            'contact_person': self.contact_person
        } 