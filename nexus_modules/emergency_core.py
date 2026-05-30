"""
AURA MEDIX — Emergency Detection & Response
SOS, emergency alerts, critical monitoring, and emergency contacts
File: emergency_core.py  (Blueprint)
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from nexus_core import db
from nexus_core.quantum_models import EmergencyAlert, VitalSign, EmergencyContact
from datetime import datetime

emergency_core = Blueprint('emergency_core', __name__, url_prefix='/emergency')


# ═══════════════════════════════════════════
#  EMERGENCY DETECTION
# ═══════════════════════════════════════════

@emergency_core.route('/detect', methods=['POST'])
@login_required
def detect_emergency():
    """Detect emergency from symptoms/vitals and log an alert."""
    data     = request.json or {}
    symptoms = data.get('symptoms', [])
    vitals   = data.get('vitals', {})

    critical_symptoms = [
        'chest pain', 'severe shortness of breath', 'loss of consciousness',
        'severe bleeding', 'difficulty speaking', 'facial drooping', 'arm weakness'
    ]
    has_critical = any(
        s.lower() in [c.lower() for c in critical_symptoms] for s in symptoms
    )

    critical_vitals = False
    hr  = vitals.get('heart_rate', 0)
    bps = vitals.get('bp_systolic', 0)
    spo2 = vitals.get('oxygen_saturation', 100)
    if hr > 140 or (0 < hr < 40):        critical_vitals = True
    if bps > 180 or (0 < bps < 90):      critical_vitals = True
    if spo2 < 90:                         critical_vitals = True

    if has_critical or critical_vitals:
        alert = EmergencyAlert(
            user_id    = current_user.id,
            alert_type = 'critical_symptoms' if has_critical else 'critical_vitals',
            severity   = 'critical',
            description= (
                f"Emergency detected. "
                f"Symptoms: {', '.join(symptoms) or 'none'}. "
                f"Vitals: {vitals}"
            )
        )
        try:
            db.session.add(alert)
            db.session.commit()
            return jsonify({
                'emergency_detected': True,
                'alert_id'          : alert.id,
                'severity'          : 'CRITICAL',
                'action'            : 'CALL 112 IMMEDIATELY',
                'message'           : 'Emergency alert logged.'
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return jsonify({
        'emergency_detected': False,
        'message': 'No emergency detected. Consult a healthcare provider if symptoms worsen.'
    })


# ═══════════════════════════════════════════
#  ALERT MANAGEMENT
# ═══════════════════════════════════════════

@emergency_core.route('/alerts/active', methods=['GET'])
@login_required
def get_active_alerts():
    """Return all active emergency alerts for the current user."""
    alerts = EmergencyAlert.query.filter(
        EmergencyAlert.user_id == current_user.id,
        EmergencyAlert.status  == 'active'
    ).order_by(EmergencyAlert.created_at.desc()).all()

    return jsonify([{
        'id'         : a.id,
        'type'       : a.alert_type,
        'severity'   : a.severity,
        'description': a.description,
        'created_at' : a.created_at.isoformat()
    } for a in alerts])


@emergency_core.route('/alert/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Mark an alert as resolved."""
    alert = EmergencyAlert.query.filter_by(
        id=alert_id, user_id=current_user.id
    ).first_or_404()

    alert.status       = 'resolved'
    alert.responded_at = datetime.utcnow()
    try:
        db.session.commit()
        return jsonify({'status': 'alert_resolved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════
#  EMERGENCY CONTACTS  (new)
# ═══════════════════════════════════════════

@emergency_core.route('/contact/save', methods=['POST'])
@login_required
def save_emergency_contact():
    """Save (or update) the user's emergency contact."""
    data  = request.json or {}
    name  = data.get('name', '').strip()
    phone = data.get('phone', '').strip()

    if not name or not phone:
        return jsonify({'error': 'name and phone are required'}), 400

    # Upsert: one contact per user
    contact = EmergencyContact.query.filter_by(user_id=current_user.id).first()
    if contact:
        contact.name  = name
        contact.phone = phone
    else:
        contact = EmergencyContact(
            user_id=current_user.id,
            name   =name,
            phone  =phone
        )
        db.session.add(contact)

    try:
        db.session.commit()
        return jsonify({'status': 'saved', 'name': name, 'phone': phone})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@emergency_core.route('/contact', methods=['GET'])
@login_required
def get_emergency_contact():
    """Retrieve the user's saved emergency contact."""
    contact = EmergencyContact.query.filter_by(user_id=current_user.id).first()
    if not contact:
        return jsonify({'contact': None})
    return jsonify({'contact': {'name': contact.name, 'phone': contact.phone}})


@emergency_core.route('/contact/delete', methods=['DELETE'])
@login_required
def delete_emergency_contact():
    """Delete the user's emergency contact."""
    contact = EmergencyContact.query.filter_by(user_id=current_user.id).first()
    if not contact:
        return jsonify({'error': 'No contact found'}), 404
    db.session.delete(contact)
    try:
        db.session.commit()
        return jsonify({'status': 'deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════
#  CRITICAL VITALS CHECK
# ═══════════════════════════════════════════

@emergency_core.route('/vitals/critical-check', methods=['POST'])
@login_required
def check_critical_vitals():
    """Check if submitted vitals cross critical thresholds."""
    data = request.json or {}

    thresholds = {
        'heart_rate'         : {'min': 30,  'max': 150},
        'bp_systolic'        : {'min': 70,  'max': 180},
        'oxygen_saturation'  : {'min': 85},
    }

    alert_messages = []

    hr = data.get('heart_rate')
    if hr is not None:
        if hr < thresholds['heart_rate']['min']:
            alert_messages.append('Heart rate critically LOW')
        elif hr > thresholds['heart_rate']['max']:
            alert_messages.append('Heart rate critically HIGH')

    bps = data.get('bp_systolic')
    if bps is not None:
        if bps > thresholds['bp_systolic']['max']:
            alert_messages.append('Blood pressure CRITICALLY HIGH')
        elif bps < thresholds['bp_systolic']['min']:
            alert_messages.append('Blood pressure CRITICALLY LOW')

    spo2 = data.get('oxygen_saturation')
    if spo2 is not None and spo2 < thresholds['oxygen_saturation']['min']:
        alert_messages.append('Oxygen saturation CRITICAL')

    if alert_messages:
        alert = EmergencyAlert(
            user_id    = current_user.id,
            alert_type = 'critical_vitals',
            severity   = 'critical',
            description= '; '.join(alert_messages)
        )
        try:
            db.session.add(alert)
            db.session.commit()
        except Exception:
            db.session.rollback()

    return jsonify({
        'has_critical_vitals'     : len(alert_messages) > 0,
        'alerts'                  : alert_messages,
        'should_seek_immediate_care': len(alert_messages) > 0
    })


# ═══════════════════════════════════════════
#  CPR GUIDE  (public — no login required)
# ═══════════════════════════════════════════

@emergency_core.route('/cpr-guide', methods=['GET'])
def get_cpr_guide():
    return jsonify({
        'title': 'CPR Instructions — Step by Step',
        'steps': [
            {'step': 1, 'title': 'Check Responsiveness',     'action': 'Shake shoulders and shout "Are you okay?"'},
            {'step': 2, 'title': 'Call Emergency Services',  'action': 'Call 112 immediately or have bystander call'},
            {'step': 3, 'title': 'Position the Person',      'action': 'Lay on back on a firm, flat surface'},
            {'step': 4, 'title': 'Open Airway',              'action': 'Tilt head back slightly and lift chin'},
            {'step': 5, 'title': 'Hand Position',            'action': 'Place heel of hand on center of chest'},
            {'step': 6, 'title': 'Chest Compressions',       'action': 'Push down 5–6 cm at 100–120 compressions/minute'},
            {'step': 7, 'title': 'Rescue Breaths',           'action': 'Give 2 rescue breaths after every 30 compressions'},
            {'step': 8, 'title': 'Continue',                 'action': 'Keep going until emergency services arrive'},
        ],
        'emergency_number': '112'
    })


# ═══════════════════════════════════════════
#  FIRST AID  (public — no login required)
# ═══════════════════════════════════════════

@emergency_core.route('/first-aid/<condition>', methods=['GET'])
def get_first_aid(condition):
    guides = {
        'choking' : {
            'symptoms': ['Unable to cough or speak', 'Unable to breathe', 'Weak cough'],
            'steps'   : ['Encourage coughing', 'Give 5 firm back blows', 'Give 5 abdominal thrusts (Heimlich)', 'Repeat until object dislodges', 'Call 112 if unsuccessful']
        },
        'bleeding': {
            'symptoms': ['Active bleeding', 'Spurting blood'],
            'steps'   : ['Apply direct pressure with clean cloth', 'Maintain pressure for 10–15 minutes', 'Elevate affected area if possible', 'Apply tourniquet for severe limb bleeding', 'Call 112 if bleeding continues']
        },
        'burns'   : {
            'symptoms': ['Red or blistered skin', 'Pain'],
            'steps'   : ['Cool under running water 20 min', 'Remove tight items nearby', 'Cover with clean dry cloth', 'Take pain reliever', 'Seek care for severe burns']
        },
        'fractures': {
            'symptoms': ['Pain', 'Swelling', 'Deformity'],
            'steps'   : ['Immobilize the area', 'Apply ice wrapped in cloth', 'Elevate if possible', 'Take pain reliever', 'Seek emergency care']
        },
        'stroke'  : {
            'symptoms': ['Face drooping', 'Arm weakness', 'Speech difficulty'],
            'steps'   : ['F — Face drooping?', 'A — Arm weakness?', 'S — Speech slurred?', 'T — Time to call 112 NOW', 'Note time symptoms started']
        },
    }

    guide = guides.get(condition.lower(), {
        'symptoms': ['Unknown condition'],
        'steps'   : ['Call emergency services if unsure']
    })

    return jsonify({
        'condition'       : condition,
        'symptoms'        : guide.get('symptoms', []),
        'steps'           : guide.get('steps', []),
        'emergency_number': '112'
    })