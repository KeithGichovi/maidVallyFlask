# app/init_data.py
from app.extensions import db
from app.models import JobType, Client, Job, Payment, ClientTypeEnum, ClientStatusEnum, PaymentStatus
from datetime import datetime, timedelta

def init_job_types():
    """Initialize default job types if they don't exist"""
    default_job_types = [
        "House Cleaning",
        "Deep Cleaning", 
        "Office Cleaning",
        "Move-in/Move-out Cleaning",
        "Post-Construction Cleaning",
        "One-off Cleaning"
    ]
    
    for job_type_name in default_job_types:
        # Check if job type already exists
        existing = JobType.query.filter_by(name=job_type_name).first()
        if not existing:
            job_type = JobType(name=job_type_name)
            db.session.add(job_type)

    db.session.commit()

def init_sample_data():
    """Create sample data for testing (only if no data exists)"""
    
    # Only create sample data if no clients exist
    if Client.query.count() == 0:
        # Create sample client
        client = Client(
            name="Test Client Ltd",
            client_type=ClientTypeEnum.COMPANY,
            status=ClientStatusEnum.ACTIVE,
            address="123 Business Street",
            city="London", 
            state="England",
            post_code="EC1A 1BB"
        )
        db.session.add(client)
        db.session.flush()  # Get the ID without committing
        
        # Get the first job type
        job_type = JobType.query.first()
        if job_type:
            # Create sample job
            job = Job(
                job_type_id=job_type.id,
                client_id=client.id,
                total_amount=200.00,
                time_started=datetime.utcnow() - timedelta(days=15),
                time_ended=datetime.utcnow() - timedelta(days=15),
                location="Client Office",
                description="Weekly office cleaning"
            )
            db.session.add(job)
            db.session.flush()
            
            # Create overdue payment for testing Celery tasks
            overdue_payment = Payment(
                job_id=job.id,
                amount=200.00,
                payment_date=datetime.utcnow(),
                due_date=datetime.utcnow() - timedelta(days=5),  # 5 days overdue
                payment_status=PaymentStatus.UNPAID,
                notes="Test overdue payment for Celery testing"
            )
            db.session.add(overdue_payment)
        
        db.session.commit()
    else:
        pass