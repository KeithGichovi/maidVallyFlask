import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

class Config:
    ALLOWED_EMAILS = os.getenv('ALLOWED_EMAILS').split(',')
    # Flask-SQLAlchemy configurations
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Sasha1301@localhost:3306/maidvally'
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
    REDIS_URL = 'redis://localhost:6379/0'
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    CELERY_TIMEZONE = TIMEZONE
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    