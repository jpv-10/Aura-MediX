"""
AURA MEDIX — Core Application Factory
Production-grade Flask initialization with extensions
FIXED: Corrected import paths for config module and added migration support
"""

import os
import logging
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# =========================
# INITIALIZE EXTENSIONS
# =========================

db = SQLAlchemy()

login_manager = LoginManager()

bcrypt = Bcrypt()

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)


# =========================
# SAFE DATABASE INITIALIZATION
# =========================

def init_safe_db(app):
    """
    Initialize database tables safely without duplicate index errors.
    """
    with app.app_context():
        try:
            logger.info("[Database] Attempting to initialize database...")
            
            # Get database engine and inspector
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            logger.info(f"[Database] Existing tables: {existing_tables}")
            
            # Run migrations first
            from nexus_core.migrations import run_migrations
            logger.info("[Database] Running database migrations...")
            run_migrations(db)
            
            # Attempt to create all tables
            db.create_all()
            
            logger.info("[Database] Database initialization completed successfully")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific SQLite index errors
            if 'already exists' in error_msg and 'index' in error_msg:
                logger.warning(f"[Database] Index already exists (safe to ignore): {e}")
                logger.info("[Database] Database is already initialized with indexes")
                return True
            
            # Handle other database errors
            elif 'operational error' in error_msg or 'programming error' in error_msg:
                logger.error(f"[Database] Database operational error: {e}")
                logger.warning("[Database] Attempting recovery with table-by-table creation...")
                
                try:
                    # Try creating tables individually
                    from nexus_core.quantum_models import (
                        User, PatientProfile, VitalSign, ChatSession,
                        DiseasePredictor, HealthTimeline, Report,
                        EmergencyAlert, EmergencyContact
                    )
                    
                    models = [
                        User, PatientProfile, VitalSign, ChatSession,
                        DiseasePredictor, HealthTimeline, Report,
                        EmergencyAlert, EmergencyContact
                    ]
                    
                    for model in models:
                        try:
                            model.__table__.create(db.engine, checkfirst=True)
                            logger.info(f"[Database] Table created/verified: {model.__tablename__}")
                        except Exception as table_e:
                            if 'already exists' in str(table_e).lower():
                                logger.info(f"[Database] Table already exists: {model.__tablename__}")
                            else:
                                logger.warning(f"[Database] Error creating {model.__tablename__}: {table_e}")
                    
                    logger.info("[Database] Recovery completed")
                    return True
                    
                except Exception as recovery_e:
                    logger.error(f"[Database] Recovery failed: {recovery_e}")
                    return False
            
            else:
                logger.error(f"[Database] Unexpected error: {e}")
                return False


# =========================
# CREATE FLASK APP
# =========================

def create_nexus_app(config_name='development'):
    """
    Create and configure the Flask application with safe database initialization
    """
    
    # Import config_map from nexus_core.config (not from config)
    from nexus_core.config import config_map

    app = Flask(
        __name__,
        template_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'quantum_ui',
            'templates'
        ),
        static_folder=os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'quantum_ui',
            'static'
        )
    )

    # =========================
    # LOAD CONFIG
    # =========================

    config_class = config_map.get(config_name, config_map['development'])
    app.config.from_object(config_class)
    
    logger.info(f"[App] Configuration loaded: {config_name}")

    # =========================
    # INIT EXTENSIONS
    # =========================

    db.init_app(app)

    login_manager.init_app(app)

    bcrypt.init_app(app)

    CORS(app)

    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        ping_timeout=60,
        ping_interval=25,
        engineio_logger=False,
        socketio_logger=False
    )

    # =========================
    # LOGIN MANAGER CONFIG
    # =========================

    login_manager.login_view = 'medix_portal.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.login_message_category = 'info'

    # =========================
    # USER LOADER
    # =========================

    from nexus_core.quantum_models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # =========================
    # SAFE DATABASE INITIALIZATION
    # =========================

    with app.app_context():
        logger.info("[App] Starting safe database initialization...")
        success = init_safe_db(app)
        if not success:
            logger.warning("[App] Database initialization had issues but continuing...")

    # =========================
    # REGISTER BLUEPRINTS
    # =========================

    register_blueprints(app)

    # =========================
    # REGISTER ERROR HANDLERS
    # =========================

    register_error_handlers(app)

    # =========================
    # REGISTER CLI COMMANDS
    # =========================

    register_cli_commands(app)

    logger.info("[App] Application initialized successfully")
    return app


# =========================
# BLUEPRINT REGISTRATION
# =========================

