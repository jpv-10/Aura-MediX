"""
AURA MEDIX — Analytics & Insights
Health trends and analytics endpoints
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from nexus_core.quantum_models import VitalSign
from datetime import datetime, timedelta
import statistics

neural_analytics = Blueprint('neural_analytics', __name__, url_prefix='/analytics')

# ==================== HEALTH TRENDS ====================

@neural_analytics.route('/health-trends', methods=['GET'])
@login_required
def get_health_trends():
    """Get health trends over time"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    vitals = VitalSign.query.filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= start_date
    ).order_by(VitalSign.recorded_at).all()
    
    # Aggregate data
    hr_data = [v.heart_rate for v in vitals if v.heart_rate]
    bp_sys_data = [v.blood_pressure_systolic for v in vitals if v.blood_pressure_systolic]
    bp_dia_data = [v.blood_pressure_diastolic for v in vitals if v.blood_pressure_diastolic]
    temp_data = [v.temperature_celsius for v in vitals if v.temperature_celsius]
    glucose_data = [v.blood_glucose for v in vitals if v.blood_glucose]
    
    def get_stats(data):
        if not data:
            return {'average': 0, 'min': 0, 'max': 0, 'std_dev': 0}
        return {
            'average': round(statistics.mean(data), 1),
            'min': min(data),
            'max': max(data),
            'std_dev': round(statistics.stdev(data), 1) if len(data) > 1 else 0
        }
    
    return jsonify({
        'period_days': days,
        'data_points': len(vitals),
        'heart_rate': get_stats(hr_data),
        'blood_pressure_systolic': get_stats(bp_sys_data),
        'blood_pressure_diastolic': get_stats(bp_dia_data),
        'temperature': get_stats(temp_data),
        'blood_glucose': get_stats(glucose_data),
        'timeline': [{
            'date': v.recorded_at.strftime('%Y-%m-%d %H:%M'),
            'heart_rate': v.heart_rate,
            'bp_systolic': v.blood_pressure_systolic,
            'bp_diastolic': v.blood_pressure_diastolic,
            'temperature': v.temperature_celsius,
            'blood_glucose': v.blood_glucose
        } for v in vitals[-50:]]  # Last 50 records
    })

# ==================== RISK ASSESSMENT ====================

@neural_analytics.route('/risk-matrix', methods=['GET'])
@login_required
def get_risk_matrix():
    """Get disease risk assessment"""
    profile = current_user.profile
    
    # Calculate risk scores based on vitals
    recent_vitals = VitalSign.query.filter_by(
        user_id=current_user.id
    ).order_by(VitalSign.recorded_at.desc()).first()
    
    risks = {
        'cardiovascular': 'Low',
        'diabetes': 'Low',
        'hypertension': 'Low',
        'obesity': 'Low',
        'overall': 'Low'
    }
    
    if recent_vitals:
        # Heart disease risk
        if recent_vitals.heart_rate and recent_vitals.heart_rate > 100:
            risks['cardiovascular'] = 'Medium'
        
        # Hypertension risk
        if (recent_vitals.blood_pressure_systolic and recent_vitals.blood_pressure_systolic > 140):
            risks['hypertension'] = 'High'
        elif (recent_vitals.blood_pressure_systolic and recent_vitals.blood_pressure_systolic > 130):
            risks['hypertension'] = 'Medium'
    
    if profile and profile.weight_kg and profile.height_cm:
        bmi = profile.weight_kg / ((profile.height_cm / 100) ** 2)
        if bmi > 30:
            risks['obesity'] = 'High'
            risks['diabetes'] = 'Medium'
        elif bmi > 25:
            risks['obesity'] = 'Medium'
    
    return jsonify({
        'risk_scores': risks,
        'assessment_date': datetime.utcnow().isoformat(),
        'recommendations': [
            'Monitor vitals regularly',
            'Maintain healthy lifestyle',
            'Schedule regular health checkups',
            'Follow healthcare provider recommendations'
        ]
    })

# ==================== WELLNESS SCORE ====================

@neural_analytics.route('/wellness-score', methods=['GET'])
@login_required
def get_wellness_score():
    """Calculate comprehensive wellness score"""
    days = request.args.get('days', 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    vitals = VitalSign.query.filter(
        VitalSign.user_id == current_user.id,
        VitalSign.recorded_at >= start_date
    ).all()
    
    score = 50  # Base score
    
    if vitals:
        # Check vital patterns
        hr_values = [v.heart_rate for v in vitals if v.heart_rate]
        if hr_values and statistics.mean(hr_values) < 100:
            score += 15
        
        bp_sys_values = [v.blood_pressure_systolic for v in vitals if v.blood_pressure_systolic]
        if bp_sys_values and statistics.mean(bp_sys_values) < 130:
            score += 15
        
        glucose_values = [v.blood_glucose for v in vitals if v.blood_glucose]
        if glucose_values and 70 <= statistics.mean(glucose_values) <= 130:
            score += 15
        
        temp_values = [v.temperature_celsius for v in vitals if v.temperature_celsius]
        if temp_values and 36.1 <= statistics.mean(temp_values) <= 37.2:
            score += 5
    
    return jsonify({
        'wellness_score': min(100, score),
        'rating': 'Excellent' if score >= 80 else 'Good' if score >= 60 else 'Fair',
        'metrics': {
            'cardiovascular': score * 0.7,
            'metabolic': score * 0.6,
            'respiratory': score * 0.8,
            'overall': score
        },
        'period_days': days
    })

# ==================== ACTIVITY FEED ====================

@neural_analytics.route('/activity-feed', methods=['GET'])
@login_required
def get_activity_feed():
    """Get user activity history"""
    limit = request.args.get('limit', 20, type=int)
    
    vitals = VitalSign.query.filter_by(user_id=current_user.id).order_by(
        VitalSign.recorded_at.desc()
    ).limit(limit).all()
    
    activity = []
    for v in vitals:
        activity.append({
            'type': 'vital_logged',
            'timestamp': v.recorded_at.isoformat(),
            'description': f'Logged vitals - HR: {v.heart_rate} bpm'
        })
    
    return jsonify({
        'activities': activity,
        'total': len(activity)
    })

# ==================== HEALTH METRICS ====================

@neural_analytics.route('/health-metrics', methods=['GET'])
@login_required
def get_health_metrics():
    """Get comprehensive health metrics"""
    recent = VitalSign.query.filter_by(
        user_id=current_user.id
    ).order_by(VitalSign.recorded_at.desc()).first()
    
    metrics = {
        'heart_rate': {'value': 0, 'unit': 'bpm', 'status': 'normal'},
        'blood_pressure': {'value': '0/0', 'unit': 'mmHg', 'status': 'normal'},
        'oxygen': {'value': 0, 'unit': '%', 'status': 'normal'},
        'temperature': {'value': 0, 'unit': '°C', 'status': 'normal'}
    }
    
    if recent:
        metrics['heart_rate']['value'] = recent.heart_rate or 0
        if recent.heart_rate and recent.heart_rate > 100:
            metrics['heart_rate']['status'] = 'elevated'
        
        if recent.blood_pressure_systolic and recent.blood_pressure_diastolic:
            metrics['blood_pressure']['value'] = f"{recent.blood_pressure_systolic}/{recent.blood_pressure_diastolic}"
        
        metrics['oxygen']['value'] = recent.oxygen_saturation or 0
        metrics['temperature']['value'] = recent.temperature_celsius or 0
    
    return jsonify(metrics)
