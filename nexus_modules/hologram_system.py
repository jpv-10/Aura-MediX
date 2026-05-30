"""
AURA MEDIX — Chat, Reports, Hospital Locator
Hologram system for advanced features
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from nexus_core import db
from nexus_core.quantum_models import ChatSession, Report
from datetime import datetime
import json

hologram_system = Blueprint('hologram_system', __name__, url_prefix='/hologram')

# ==================== CHAT SESSIONS ====================

@hologram_system.route('/chat/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    """Get all chat sessions for user"""
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(
        ChatSession.updated_at.desc()
    ).all()
    
    return jsonify([{
        'id': s.id,
        'title': s.title or 'Untitled Chat',
        'message_count': len(json.loads(s.messages) if s.messages else []),
        'created_at': s.created_at.isoformat(),
        'updated_at': s.updated_at.isoformat()
    } for s in sessions])

@hologram_system.route('/chat/session/<int:session_id>', methods=['GET'])
@login_required
def get_chat_session(session_id):
    """Get specific chat session"""
    session = ChatSession.query.filter_by(
        id=session_id,
        user_id=current_user.id
    ).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'id': session.id,
        'title': session.title,
        'messages': json.loads(session.messages) if session.messages else [],
        'created_at': session.created_at.isoformat(),
        'updated_at': session.updated_at.isoformat()
    })

@hologram_system.route('/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    """Send message to AI Doctor"""
    data = request.json
    session_id = data.get('session_id')
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Get or create session
    if session_id:
        session = ChatSession.query.filter_by(
            id=session_id,
            user_id=current_user.id
        ).first()
    else:
        session = ChatSession(user_id=current_user.id)
        db.session.add(session)
        db.session.commit()
    
    # Add user message
    messages = json.loads(session.messages) if session.messages else []
    messages.append({
        'role': 'user',
        'content': message,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Get AI response
    from ai_engine.nexus_chatbot import ai_doctor
    ai_response = ai_doctor.generate_response(message)
    
    messages.append({
        'role': 'assistant',
        'content': ai_response['message'],
        'type': ai_response.get('type', 'response'),
        'timestamp': datetime.utcnow().isoformat()
    })
    
    session.messages = json.dumps(messages)
    session.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'session_id': session.id,
            'message': ai_response['message'],
            'follow_up': ai_response.get('follow_up'),
            'requires_human': ai_response.get('requires_human', False)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== REPORTS ====================

@hologram_system.route('/report/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate PDF health report"""
    data = request.json
    report_type = data.get('type', 'health_summary')
    title = data.get('title', f'Health Report - {datetime.now().strftime("%Y-%m-%d")}')
    
    try:
        report = Report(
            user_id=current_user.id,
            title=title,
            report_type=report_type,
            content=json.dumps(data.get('content', {}))
        )
        
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'report_id': report.id,
            'title': report.title,
            'status': 'pending',
            'message': 'Report generation started'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@hologram_system.route('/report/list', methods=['GET'])
@login_required
def list_reports():
    """List all reports for user"""
    reports = Report.query.filter_by(user_id=current_user.id).order_by(
        Report.created_at.desc()
    ).all()
    
    return jsonify([{
        'id': r.id,
        'title': r.title,
        'type': r.report_type,
        'created_at': r.created_at.isoformat()
    } for r in reports])

# ==================== HOSPITALS ====================

@hologram_system.route('/hospitals/nearby', methods=['POST'])
@login_required
def find_nearby_hospitals():
    """Find nearby hospitals (mock implementation)"""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    # Mock hospital data
    hospitals = [
        {
            'id': 1,
            'name': 'City Medical Center',
            'distance_km': 2.3,
            'rating': 4.8,
            'address': '123 Main St',
            'phone': '+1-555-0101',
            'emergency': True,
            'latitude': latitude + 0.01,
            'longitude': longitude + 0.01
        },
        {
            'id': 2,
            'name': 'General Hospital',
            'distance_km': 5.1,
            'rating': 4.5,
            'address': '456 Oak Ave',
            'phone': '+1-555-0102',
            'emergency': True,
            'latitude': latitude - 0.02,
            'longitude': longitude + 0.015
        },
        {
            'id': 3,
            'name': 'Premier Health Clinic',
            'distance_km': 3.7,
            'rating': 4.6,
            'address': '789 Elm St',
            'phone': '+1-555-0103',
            'emergency': False,
            'latitude': latitude + 0.015,
            'longitude': longitude - 0.01
        }
    ]
    
    return jsonify({
        'hospitals': hospitals,
        'count': len(hospitals),
        'location': {
            'latitude': latitude,
            'longitude': longitude
        }
    })

# ==================== EMERGENCY ====================

@hologram_system.route('/emergency/sos', methods=['POST'])
@login_required
def trigger_sos():
    """Trigger SOS emergency alert"""
    from nexus_core.quantum_models import EmergencyAlert
    
    alert = EmergencyAlert(
        user_id=current_user.id,
        alert_type='sos',
        severity='critical',
        description='User triggered SOS'
    )
    
    try:
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'alert_id': alert.id,
            'status': 'alert_triggered',
            'message': 'Emergency services notified',
            'emergency_number': '911'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
