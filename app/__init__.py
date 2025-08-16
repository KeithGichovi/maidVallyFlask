from flask import Flask
from app.extensions import *
from config import Config
import os

def create_app():
   # Get the project root and static/template directories
   project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
   template_dir = os.path.join(project_root, 'templates')
   static_dir = os.path.join(project_root, 'static')
   
   # Initialize Flask app
   app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
   app.config.from_object(Config)

   # Initialize extensions
   db.init_app(app)
   migrate.init_app(app, db)
   login_manager.init_app(app)
   cors.init_app(app)
   mail.init_app(app)
   csrf.init_app(app)
   bootstrap.init_app(app)

   # configure celery
   make_celery(app)

   # import tasks to register them
   from app import tasks

   # User loader for Flask-Login
   @login_manager.user_loader
   def load_user(user_id):
      from app.models import User  # Avoid circular imports by placing inside function
      return User.query.get(int(user_id))

   # Flask-Login settings
   login_manager.login_view = 'auth.login'
   login_manager.login_message = 'Please log in to access this page.'
   login_manager.login_message_category = 'info'

   # Import views and models after app and extensions setup
   from app import models

   # Register Blueprints for different routes (modular views)
   from app.views import auth_bp, main_bp, clients_bp, jobs_bp, http_bp
   app.register_blueprint(auth_bp)
   app.register_blueprint(main_bp)
   app.register_blueprint(clients_bp)
   app.register_blueprint(jobs_bp)
   app.register_blueprint(http_bp)

   @app.template_filter('format_enum')
   def format_enum(value):
      """Format enum values for display"""
      if value:
         # Convert enum to string value if needed
         str_value = value.value if hasattr(value, 'value') else str(value)
         return str_value.replace('_', ' ').title()
      return value

   return app
