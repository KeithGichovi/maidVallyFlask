import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

class Config:
    allowed_emails_env = os.getenv('ALLOWED_EMAILS')
    ALLOWED_EMAILS = allowed_emails_env.split(',') if allowed_emails_env else None
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.urandom(32)
    TIMEZONE = 'Europe/London'
    
    # Security settings for DEVELOPMENT
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False  # CHANGED: False for HTTP development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Celery Config
    REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TIMEZONE = TIMEZONE
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    
    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')

    # Business Notifications
    BUSINESS_NOTIFICATIONS_ENABLED = True
    BUSINESS_NOTIFICATIONS_EMAIL = os.getenv('MAIL_DEFAULT_SENDER')