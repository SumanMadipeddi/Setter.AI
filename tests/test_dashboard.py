#!/usr/bin/env python3
"""
Test Dashboard Endpoints
Simple script to test dashboard functionality
"""

import requests
import json

def test_dashboard():
    """Test dashboard endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Dashboard Endpoints")
    print("=" * 40)
    
    # Test dashboard data
    try:
        response = requests.get(f"{base_url}/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data: {len(data.get('recent_calls', []))} recent calls")
            print(f"📊 Total calls: {data.get('total_calls', 0)}")
            print(f"📞 Active calls: {data.get('active_calls', 0)}")
        else:
            print(f"❌ Dashboard error: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
    
    # Test leads endpoint
    try:
        response = requests.get(f"{base_url}/leads")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Leads data: {len(data.get('leads', []))} leads available")
            print(f"📊 Called count: {data.get('called_count', 0)}")
        else:
            print(f"❌ Leads error: {response.status_code}")
    except Exception as e:
        print(f"❌ Leads error: {str(e)}")
    
    # Test config endpoint
    try:
        response = requests.get(f"{base_url}/config")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Config loaded: {data.get('agent_name', 'Unknown')}")
        else:
            print(f"❌ Config error: {response.status_code}")
    except Exception as e:
        print(f"❌ Config error: {str(e)}")

if __name__ == "__main__":
    test_dashboard() 