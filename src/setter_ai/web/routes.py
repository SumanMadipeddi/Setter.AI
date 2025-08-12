"""
Route handlers for Setter.AI web application
===========================================

Contains all the Flask route handlers for the dashboard and API endpoints.
"""

import sqlite3
import json
from datetime import datetime
from flask import jsonify, request, render_template
import logging

logger = logging.getLogger(__name__)

def register_routes(app, ai_logic, ghl_integration, twilio_integration, 
                   active_calls, call_history, db_path):
    """Register all routes with the Flask app"""
    
    @app.route('/', methods=['GET'])
    def dashboard_page():
        """Main dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/dashboard', methods=['GET'])
    def dashboard():
        """Dashboard API endpoint"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get call statistics
            cursor.execute('SELECT COUNT(*) FROM call_records')
            total_calls = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM call_records WHERE status IN ("initiated", "ringing", "active")')
            active_calls_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(duration) FROM call_records WHERE duration > 0')
            total_duration = cursor.fetchone()[0] or 0
            minutes_spoken = round(total_duration / 60, 1)
            
            cursor.execute('SELECT COUNT(*) FROM call_records WHERE status = "completed"')
            completed_calls = cursor.fetchone()[0]
            success_rate = round((completed_calls / total_calls * 100) if total_calls > 0 else 0, 1)
            
            cursor.execute('SELECT COUNT(*) FROM call_records WHERE meeting_email IS NOT NULL AND meeting_email != ""')
            meetings_scheduled = cursor.fetchone()[0]
            
            # Get recent calls
            cursor.execute('''
                SELECT call_id, lead_name, status, call_start_time, duration, call_sid
                FROM call_records 
                ORDER BY call_start_time DESC
                LIMIT 10
            ''')
            
            recent_calls = []
            for row in cursor.fetchall():
                call_data = {
                    'call_id': row[0],
                    'lead_name': row[1] or 'Unknown',
                    'status': row[2] or 'unknown',
                    'call_time': row[3],
                    'duration': row[4] or 0,
                    'call_sid': row[5] or ''
                }
                recent_calls.append(call_data)
            
            conn.close()
            
            return jsonify({
                'total_calls': total_calls,
                'active_calls': active_calls_count,
                'minutes_spoken': minutes_spoken,
                'success_rate': success_rate,
                'meetings_scheduled': meetings_scheduled,
                'recent_calls': recent_calls
            })
            
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/call_records/<call_id>', methods=['GET'])
    def get_call_record(call_id):
        """Get call record details"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT lead_name, status, conversation_data, recording_url, duration, call_start_time
                FROM call_records 
                WHERE call_id = ?
            ''', (call_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                # Get conversation from AI logic
                ai_conversation = ai_logic.get_conversation_history(call_id)
                
                return jsonify({
                    'call_id': call_id,
                    'lead_name': row[0],
                    'status': row[1],
                    'conversation_data': row[2] or '',
                    'ai_conversation': ai_conversation,
                    'recording_url': row[3] or '',
                    'duration': row[4] or 0,
                    'call_start_time': row[5]
                })
            else:
                return jsonify({'error': 'Call not found'}), 404
                
        except Exception as e:
            logger.error(f"Error getting call record: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/recording/<call_id>', methods=['GET'])
    def get_recording_url(call_id):
        """Get recording URL for a call"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT recording_url FROM call_records WHERE call_id = ?', (call_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0]:
                recording_sid = row[0]
                # Generate Twilio recording URL
                recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_integration.account_sid}/Recordings/{recording_sid}/Media"
                return jsonify({'recording_url': recording_url})
            else:
                return jsonify({'error': 'No recording available'}), 404
                
        except Exception as e:
            logger.error(f"Error getting recording URL: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/recording_media/<recording_sid>', methods=['GET'])
    def serve_recording_media(recording_sid):
        """Serve recording media file"""
        try:
            # Get recording media from Twilio
            recording_url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_integration.account_sid}/Recordings/{recording_sid}/Media"
            
            # For now, return the URL - in production you'd stream the audio
            return jsonify({'recording_url': recording_url})
            
        except Exception as e:
            logger.error(f"Error serving recording media: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/leads', methods=['GET'])
    def get_leads():
        """Get available leads from GHL"""
        try:
            leads = ghl_integration.get_leads()
            check_interval = ghl_integration.config.get('check_interval_minutes', 10)
            
            return jsonify({
                'leads': leads,
                'check_interval_minutes': check_interval
            })
            
        except Exception as e:
            logger.error(f"Error getting leads: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/make_call', methods=['POST'])
    def make_call_endpoint():
        """Manual call endpoint"""
        try:
            data = request.get_json()
            lead_id = data.get('lead_id')
            
            if not lead_id:
                return jsonify({'error': 'Lead ID required'}), 400
            
            # Get lead from GHL
            lead = ghl_integration.get_lead_by_id(lead_id)
            if not lead:
                return jsonify({'error': 'Lead not found'}), 404
            
            # Make call
            success = make_call(lead, ai_logic, ghl_integration, 
                              twilio_integration, active_calls, 
                              call_history, db_path)
            
            if success:
                return jsonify({'success': True, 'message': 'Call initiated'})
            else:
                return jsonify({'error': 'Failed to initiate call'}), 500
                
        except Exception as e:
            logger.error(f"Error making call: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/test_call', methods=['POST'])
    def test_call():
        """Test call endpoint"""
        try:
            data = request.get_json()
            phone_number = data.get('phone_number')
            
            if not phone_number:
                return jsonify({'error': 'Phone number required'}), 400
            
            # Create test lead
            test_lead = {
                'id': 'test',
                'firstName': 'Test',
                'lastName': 'User',
                'phone': phone_number
            }
            
            # Make test call
            success = make_call(test_lead, ai_logic, ghl_integration, 
                              twilio_integration, active_calls, 
                              call_history, db_path)
            
            if success:
                return jsonify({'success': True, 'message': 'Test call initiated'})
            else:
                return jsonify({'error': 'Failed to initiate test call'}), 500
                
        except Exception as e:
            logger.error(f"Error making test call: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/test_webhook', methods=['GET', 'POST'])
    def test_webhook():
        """Test webhook endpoint"""
        return jsonify({
            'status': 'success',
            'message': 'Webhook endpoint is working',
            'method': request.method,
            'data': request.get_json() if request.is_json else request.form.to_dict()
        })
    
    @app.route('/handle_call', methods=['POST'])
    def handle_call():
        """Handle incoming call from Twilio"""
        try:
            call_id = request.args.get('call_id', '')
            lead_id = request.args.get('lead_id', '')
            
            if not call_id:
                return jsonify({'error': 'Call ID required'}), 400
            
            # Get call info from memory or create if not exists
            if call_id not in call_history:
                call_info = {
                    'call_id': call_id,
                    'lead_id': lead_id,
                    'start_time': datetime.now(),
                    'status': 'initiated'
                }
                call_history[call_id] = call_info
            
            # Generate AI response
            lead_info = call_history[call_id].get('lead_info', {})
            ai_response = ai_logic.generate_response(lead_info, "", call_id)
            
            # Store AI response in conversation history
            ai_logic.store_ai_response(call_id, ai_response)
            
            # Return TwiML response
            twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{ai_response}</Say>
    <Record action="/handle_response?call_id={call_id}" 
            maxLength="30" 
            playBeep="true" 
            trim="trim-silence" />
</Response>'''
            
            return twiml_response, 200, {'Content-Type': 'text/xml'}
            
        except Exception as e:
            logger.error(f"Error handling call: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/handle_response', methods=['POST'])
    def handle_call_response():
        """Handle user response from Twilio"""
        try:
            call_id = request.args.get('call_id', '')
            
            if not call_id:
                return jsonify({'error': 'Call ID required'}), 400
            
            # Get user response
            user_response = request.form.get('SpeechResult', '')
            if not user_response:
                user_response = "User spoke but no text was captured"
            
            # Store user response
            ai_logic.store_user_response(call_id, user_response)
            
            # Generate AI response
            lead_info = call_history.get(call_id, {}).get('lead_info', {})
            ai_response = ai_logic.generate_response(lead_info, user_response, call_id)
            
            # Store AI response
            ai_logic.store_ai_response(call_id, ai_response)
            
            # Return TwiML response
            twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{ai_response}</Say>
    <Record action="/handle_response?call_id={call_id}" 
            maxLength="30" 
            playBeep="true" 
            trim="trim-silence" />
</Response>'''
            
            return twiml_response, 200, {'Content-Type': 'text/xml'}
            
        except Exception as e:
            logger.error(f"Error handling response: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/call_status', methods=['POST'])
    def handle_call_status():
        """Handle call status updates from Twilio"""
        try:
            call_id = request.args.get('call_id', '')
            call_sid = request.form.get('CallSid', '')
            call_status = request.form.get('CallStatus', '')
            recording_url = request.form.get('RecordingUrl', '')
            recording_sid = request.form.get('RecordingSid', '')
            
            # Find call_id if not in URL
            if not call_id and call_sid:
                for cid, info in call_history.items():
                    if info.get('call_sid') == call_sid:
                        call_id = cid
                        break
            
            if not call_id:
                # Try to find in database
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT call_id FROM call_records WHERE call_sid = ?', (call_sid,))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    call_id = row[0]
            
            if not call_id:
                logger.error(f"Could not find call_id for call_sid: {call_sid}")
                return jsonify({'error': 'Call ID not found'}), 400
            
            # Update call status
            status_mapping = {
                'initiated': 'initiated',
                'ringing': 'ringing',
                'answered': 'active',
                'completed': 'completed',
                'busy': 'busy',
                'failed': 'failed',
                'no-answer': 'no-answer',
                'canceled': 'canceled',
                'in-progress': 'active'
            }
            
            mapped_status = status_mapping.get(call_status, call_status)
            
            # Update call history
            if call_id in call_history:
                call_history[call_id]['status'] = mapped_status
                
                if mapped_status in ['completed', 'busy', 'failed', 'no-answer', 'canceled']:
                    if call_id in active_calls:
                        del active_calls[call_id]
            
            # Extract recording_sid from full URL if needed
            if recording_url and not recording_sid:
                # Extract recording_sid from URL
                if '/Recordings/' in recording_url:
                    recording_sid = recording_url.split('/Recordings/')[-1].split('/')[0]
            
            # Save to database
            call_result = {
                'status': mapped_status,
                'call_sid': call_sid,
                'conversation_data': '',
                'recording_url': recording_sid or '',
                'duration': 0
            }
            
            save_call_record(call_id, call_history.get(call_id, {}), call_result, db_path)
            
            # Direct database update for immediate status change
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE call_records 
                    SET status = ?, recording_url = ?
                    WHERE call_id = ?
                ''', (mapped_status, recording_sid or '', call_id))
                conn.commit()
                conn.close()
            except Exception as e:
                logger.error(f"Error updating call status in database: {str(e)}")
            
            return jsonify({'success': True, 'status': mapped_status})
            
        except Exception as e:
            logger.error(f"Error handling call status: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'active_calls': len(active_calls),
            'ghl_configured': ghl_integration.is_configured(),
            'twilio_configured': twilio_integration.is_configured(),
            'ai_configured': ai_logic.is_configured()
        })
    
    @app.route('/config', methods=['GET'])
    def get_config():
        """Get configuration for frontend"""
        return jsonify({
            'agent_name': ai_logic.config.get('agent_name', ''),
            'company_name': ai_logic.config.get('company_name', ''),
            'contact_person': ai_logic.config.get('contact_person', ''),
            'check_interval_minutes': ghl_integration.config.get('check_interval_minutes', 10)
        })
    
    @app.route('/debug_conversation/<call_id>', methods=['GET'])
    def debug_conversation(call_id):
        """Debug endpoint to check conversation data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT conversation_data, status, lead_name FROM call_records 
                WHERE call_id = ?
            ''', (call_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                conversation_data = row[0]
                status = row[1]
                lead_name = row[2]
                
                # Also get from AI logic
                ai_conversation = ai_logic.get_conversation_history(call_id)
                
                return jsonify({
                    'call_id': call_id,
                    'lead_name': lead_name,
                    'status': status,
                    'database_conversation_data': conversation_data,
                    'ai_logic_conversation': ai_conversation,
                    'ai_logic_conversation_length': len(ai_conversation),
                    'database_conversation_length': len(conversation_data) if conversation_data else 0
                })
            else:
                return jsonify({'error': 'Call not found'}), 404
                
        except Exception as e:
            logger.error(f"Error debugging conversation: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/debug_all_calls', methods=['GET'])
    def debug_all_calls():
        """Debug endpoint to check all calls and their conversation data"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT call_id, lead_name, status, conversation_data, recording_url, duration
                FROM call_records 
                ORDER BY call_start_time DESC
                LIMIT 10
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            calls_data = []
            for row in rows:
                call_id = row[0]
                ai_conversation = ai_logic.get_conversation_history(call_id)
                
                calls_data.append({
                    'call_id': call_id,
                    'lead_name': row[1],
                    'status': row[2],
                    'database_conversation_data': row[3],
                    'ai_logic_conversation_length': len(ai_conversation),
                    'database_conversation_length': len(row[3]) if row[3] else 0,
                    'recording_url': row[4],
                    'duration': row[5]
                })
            
            return jsonify({
                'total_calls': len(calls_data),
                'calls': calls_data
            })
            
        except Exception as e:
            logger.error(f"Error debugging all calls: {str(e)}")
            return jsonify({'error': str(e)}), 500
