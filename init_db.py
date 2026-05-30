"""
AURA MEDIX — Database Initialization Script
Initialize database with demo user and sample data
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nexus_core import create_nexus_app, db
from nexus_core.quantum_models import User, PatientProfile, VitalSign

def init_database():
    """Initialize database with tables and demo data"""
    app = create_nexus_app('development')
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created")
        
        # Check if demo user exists
        demo = User.query.filter_by(email='demo@auramedix.ai').first()
        
        if demo:
            print("✓ Demo user already exists")
        else:
            print("\nCreating demo user...")
            # Create demo user
            demo_user = User(
                email='demo@auramedix.ai',
                username='demo',
                full_name='Demo User',
                is_verified=True,
                is_active=True
            )
            demo_user.set_password('Demo@2024')
            
            db.session.add(demo_user)
            db.session.commit()
            print(f"✓ Demo user created")
            
            # Create patient profile
            profile = PatientProfile(
                user_id=demo_user.id,
                age=35,
                gender='Male',
                height_cm=175,
                weight_kg=75,
                blood_type='O+',
                medical_conditions='None',
                medications='None',
                allergies='Penicillin'
            )
            db.session.add(profile)
            db.session.commit()
            print(f"✓ Patient profile created")
            
            # Add sample vital signs (last 30 days)
            print("\nAdding sample vital signs...")
            for i in range(30):
                vital = VitalSign(
                    user_id=demo_user.id,
                    heart_rate=random.randint(60, 100),
                    blood_pressure_systolic=random.randint(110, 140),
                    blood_pressure_diastolic=random.randint(70, 90),
                    temperature_celsius=round(36.5 + random.uniform(-0.5, 0.5), 1),
                    blood_glucose=random.randint(80, 130),
                    oxygen_saturation=random.randint(95, 100),
                    respiratory_rate=random.randint(12, 20),
                    recorded_at=datetime.utcnow() - timedelta(days=i)
                )
                db.session.add(vital)
            
            db.session.commit()
            print(f"✓ 30 days of sample vitals added")
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print("\nDemo Credentials:")
        print("  Email: demo@auramedix.ai")
        print("  Password: Demo@2024")
        print("\nRun the application with: python run.py")
        print("Then visit: http://localhost:5000")

if __name__ == '__main__':
    init_database()
