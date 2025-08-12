#!/usr/bin/env python3
"""
GHL (GoHighLevel) Integration Module
Handles all GHL API interactions for lead management
"""

import json
import requests
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GHLIntegration:
    """GoHighLevel API integration class"""
    
    def __init__(self, config):
        """Initialize GHL integration with config"""
        self.config = config
        self.ghl_config = config.get('ghl', {})
        self.api_key = self.ghl_config.get('api_key')
        self.location_id = self.ghl_config.get('location_id')
        self.check_interval = self.ghl_config.get('check_interval_minutes', 10)
        self.auto_call_enabled = self.ghl_config.get('auto_call_enabled', True)
        
        if not self.api_key or not self.location_id:
            logger.warning("GHL credentials not configured")
    
    def get_leads(self):
        """Fetch leads from GHL API"""
        try:
            if not self.api_key or not self.location_id:
                logger.warning("GHL credentials not configured, using dummy leads")
                return self.get_dummy_leads()
            
            # GHL API endpoint for contacts - using the correct endpoint
            url = f"https://rest.gohighlevel.com/v1/contacts/"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Add query parameters for location and limit
            params = {
                'locationId': self.location_id,
                'limit': 100,  # Get up to 100 contacts
                'skip': 0
            }
            
            logger.info(f"Fetching leads from GHL API: {url}")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                leads = []
                
                # Get hours limit from config (convert check interval to hours)
                check_interval_hours = self.check_interval / 60.0  # Convert minutes to hours
                cutoff_time = datetime.now() - timedelta(hours=check_interval_hours)
                
                logger.info(f"Filtering leads from last {check_interval_hours:.1f} hours (check interval: {self.check_interval} minutes)")
                
                for contact in data.get('contacts', []):
                    # Check if lead was created within the time limit
                    created_at = contact.get('createdAt')
                    if created_at:
                        try:
                            lead_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            if lead_time < cutoff_time:
                                continue  # Skip leads older than the check interval
                        except:
                            # If date parsing fails, include the lead
                            pass
                    
                    # Only get leads that haven't been called yet
                    lead = {
                        'id': contact.get('id'),
                        'firstName': contact.get('firstName', ''),
                        'lastName': contact.get('lastName', ''),
                        'email': contact.get('email', ''),
                        'phone': contact.get('phone', ''),
                        'companyName': contact.get('companyName', ''),
                        'customField': contact.get('customField', {}),
                        'source': 'ghl',
                        'created_at': contact.get('createdAt'),
                        'updated_at': contact.get('updatedAt')
                    }
                    leads.append(lead)
                
                logger.info(f"Retrieved {len(leads)} leads from GHL (last {check_interval_hours:.1f} hours)")
                return leads
            else:
                logger.error(f"GHL API error: {response.status_code} - {response.text}")
                return self.get_dummy_leads()
                
        except Exception as e:
            logger.error(f"Error getting leads from GHL: {str(e)}")
            return self.get_dummy_leads()
    
    def get_dummy_leads(self):
        """Get dummy leads for testing"""
        return self.config.get('dummy_leads', [])
    
    def filter_available_leads(self, leads, called_lead_ids):
        """Filter out leads that have already been called"""
        available_leads = [lead for lead in leads if lead.get('id') not in called_lead_ids]
        logger.info(f"Found {len(available_leads)} available leads out of {len(leads)} total")
        return available_leads
    
    def update_lead_status(self, lead_id, status, outcome=None):
        """Update lead status in GHL (if needed)"""
        try:
            if not self.api_key or not self.location_id:
                return False
            
            # GHL API endpoint for updating contact
            url = f"https://rest.gohighlevel.com/v1/contacts/{lead_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Update custom fields to track call status
            data = {
                'customField': {
                    'c_call_status': status,
                    'c_call_outcome': outcome or 'unknown',
                    'c_last_called': datetime.now().isoformat()
                }
            }
            
            response = requests.put(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Updated lead {lead_id} status to {status}")
                return True
            else:
                logger.error(f"Failed to update lead {lead_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating lead status: {str(e)}")
            return False
    
    def get_lead_by_id(self, lead_id):
        """Get specific lead by ID"""
        try:
            if not self.api_key or not self.location_id:
                return None
            
            url = f"https://rest.gohighlevel.com/v1/contacts/{lead_id}"
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                contact = response.json()
                return {
                    'id': contact.get('id'),
                    'firstName': contact.get('firstName', ''),
                    'lastName': contact.get('lastName', ''),
                    'email': contact.get('email', ''),
                    'phone': contact.get('phone', ''),
                    'companyName': contact.get('companyName', ''),
                    'customField': contact.get('customField', {}),
                    'source': 'ghl'
                }
            else:
                logger.error(f"Failed to get lead {lead_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting lead {lead_id}: {str(e)}")
            return None
    
    def is_configured(self):
        """Check if GHL is properly configured"""
        return bool(self.api_key and self.location_id)
    
    def get_config_info(self):
        """Get configuration information"""
        return {
            'configured': self.is_configured(),
            'location_id': self.location_id,
            'check_interval': self.check_interval,
            'auto_call_enabled': self.auto_call_enabled
        } 