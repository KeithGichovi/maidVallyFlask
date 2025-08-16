# app.py
from app import create_app
from app.extensions import db
import os

app = create_app()


if __name__ == "__main__":
    # Create tables when running directly
    with app.app_context():
        db.create_all()
        from app.init_data import init_job_types, init_sample_data
        init_job_types()
        init_sample_data()
    app.run(host='0.0.0.0', port=5000)