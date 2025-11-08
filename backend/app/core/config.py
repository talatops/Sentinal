"""Configuration management for Flask application."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"postgresql://{os.environ.get('POSTGRES_USER', 'sentinal_user')}:" \
        f"{os.environ.get('POSTGRES_PASSWORD', 'password')}@" \
        f"{os.environ.get('POSTGRES_HOST', 'postgres')}:" \
        f"{os.environ.get('POSTGRES_PORT', '5432')}/" \
        f"{os.environ.get('POSTGRES_DB', 'sentinal')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # GitHub OAuth
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
    GITHUB_CALLBACK_URL = os.environ.get('GITHUB_CALLBACK_URL', 'http://localhost/callback')
    
    # Security Tools
    TRIVY_API_URL = os.environ.get('TRIVY_API_URL', 'http://trivy:8080')
    OWASP_ZAP_API_URL = os.environ.get('OWASP_ZAP_API_URL', 'http://zap:8090')
    SONARQUBE_URL = os.environ.get('SONARQUBE_URL', 'http://sonarqube:9000')
    SONARQUBE_TOKEN = os.environ.get('SONARQUBE_TOKEN', '')
    SONARQUBE_PROJECT_KEY = os.environ.get('SONARQUBE_PROJECT_KEY', 'sentinal')
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # GDPR Compliance
    GDPR_DATA_RETENTION_DAYS = int(os.environ.get('GDPR_DATA_RETENTION_DAYS', 365))
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://test_user:test_pass@localhost/test_sentinal'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 5


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # Force HTTPS in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

