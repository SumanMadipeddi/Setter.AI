"""
Setter.AI - AI-Powered Lead Calling System
==========================================

A professional AI system that automatically calls leads with natural voice conversations.
"""

__version__ = "1.0.0"
__author__ = "Setter.AI Team"
__description__ = "AI-Powered Lead Calling System with Professional Voice"

from .core.ai_logic import AILogic
from .integrations.ghl_integration import GHLIntegration
from .integrations.twilio_integration import TwilioIntegration
from .web.app import create_app

__all__ = [
    'AILogic',
    'GHLIntegration', 
    'TwilioIntegration',
    'create_app'
]
