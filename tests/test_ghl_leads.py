#!/usr/bin/env python3
"""
Test GHL Leads Integration
Simple script to test GHL lead fetching
"""

import json
from ghl_integration import GHLIntegration

def test_ghl_leads():
    """Test GHL lead fetching"""
    print("🧪 Testing GHL Leads Integration")
    print("=" * 40)
    
    # Load config using the new config system
    import sys
    import os
    sys.path.append('..')
    from src.setter_ai.utils.config import load_config
    config = load_config()
    
    # Initialize GHL integration
    ghl = GHLIntegration(config)
    
    print(f"🔧 GHL Configured: {ghl.is_configured()}")
    print(f"📍 Location ID: {ghl.location_id}")
    print(f"⏰ Hours Limit: {ghl.ghl_config.get('leads_hours_limit', 24)}")
    
    # Get leads
    print("\n📞 Fetching leads from GHL...")
    leads = ghl.get_leads()
    
    print(f"✅ Retrieved {len(leads)} leads")
    
    if leads:
        print("\n📋 Lead Details:")
        for i, lead in enumerate(leads[:5], 1):  # Show first 5 leads
            print(f"{i}. {lead.get('firstName', '')} {lead.get('lastName', '')}")
            print(f"   Company: {lead.get('companyName', 'N/A')}")
            print(f"   Phone: {lead.get('phone', 'N/A')}")
            print(f"   Email: {lead.get('email', 'N/A')}")
            print(f"   Source: {lead.get('source', 'unknown')}")
            print()
    else:
        print("❌ No leads found")
    
    # Test filtering
    print("🔍 Testing lead filtering...")
    called_lead_ids = ['dummy_1']  # Simulate called leads
    available_leads = ghl.filter_available_leads(leads, called_lead_ids)
    print(f"📊 Available leads: {len(available_leads)} out of {len(leads)} total")

if __name__ == "__main__":
    test_ghl_leads() 