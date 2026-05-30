"""
AURA MEDIX — Authentication & Portal Routes with Data Provisioning
Main application routes for auth, dashboard, and page navigation
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from nexus_core import db, bcrypt
from nexus_core.quantum_models import (
    User, PatientProfile, DiseasePredictor, HealthTimeline, Report
)
from functools import wraps
import secrets
from datetime import datetime, timedelta

medix_portal = Blueprint('medix_portal', __name__)

# ==================== AUTH ROUTES ====================

@medix_portal.route('/auth/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember', False))
            next_page = request.args.get('next')
            return redirect(next_page or url_for('medix_portal.dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html')

@medix_portal.route('/auth/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        
        # Validation
        if not email or not username or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('medix_portal.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('medix_portal.register'))
        
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'error')
            return redirect(url_for('medix_portal.register'))
        
        # Check existing user
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('medix_portal.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'error')
            return redirect(url_for('medix_portal.register'))
        
        # Create user
        user = User(email=email, username=username, full_name=full_name)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create patient profile
            profile = PatientProfile(user_id=user.id)
            db.session.add(profile)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('medix_portal.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html')

@medix_portal.route('/auth/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('medix_portal.landing'))

@medix_portal.route('/auth/guest-session')
def guest_session():
    """Create guest session"""
    guest_user = User(
        email=f'guest_{secrets.token_hex(4)}@auramedix.local',
        username=f'guest_{secrets.token_hex(4)}',
        full_name='Guest User',
        is_verified=True
    )
    guest_user.set_password(secrets.token_urlsafe(16))
    
    try:
        db.session.add(guest_user)
        db.session.commit()
        
        profile = PatientProfile(user_id=guest_user.id)
        db.session.add(profile)
        db.session.commit()
        
        login_user(guest_user)
        return redirect(url_for('medix_portal.dashboard'))
    except:
        db.session.rollback()
        flash('Guest session creation failed', 'error')
        return redirect(url_for('medix_portal.landing'))

# ==================== PAGE ROUTES ====================

@medix_portal.route('/')
def landing():
    """Landing page"""
    stats = {
        'patients':      50000,
        'accuracy':      97.4,
        'response_time': 2,
        'uptime':        99.9,
    }
    return render_template('landing.html', stats=stats)

@medix_portal.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    user = current_user
    profile = user.profile
    
    return render_template('dashboard/main.html', user=user, profile=profile)

# ==================== MODULE ROUTES ====================

@medix_portal.route('/modules/ai-doctor')
@login_required
def ai_doctor():
    """AI Doctor chatbot"""
    return render_template('modules/ai_doctor.html')

@medix_portal.route('/modules/disease-detection')
@login_required
def disease_detection():
    """Disease prediction module"""
    return render_template('modules/disease_detection.html')

@medix_portal.route('/modules/symptom-engine')
@login_required
def symptom_engine():
    """Symptom analyzer"""
    return render_template('modules/symptom_engine.html')

@medix_portal.route('/modules/mental-wellness')
@login_required
def mental_wellness():
    """Mental wellness assessment"""
    return render_template('modules/mental_wellness.html')

@medix_portal.route('/modules/hospital-locator')
@login_required
def hospital_locator():
    """Hospital finder"""
    return render_template('modules/hospital_locator.html')

@medix_portal.route('/modules/voice-assistant')
@login_required
def voice_assistant():
    """Voice assistant"""
    return render_template('modules/voice_assistant.html')

@medix_portal.route('/modules/bmi-fitness')
@login_required
def bmi_fitness():
    """BMI and fitness calculator"""
    return render_template('modules/bmi_fitness.html')

@medix_portal.route('/modules/medicine-recommendation')
@login_required
def medicine_recommendation():
    """Medicine recommendations"""
    return render_template('modules/medicine_recommendation.html')

@medix_portal.route('/modules/health-analytics')
@login_required
def health_analytics():
    """Health analytics dashboard"""
    return render_template('modules/health_analytics.html')

@medix_portal.route('/modules/medical-reports')
@login_required
def medical_reports():
    """Medical reports generator with database records"""
    records = Report.query.filter_by(user_id=current_user.id).order_by(
        Report.created_at.desc()
    ).all()
    return render_template('modules/medical_reports.html', records=records)

@medix_portal.route('/modules/health-timeline')
@login_required
def health_timeline():
    """Health timeline with predictions and records"""
    # Get timeline entries and predictions for display
    timeline_entries = HealthTimeline.query.filter_by(
        user_id=current_user.id
    ).order_by(HealthTimeline.created_at.desc()).all()
    
    predictions = DiseasePredictor.query.filter_by(
        user_id=current_user.id
    ).order_by(DiseasePredictor.created_at.desc()).all()
    
    return render_template(
        'modules/health_timeline.html',
        records=timeline_entries,
        predictions=predictions
    )

@medix_portal.route('/modules/emergency')
@login_required
def emergency():
    """Emergency module"""
    return render_template('modules/emergency.html')

@medix_portal.route('/modules/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('modules/settings.html')

# ==================== API ROUTES FOR TIMELINE ====================

@medix_portal.route('/api/v1/timeline', methods=['GET'])
@login_required
def get_timeline_data():
    """Get timeline data for AJAX requests"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    entries = HealthTimeline.query.filter(
        HealthTimeline.user_id == current_user.id,
        HealthTimeline.created_at >= start_date
    ).order_by(HealthTimeline.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'count': len(entries),
        'entries': [e.to_dict() for e in entries]
    })

@medix_portal.route('/api/v1/predictions', methods=['GET'])
@login_required
def get_predictions_data():
    """Get predictions data for AJAX requests"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    predictions = DiseasePredictor.query.filter(
        DiseasePredictor.user_id == current_user.id,
        DiseasePredictor.created_at >= start_date
    ).order_by(DiseasePredictor.created_at.desc()).all()
    
    return jsonify({
        'success': True,
        'count': len(predictions),
        'predictions': [p.to_dict() for p in predictions]
    })

# ==================== ERROR HANDLERS ====================

@medix_portal.errorhandler(404)
def not_found(e):
    """404 error handler"""
    return render_template('errors/404.html'), 404

@medix_portal.errorhandler(500)
def server_error(e):
    """500 error handler"""
    return render_template('errors/500.html'), 500