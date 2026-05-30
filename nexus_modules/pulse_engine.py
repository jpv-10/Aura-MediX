"""
AURA MEDIX — Real-time Vitals & ECG Engine
WebSocket-based real-time monitoring
"""
import random
from datetime import datetime
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
from nexus_core import socketio, db
from nexus_core.quantum_models import VitalSign

pulse_engine = Blueprint('pulse_engine', __name__, url_prefix='/pulse')

# ==================== SIMULATED REAL-TIME DATA ====================

class VitalSimulator:
    """Simulate realistic vital signs data"""
    
    @staticmethod
    def generate_heart_rate():
        """Generate realistic heart rate"""
        base = random.randint(60, 100)
        variation = random.randint(-5, 5)
        return max(40, min(200, base + variation))
    
    @staticmethod
    def generate_blood_pressure():
        """Generate realistic blood pressure"""
        systolic = random.randint(110, 140) + random.randint(-10, 10)
        diastolic = random.randint(70, 90) + random.randint(-5, 5)
        return {
            'systolic': max(90, min(200, systolic)),
            'diastolic': max(60, min(120, diastolic))
        }
    
    @staticmethod
    def generate_oxygen_saturation():
        """Generate realistic SpO2"""
        return max(94, min(100, random.randint(95, 100) + random.randint(-2, 2)))
    
    @staticmethod
    def generate_temperature():
        """Generate realistic temperature"""
        return round(36.5 + random.uniform(-0.5, 0.5), 1)
    
    @staticmethod
    def generate_blood_glucose():
        """Generate realistic blood glucose"""
        return max(70, min(200, random.randint(80, 130) + random.randint(-10, 10)))
    
    @staticmethod
    def generate_ecg_waveform(points=200):
        """Generate realistic ECG waveform"""
        import math
        waveform = []
        for i in range(points):
            t = i / points * 4 * math.pi
            noise = random.gauss(0, 0.1)
            if HAS_NUMPY:
                import numpy as np
                value = (
                    0.5 * noise +
                    0.3 * np.sin(t) +
                    0.8 * np.sin(t * 2) * np.exp(-((t - np.pi) ** 2) / 0.5)
                )
            else:
                value = 0.5 * noise + 0.3 * math.sin(t)
            waveform.append(max(-1, min(1, value)))
        return waveform

# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connection_response', {'data': 'Connected to Pulse Engine'})

@socketio.on('start_vitals_stream')
@login_required
def start_vitals_stream():
    """Start real-time vitals streaming"""
    user_id = current_user.id
    room = f'vitals_{user_id}'
    join_room(room)
    
    # Emit initial data
    emit('vitals_stream_started', {
        'status': 'streaming',
        'room': room,
        'message': 'Real-time vitals monitoring started'
    })
    
    # Simulate real-time data
    for _ in range(60):  # 60 second stream
        vital_data = {
            'heart_rate': VitalSimulator.generate_heart_rate(),
            'blood_pressure': VitalSimulator.generate_blood_pressure(),
            'oxygen_saturation': VitalSimulator.generate_oxygen_saturation(),
            'temperature': VitalSimulator.generate_temperature(),
            'blood_glucose': VitalSimulator.generate_blood_glucose(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        socketio.emit('vital_update', vital_data, room=room)
        socketio.sleep(1)

@socketio.on('stop_vitals_stream')
def stop_vitals_stream():
    """Stop vitals streaming"""
    user_id = current_user.id if current_user else None
    if user_id:
        leave_room(f'vitals_{user_id}')
    emit('vitals_stream_stopped', {'status': 'stopped'})

# ==================== REST ENDPOINTS ====================

@pulse_engine.route('/ecg/generate', methods=['GET'])
@login_required
def generate_ecg():
    """Generate ECG waveform data"""
    import numpy as np
    points = 500
    waveform = []
    
    for i in range(points):
        t = i / points * 2 * 3.14159
        # Simulate ECG pattern
        value = (
            0.3 * np.sin(t) +
            0.8 * np.sin(t * 2) * np.exp(-((t - np.pi) ** 2) / 0.5) +
            0.1 * np.random.normal(0, 0.05)
        )
        waveform.append(float(max(-1, min(1, value))))
    
    return jsonify({
        'waveform': waveform,
        'points': points,
        'heart_rate': VitalSimulator.generate_heart_rate()
    })

@pulse_engine.route('/realtime/metrics', methods=['GET'])
@login_required
def get_realtime_metrics():
    """Get current real-time metrics"""
    return jsonify({
        'heart_rate': VitalSimulator.generate_heart_rate(),
        'blood_pressure': VitalSimulator.generate_blood_pressure(),
        'oxygen_saturation': VitalSimulator.generate_oxygen_saturation(),
        'temperature': VitalSimulator.generate_temperature(),
        'blood_glucose': VitalSimulator.generate_blood_glucose(),
        'timestamp': datetime.utcnow().isoformat()
    })

@pulse_engine.route('/vitals/stream', methods=['GET'])
@login_required
def vitals_stream():
    """Get vitals history stream"""
    days = request.args.get('days', 7, type=int)
    from datetime import timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    vitals = VitalSign.query.filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= start_date
    ).order_by(VitalSign.recorded_at).all()
    
    return jsonify([{
        'heart_rate': v.heart_rate or 0,
        'systolic': v.blood_pressure_systolic or 0,
        'diastolic': v.blood_pressure_diastolic or 0,
        'temperature': v.temperature_celsius or 0,
        'blood_glucose': v.blood_glucose or 0,
        'oxygen_saturation': v.oxygen_saturation or 0,
        'timestamp': v.recorded_at.isoformat()
    } for v in vitals])
