"""
Flask Application Factory for Setter.AI
======================================

Creates and configures the Flask application with all routes and middleware.
"""

import os
import sqlite3
import threading
import time
from datetime import datetime
from flask import Flask, jsonify, request, render_template
import logging

from ..core.ai_logic import AILogic
from ..integrations.ghl_integration import GHLIntegration
from ..integrations.twilio_integration import TwilioIntegration
from ..utils.config import load_config, get_webhook_url
from ..utils.database import init_database, get_db_path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_overrides=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = load_config()
    if config_overrides:
        config.update(config_overrides)
    
    # Initialize components
    ai_logic = AILogic(config['ai_settings'])
    ghl_integration = GHLIntegration(config['ghl'])
    twilio_integration = TwilioIntegration(config['twilio'])
    
    # Initialize database
    db_path = get_db_path()
    init_database(db_path)
    
    # Global variables for call tracking
    active_calls = {}
    call_history = {}
    
    # Import routes after app creation to avoid circular imports
    from .routes import register_routes
    register_routes(app, ai_logic, ghl_integration, twilio_integration, 
                   active_calls, call_history, db_path)
    
    # Start background monitoring thread
    def start_monitoring_thread():
        """Background thread for monitoring leads every 10 minutes"""
        def monitor():
            while True:
                try:
                    # Get new leads from GHL
                    leads = ghl_integration.get_leads()
                    
                    # Filter out leads that have already been called
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT lead_id FROM called_leads')
                    called_lead_ids = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    
                    available_leads = ghl_integration.filter_available_leads(leads, called_lead_ids)
                    
                    if available_leads:
                        logger.info(f"Found {len(available_leads)} new leads to call")
                        
                        # Call the first available lead
                        lead = available_leads[0]
                        success = make_call(lead, ai_logic, ghl_integration, 
                                         twilio_integration, active_calls, 
                                         call_history, db_path)
                        
                        if success:
                            logger.info(f"Successfully initiated call to {lead.get('firstName', '')} {lead.get('lastName', '')}")
                        else:
                            logger.error(f"Failed to call {lead.get('firstName', '')} {lead.get('lastName', '')}")
                    else:
                        logger.info("No new leads to call")
                    
                    # Wait 10 minutes before next check
                    time.sleep(600)  # 10 minutes
                    
                except Exception as e:
                    logger.error(f"Error in monitoring thread: {str(e)}")
                    time.sleep(60)  # Wait 1 minute on error
        
        # Start monitoring thread
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        logger.info("GHL lead monitoring thread started (checking every 10 minutes)")
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=start_monitoring_thread, daemon=True)
    monitor_thread.start()
    
    return app

def make_call(lead, ai_logic, ghl_integration, twilio_integration, 
              active_calls, call_history, db_path):
    """Make a call to a lead"""
    try:
        # Generate unique call ID
        call_id = f"call_{int(time.time())}_{lead.get('id', 'unknown')}"
        
        # Make call via Twilio
        success, call_sid = twilio_integration.make_call(lead, call_id)
        
        if success:
            # Store call info in memory
            call_info = {
                'call_id': call_id,
                'call_sid': call_sid,
                'lead_info': lead,
                'start_time': datetime.now(),
                'status': 'initiated'
            }
            
            call_history[call_id] = call_info
            active_calls[call_id] = call_info
            
            # Save initial call record
            call_result = {
                'status': 'initiated',
                'call_sid': call_sid,
                'conversation_data': '',
                'recording_url': '',
                'duration': 0
            }
            
            save_call_record(call_id, call_info, call_result, db_path)
            
            # Mark lead as called
            ghl_integration.mark_lead_as_called(lead)
            
            logger.info(f"Call initiated successfully: {call_id} to {lead.get('firstName', '')} {lead.get('lastName', '')}")
            return True
        else:
            logger.error(f"Failed to initiate call to {lead.get('firstName', '')} {lead.get('lastName', '')}")
            return False
            
    except Exception as e:
        logger.error(f"Error making call: {str(e)}")
        return False

def save_call_record(call_id, call_info, call_result, db_path):
    """Save call record to database"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        lead_info = call_info.get('lead_info', {})
        lead_name = f"{lead_info.get('firstName', '')} {lead_info.get('lastName', '')}".strip()
        
        cursor.execute('''
            INSERT OR REPLACE INTO call_records 
            (call_id, lead_id, lead_name, phone_number, call_start_time, 
             status, conversation_data, recording_url, duration, call_sid)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            call_id,
            lead_info.get('id', ''),
            lead_name,
            lead_info.get('phone', ''),
            call_info.get('start_time', datetime.now()),
            call_result.get('status', ''),
            call_result.get('conversation_data', ''),
            call_result.get('recording_url', ''),
            call_result.get('duration', 0),
            call_result.get('call_sid', '')
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Call record saved: {call_id}")
        
    except Exception as e:
        logger.error(f"Error saving call record: {str(e)}")