def register_blueprints(app):
    """
    Register all application blueprints
    """

    from nexus_modules.medix_portal import medix_portal
    from nexus_modules.ai_engine import ai_engine
    from nexus_modules.nexus_api import nexus_api
    from nexus_modules.emergency_core import emergency_core
    from nexus_modules.neural_analytics import neural_analytics
    from nexus_modules.hologram_system import hologram_system
    from nexus_modules.pulse_engine import pulse_engine
    from nexus_modules.hospital_api import hospital_api

    app.register_blueprint(medix_portal)
    app.register_blueprint(ai_engine)
    app.register_blueprint(nexus_api)
    app.register_blueprint(emergency_core)
    app.register_blueprint(neural_analytics)
    app.register_blueprint(hologram_system)
    app.register_blueprint(pulse_engine)
    app.register_blueprint(hospital_api)

    logger.info("[App] Blueprints registered successfully")


# =========================
# ERROR HANDLERS
# =========================

def register_error_handlers(app):
    """
    Register HTTP error handlers
    """

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        logger.error(f"[Error] 500 Internal Server Error: {error}")
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

    @app.errorhandler(400)
    def bad_request(error):
        from flask import render_template, jsonify

        if request.is_json:
            return jsonify({'error': 'Bad request'}), 400

        return render_template('errors/404.html'), 400


# =========================
# CLI COMMANDS
# =========================

def register_cli_commands(app):
    """
    Register CLI commands for database management
    """

    @app.cli.command()
    def init_db():
        """Initialize database with safe creation"""
        logger.info("[CLI] Initializing database...")
        with app.app_context():
            success = init_safe_db(app)
            if success:
                logger.info("[CLI] Database initialized successfully")
                print('✓ Database initialized successfully!')
            else:
                logger.error("[CLI] Database initialization failed")
                print('✗ Database initialization had errors')

    @app.cli.command()
    def migrate_db():
        """Run database migrations"""
        logger.info("[CLI] Running database migrations...")
        with app.app_context():
            try:
                from nexus_core.migrations import run_migrations
                success = run_migrations(db)
                if success:
                    logger.info("[CLI] Migrations completed successfully")
                    print('✓ Database migrations completed successfully!')
                else:
                    logger.error("[CLI] Migrations had errors")
                    print('✗ Database migrations had errors')
            except Exception as e:
                logger.error(f"[CLI] Migration error: {e}")
                print(f'✗ Migration error: {e}')

    @app.cli.command()
    def drop_db():
        """Drop all database tables (WITH WARNING)"""
        logger.warning("[CLI] Drop database command initiated")
        confirm = input('WARNING: This will delete ALL data. Are you sure? (yes/no): ')

        if confirm.lower() == 'yes':
            with app.app_context():
                try:
                    db.drop_all()
                    logger.warning("[CLI] All database tables dropped")
                    print('✓ Database dropped successfully!')
                except Exception as e:
                    logger.error(f"[CLI] Error dropping database: {e}")
                    print(f'✗ Error dropping database: {e}')
        else:
            logger.info("[CLI] Drop database cancelled")
            print('Drop database cancelled')

    @app.cli.command()
    def seed_db():
        """Seed database with demo data"""
        logger.info("[CLI] Seeding database with demo user...")
        
        from nexus_core.quantum_models import User, PatientProfile

        with app.app_context():
            try:
                # Check if demo user already exists
                existing = User.query.filter_by(email='demo@auramedix.ai').first()
                if existing:
                    logger.info("[CLI] Demo user already exists")
                    print('Demo user already exists!')
                    return

                demo_user = User(
                    email='demo@auramedix.ai',
                    username='demo',
                    full_name='Demo User',
                    is_verified=True
                )

                demo_user.set_password('Demo@2024')

                db.session.add(demo_user)
                db.session.commit()

                profile = PatientProfile(
                    user_id=demo_user.id,
                    age=35,
                    gender='Male',
                    height_cm=175,
                    weight_kg=75,
                    blood_type='O+'
                )

                db.session.add(profile)
                db.session.commit()

                logger.info("[CLI] Demo user created successfully")
                print('✓ Demo user created successfully!')
                print('Email: demo@auramedix.ai')
                print('Password: Demo@2024')
            except Exception as e:
                db.session.rollback()
                logger.error(f"[CLI] Error seeding database: {e}")
                print(f'✗ Error seeding database: {e}')

    @app.cli.command()
    def check_db():
        """Check database status and tables"""
        logger.info("[CLI] Checking database status...")
        
        with app.app_context():
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                print("\n" + "="*60)
                print("DATABASE STATUS CHECK")
                print("="*60)
                print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
                print(f"Tables ({len(tables)}):")
                for table in sorted(tables):
                    columns = len(inspector.get_columns(table))
                    indexes = len(inspector.get_indexes(table))
                    print(f"  • {table:<30} ({columns} columns, {indexes} indexes)")
                
                print("\nIndexes by table:")
                for table in sorted(tables):
                    indexes = inspector.get_indexes(table)
                    if indexes:
                        print(f"\n  {table}:")
                        for idx in indexes:
                            print(f"    - {idx['name']}: {idx['column_names']}")
                
                print("\n" + "="*60)
                logger.info("[CLI] Database check completed")
                
            except Exception as e:
                logger.error(f"[CLI] Error checking database: {e}")
                print(f'✗ Error checking database: {e}')
