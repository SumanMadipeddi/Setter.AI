"""
Configuration utilities for Setter.AI
====================================

Handles loading and managing application configuration from environment variables
and config.json file. Environment variables take priority over config.json.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_config():
    """Load configuration from environment variables first, then config.json as fallback"""
    try:
        # Start with empty config - environment variables take absolute priority
        config = {}
        
        # Try to load from config.json as fallback (only for non-sensitive defaults)
        config_path = Path(__file__).parent.parent.parent.parent / 'config.json'
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                print("📁 Loaded fallback configuration from config.json")
            except Exception as e:
                print(f"⚠️  Warning: Could not load config.json: {e}")
                config = {}
        
        # Override with environment variables (environment takes absolute priority)
        config = _merge_with_env_vars(config)
        
        # Validate that required API keys are present
        _validate_required_keys(config)
        
        return config
        
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {str(e)}")

def _merge_with_env_vars(config):
    """Merge config.json with environment variables (env vars take priority)"""
    
    # GHL Configuration
    if "ghl" not in config:
        config["ghl"] = {}
    
    config["ghl"]["api_key"] = os.getenv("GHL_API_KEY", config.get("ghl", {}).get("api_key", ""))
    config["ghl"]["location_id"] = os.getenv("GHL_LOCATION_ID", config.get("ghl", {}).get("location_id", ""))
    config["ghl"]["check_interval_minutes"] = int(os.getenv("LEAD_CHECK_INTERVAL_MINUTES", 
                                                           str(config.get("ghl", {}).get("check_interval_minutes", 10))))
    config["ghl"]["auto_call_enabled"] = os.getenv("AUTO_CALL_ENABLED", 
                                                   str(config.get("ghl", {}).get("auto_call_enabled", True))).lower() == "true"
    config["ghl"]["leads_hours_limit"] = int(os.getenv("LEADS_HOURS_LIMIT", 
                                                       str(config.get("ghl", {}).get("leads_hours_limit", 24))))
    
    # OpenAI Configuration
    if "openai" not in config:
        config["openai"] = {}
    config["openai"]["api_key"] = os.getenv("OPENAI_API_KEY", config.get("openai", {}).get("api_key", ""))
    
    # Twilio Configuration
    if "twilio" not in config:
        config["twilio"] = {}
    config["twilio"]["account_sid"] = os.getenv("TWILIO_ACCOUNT_SID", config.get("twilio", {}).get("account_sid", ""))
    config["twilio"]["auth_token"] = os.getenv("TWILIO_AUTH_TOKEN", config.get("twilio", {}).get("auth_token", ""))
    config["twilio"]["phone_number"] = os.getenv("TWILIO_PHONE_NUMBER", config.get("twilio", {}).get("phone_number", ""))
    
    # Webhook Configuration
    config["webhook_base_url"] = os.getenv("WEBHOOK_BASE_URL", config.get("webhook_base_url", "http://localhost:5000"))
    
    # Call Settings
    if "call_settings" not in config:
        config["call_settings"] = {}
    
    call_settings = config["call_settings"]
    call_settings["max_call_duration"] = int(os.getenv("MAX_CALL_DURATION", 
                                                      str(call_settings.get("max_call_duration", 300))))
    call_settings["retry_attempts"] = int(os.getenv("RETRY_ATTEMPTS", 
                                                   str(call_settings.get("retry_attempts", 2))))
    call_settings["call_delay_minutes"] = int(os.getenv("CALL_DELAY_MINUTES", 
                                                       str(call_settings.get("call_delay_minutes", 5))))
    call_settings["lead_check_interval_minutes"] = int(os.getenv("LEAD_CHECK_INTERVAL_MINUTES", 
                                                                str(call_settings.get("lead_check_interval_minutes", 10))))
    
    # Business Hours
    if "business_hours" not in call_settings:
        call_settings["business_hours"] = {}
    call_settings["business_hours"]["start"] = os.getenv("BUSINESS_HOURS_START", 
                                                        call_settings.get("business_hours", {}).get("start", "00:00"))
    call_settings["business_hours"]["end"] = os.getenv("BUSINESS_HOURS_END", 
                                                      call_settings.get("business_hours", {}).get("end", "23:59"))
    call_settings["business_hours"]["timezone"] = os.getenv("BUSINESS_HOURS_TIMEZONE", 
                                                           call_settings.get("business_hours", {}).get("timezone", "America/New_York"))
    
    # Voice Settings
    if "voice_settings" not in call_settings:
        call_settings["voice_settings"] = {}
    voice_settings = call_settings["voice_settings"]
    voice_settings["voice"] = os.getenv("VOICE_TYPE", voice_settings.get("voice", "en-US-Neural2-F"))
    voice_settings["speech_rate"] = os.getenv("SPEECH_RATE", voice_settings.get("speech_rate", "1.0"))
    voice_settings["pitch"] = os.getenv("VOICE_PITCH", voice_settings.get("pitch", "1.0"))
    voice_settings["volume"] = os.getenv("VOICE_VOLUME", voice_settings.get("volume", "1.0"))
    voice_settings["gender"] = os.getenv("VOICE_GENDER", voice_settings.get("gender", "female"))
    
    # Conversation Settings
    if "conversation_settings" not in call_settings:
        call_settings["conversation_settings"] = {}
    conv_settings = call_settings["conversation_settings"]
    conv_settings["speech_timeout"] = os.getenv("SPEECH_TIMEOUT", conv_settings.get("speech_timeout", "auto"))
    conv_settings["gather_timeout"] = int(os.getenv("GATHER_TIMEOUT", str(conv_settings.get("gather_timeout", 5))))
    conv_settings["language"] = os.getenv("CONVERSATION_LANGUAGE", conv_settings.get("language", "en-US"))
    conv_settings["speech_model"] = os.getenv("SPEECH_MODEL", conv_settings.get("speech_model", "phone_call"))
    conv_settings["interruption_threshold"] = float(os.getenv("INTERRUPTION_THRESHOLD", 
                                                             str(conv_settings.get("interruption_threshold", 0.5))))
    conv_settings["speech_timeout_seconds"] = float(os.getenv("SPEECH_TIMEOUT_SECONDS", 
                                                             str(conv_settings.get("speech_timeout_seconds", 1.5))))
    
    # AI Settings
    if "ai_settings" not in config:
        config["ai_settings"] = {}
    ai_settings = config["ai_settings"]
    ai_settings["model"] = os.getenv("AI_MODEL", ai_settings.get("model", "gpt-4"))
    ai_settings["max_tokens"] = int(os.getenv("AI_MAX_TOKENS", str(ai_settings.get("max_tokens", 150))))
    ai_settings["temperature"] = float(os.getenv("AI_TEMPERATURE", str(ai_settings.get("temperature", 0.7))))
    ai_settings["conversation_memory_turns"] = int(os.getenv("AI_CONVERSATION_MEMORY_TURNS", 
                                                            str(ai_settings.get("conversation_memory_turns", 5))))
    ai_settings["personality"] = os.getenv("AI_PERSONALITY", ai_settings.get("personality", "professional_friendly"))
    ai_settings["agent_name"] = os.getenv("AI_AGENT_NAME", ai_settings.get("agent_name", "Maayaa"))
    ai_settings["company_name"] = os.getenv("AI_COMPANY_NAME", ai_settings.get("company_name", "LoanCater"))
    ai_settings["contact_person"] = os.getenv("AI_CONTACT_PERSON", ai_settings.get("contact_person", "Ryan"))
    ai_settings["contact_email"] = os.getenv("AI_CONTACT_EMAIL", ai_settings.get("contact_email", "ryan@loancater.com"))
    
    return config

def get_webhook_url(endpoint=""):
    """Get webhook URL for external services"""
    try:
        config = load_config()
        ngrok_url = config.get('ngrok', {}).get('public_url', '')
        
        if not ngrok_url:
            return f"http://localhost:5000/{endpoint}".rstrip('/')
        
        return f"{ngrok_url}/{endpoint}".rstrip('/')
        
    except Exception as e:
        # Fallback to localhost
        return f"http://localhost:5000/{endpoint}".rstrip('/')

def get_config_value(key, default=None):
    """Get a specific configuration value"""
    try:
        config = load_config()
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
        
    except Exception:
        return default

def _validate_required_keys(config):
    """Validate that required API keys and configuration are present"""
    required_keys = [
        ("ghl.api_key", "GHL_API_KEY"),
        ("ghl.location_id", "GHL_LOCATION_ID"),
        ("openai.api_key", "OPENAI_API_KEY"),
        ("twilio.account_sid", "TWILIO_ACCOUNT_SID"),
        ("twilio.auth_token", "TWILIO_AUTH_TOKEN")
    ]
    
    missing_keys = []
    for config_path, env_var in required_keys:
        # Get value directly from config instead of calling get_config_value
        keys = config_path.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                value = None
                break
        
        if not value:
            missing_keys.append(f"{env_var} (config path: {config_path})")
    
    if missing_keys:
        error_msg = "❌ Missing required API keys:\n"
        error_msg += "\n".join(f"  - {key}" for key in missing_keys)
        error_msg += "\n\nPlease set these environment variables or add them to your .env file."
        error_msg += "\nSee .env.example for reference."
        raise RuntimeError(error_msg)
    
    print("✅ All required API keys are configured")

def get_environment_help():
    """Get help text for environment variable configuration"""
    return """
🔐 Environment Variable Configuration
====================================

Required API Keys (set these in your .env file or environment):
  GHL_API_KEY=your_ghl_api_key_here
  GHL_LOCATION_ID=your_location_id_here
  OPENAI_API_KEY=your_openai_api_key_here
  TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
  TWILIO_AUTH_TOKEN=your_twilio_auth_token_here

Optional Overrides:
  LEAD_CHECK_INTERVAL_MINUTES=10
  AUTO_CALL_ENABLED=true
  MAX_CALL_DURATION=300
  VOICE_TYPE=en-US-Neural2-F
  AI_MODEL=gpt-4
  BUSINESS_HOURS_START=09:00
  BUSINESS_HOURS_END=17:00

Security Notes:
  - NEVER commit .env files to version control
  - Environment variables take priority over config.json
  - Use .env.example as a template
  - Consider using a secrets manager for production
"""
