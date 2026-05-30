"""
AURA MEDIX — Database Models
SQLAlchemy models for users, profiles, vitals, chats, reports, alerts, and emergency contacts
File: quantum_models.py

FIXED: Removed duplicate index definitions to prevent SQLAlchemy errors
Each table defines indexes ONLY ONCE in __table_args__
"""
from nexus_core import db, bcrypt
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
import json


class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name     = db.Column(db.String(120), nullable=True)
    role          = db.Column(db.String(20),  default='patient')
    health_score  = db.Column(db.Integer,     default=85)
    is_verified   = db.Column(db.Boolean,     default=False)
    is_active     = db.Column(db.Boolean,     default=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile           = db.relationship('PatientProfile',   backref='user', uselist=False, cascade='all, delete-orphan')
    vitals            = db.relationship('VitalSign',         backref='user', lazy=True,     cascade='all, delete-orphan')
    chat_sessions     = db.relationship('ChatSession',       backref='user', lazy=True,     cascade='all, delete-orphan')
    reports           = db.relationship('Report',            backref='user', lazy=True,     cascade='all, delete-orphan')
    predictions       = db.relationship('DiseasePredictor',   backref='user', lazy=True,     cascade='all, delete-orphan')
    timeline_entries  = db.relationship('HealthTimeline',    backref='user', lazy=True,     cascade='all, delete-orphan')
    alerts            = db.relationship('EmergencyAlert',    backref='user', lazy=True,     cascade='all, delete-orphan')
    emergency_contact = db.relationship('EmergencyContact',  backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class PatientProfile(db.Model):
    """Patient health profile"""
    __tablename__ = 'patient_profiles'

    id                 = db.Column(db.Integer, primary_key=True)
    user_id            = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    age                = db.Column(db.Integer, nullable=True)
    gender             = db.Column(db.String(20), nullable=True)
    height_cm          = db.Column(db.Float, nullable=True)
    weight_kg          = db.Column(db.Float, nullable=True)
    blood_type         = db.Column(db.String(10), nullable=True)
    medical_conditions = db.Column(db.Text, nullable=True)
    medications        = db.Column(db.Text, nullable=True)
    allergies          = db.Column(db.Text, nullable=True)
    emergency_contact  = db.Column(db.String(120), nullable=True)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PatientProfile user_id={self.user_id}>'


class VitalSign(db.Model):
    """Vital signs measurements"""
    __tablename__ = 'vital_signs'

    id                       = db.Column(db.Integer, primary_key=True)
    user_id                  = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    heart_rate               = db.Column(db.Float, nullable=True)
    blood_pressure_systolic  = db.Column(db.Float, nullable=True)
    blood_pressure_diastolic = db.Column(db.Float, nullable=True)
    temperature_celsius      = db.Column(db.Float, nullable=True)
    blood_glucose            = db.Column(db.Float, nullable=True)
    oxygen_saturation        = db.Column(db.Float, nullable=True)
    respiratory_rate         = db.Column(db.Float, nullable=True)
    notes                    = db.Column(db.Text, nullable=True)
    recorded_at              = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # FIXED: Define index ONLY ONCE in __table_args__
    __table_args__ = (
        db.Index('idx_user_recorded_at', 'user_id', 'recorded_at'),
    )

    def __repr__(self):
        return f'<VitalSign user_id={self.user_id} at {self.recorded_at}>'


class ChatSession(db.Model):
    """AI Doctor chat session"""
    __tablename__ = 'chat_sessions'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(255), nullable=True)
    messages   = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ChatSession {self.id} user_id={self.user_id}>'


class DiseasePredictor(db.Model):
    """Disease prediction results — persists ML predictions"""
    __tablename__ = 'disease_predictions'

    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    disease_name      = db.Column(db.String(100), nullable=False)
    disease_type      = db.Column(db.String(50),  nullable=False)
    prediction_result = db.Column(db.String(50),  nullable=False)
    probability       = db.Column(db.Float,       nullable=True)
    risk_percentage   = db.Column(db.Float,       nullable=True)
    confidence_score  = db.Column(db.Float,       nullable=True)
    severity          = db.Column(db.String(50),  nullable=True)
    input_data        = db.Column(db.Text,        nullable=True)
    recommendations   = db.Column(db.Text,        nullable=True)
    model_used        = db.Column(db.String(50),  nullable=True)
    timestamp         = db.Column(db.DateTime,    default=datetime.utcnow, index=True)
    created_at        = db.Column(db.DateTime,    default=datetime.utcnow)

    # FIXED: Define index ONLY ONCE in __table_args__
    __table_args__ = (
        db.Index('idx_disease_predictions_user_created', 'user_id', 'created_at'),
    )

    def to_dict(self):
        try:
            input_data = json.loads(self.input_data) if self.input_data else {}
            recommendations = json.loads(self.recommendations) if self.recommendations else []
        except:
            input_data = {}
            recommendations = []
        
        return {
            'id': self.id,
            'disease_name': self.disease_name,
            'disease_type': self.disease_type,
            'prediction_result': self.prediction_result,
            'probability': self.probability,
            'risk_percentage': self.risk_percentage,
            'confidence_score': self.confidence_score,
            'severity': self.severity,
            'input_data': input_data,
            'recommendations': recommendations,
            'model_used': self.model_used,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<DiseasePredictor disease={self.disease_name} user={self.user_id}>'


class HealthTimeline(db.Model):
    """Health timeline entry"""
    __tablename__ = 'health_timeline'

    id                = db.Column(db.Integer, primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    prediction_id     = db.Column(db.Integer, db.ForeignKey('disease_predictions.id'), nullable=True)
    event_type        = db.Column(db.String(50), nullable=False)
    title             = db.Column(db.String(255), nullable=False)
    description       = db.Column(db.Text, nullable=True)
    disease_analyzed  = db.Column(db.String(100), nullable=True)
    result            = db.Column(db.String(100), nullable=True)
    severity          = db.Column(db.String(50), nullable=True)
    ai_recommendation = db.Column(db.Text, nullable=True)
    data              = db.Column(db.Text, nullable=True)
    timestamp         = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # FIXED: Define index ONLY ONCE in __table_args__
    __table_args__ = (
        db.Index('idx_health_timeline_user_created', 'user_id', 'created_at'),
    )

    def to_dict(self):
        try:
            data = json.loads(self.data) if self.data else {}
        except:
            data = {}
        
        return {
            'id': self.id,
            'event_type': self.event_type,
            'title': self.title,
            'description': self.description,
            'disease_analyzed': self.disease_analyzed,
            'result': self.result,
            'severity': self.severity,
            'ai_recommendation': self.ai_recommendation,
            'data': data,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<HealthTimeline user={self.user_id} type={self.event_type}>'


class Report(db.Model):
    """Generated health report"""
    __tablename__ = 'reports'

    id            = db.Column(db.Integer, primary_key=True)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title         = db.Column(db.String(255), nullable=False)
    report_type   = db.Column(db.String(50),  nullable=False)
    content       = db.Column(db.Text, nullable=True)
    file_path     = db.Column(db.String(255), nullable=True)
    disease_name  = db.Column(db.String(100), nullable=True)  # NEW: Added for disease reports
    prediction_id = db.Column(db.Integer, db.ForeignKey('disease_predictions.id'), nullable=True)  # NEW: Link to prediction
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # FIXED: Define index ONLY ONCE in __table_args__
    __table_args__ = (
        db.Index('idx_reports_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f'<Report {self.id} type={self.report_type}>'


class EmergencyAlert(db.Model):
    """Emergency alert and SOS"""
    __tablename__ = 'emergency_alerts'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type   = db.Column(db.String(50), nullable=False)
    severity     = db.Column(db.String(20), nullable=False)
    description  = db.Column(db.Text, nullable=False)
    status       = db.Column(db.String(20), default='active')
    created_at   = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    responded_at = db.Column(db.DateTime, nullable=True)

    # FIXED: Define index ONLY ONCE in __table_args__
    __table_args__ = (
        db.Index('idx_emergency_alerts_user_status', 'user_id', 'status', 'created_at'),
    )

    def __repr__(self):
        return f'<EmergencyAlert {self.id} severity={self.severity}>'


class EmergencyContact(db.Model):
    """Emergency contact model"""
    __tablename__ = 'emergency_contacts'

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    relationship = db.Column(db.String(50))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'contact_name': self.contact_name,
            'phone_number': self.phone_number,
            'relationship': self.relationship
        }

    def __repr__(self):
        return f'<EmergencyContact user={self.user_id} name={self.contact_name}>'
