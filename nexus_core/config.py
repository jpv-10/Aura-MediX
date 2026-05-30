"""
AURA MEDIX — Configuration Matrix
Environment-specific settings for the Nexus platform
"""
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class NexusConfig:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'nexus-quantum-fallback-key-2024')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # AI Engine
    AI_MODEL_VERSION = 'v2.1.0'
    MAX_CHAT_HISTORY = 20
    PREDICTION_CONFIDENCE_THRESHOLD = 0.5

    # Pagination
    RECORDS_PER_PAGE = 20
    CHAT_MESSAGES_PER_PAGE = 50

    # Database migration safety
    SQLALCHEMY_ECHO = False


class DevelopmentConfig(NexusConfig):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "instance", "nexus_core.db")}'
    )
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = False


class ProductionConfig(NexusConfig):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '')
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_SSL_STRICT = True

    # Connection pooling for PostgreSQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }


class TestingConfig(NexusConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# FIXED: Renamed from 'config' to 'config_map' to avoid naming conflicts
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}