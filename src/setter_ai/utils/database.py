"""
Database utilities for Setter.AI
===============================

Handles database initialization and common operations.
"""

import os
import sqlite3
from pathlib import Path

def get_db_path():
    """Get the database file path"""
    db_dir = Path(__file__).parent.parent.parent.parent
    return db_dir / 'data' / 'call_records.db'

def init_database(db_path):
    """Initialize the database with required tables"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create call_records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_records (
                call_id TEXT PRIMARY KEY,
                lead_id TEXT,
                lead_name TEXT,
                phone_number TEXT,
                call_start_time DATETIME,
                call_end_time DATETIME,
                status TEXT,
                conversation_data TEXT,
                recording_url TEXT,
                duration INTEGER DEFAULT 0,
                call_sid TEXT,
                meeting_email TEXT,
                meeting_date TEXT,
                meeting_time TEXT,
                notes TEXT
            )
        ''')
        
        # Add call_sid column if it doesn't exist (for backward compatibility)
        try:
            cursor.execute('ALTER TABLE call_records ADD COLUMN call_sid TEXT')
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
        # Create called_leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS called_leads (
                lead_id TEXT PRIMARY KEY,
                call_id TEXT,
                call_date DATETIME,
                status TEXT,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("Database initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def get_connection(db_path):
    """Get a database connection"""
    return sqlite3.connect(db_path)

def execute_query(db_path, query, params=None):
    """Execute a database query"""
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        
        return result
        
    except Exception as e:
        print(f"Database query error: {str(e)}")
        raise

def execute_update(db_path, query, params=None):
    """Execute a database update/insert"""
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Database update error: {str(e)}")
        raise
