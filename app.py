# app.py
from app import create_app
from app.extensions import db
import os

app = create_app()

if __name__ == "__main__":
    # Create tables when running directly
    with app.app_context():
        db.create_all()
    
    app.run()