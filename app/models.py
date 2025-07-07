from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum

from app.extensions import db

# Enum Definitions
class ExpenseType(enum.Enum):
    SUPPLIES = "SUPPLIES"
    TRANSPORTATION = "TRANSPORTATION"
    EQUIPMENT = "EQUIPMENT"

class ClientTypeEnum(enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"

class ClientStatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class PaymentStatus(enum.Enum):
    PAID = "PAID"
    UNPAID = "UNPAID"

# User model for authentication (Flask-Login)
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(512))
    has_confirmed_email = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<User {self.name}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def check_email_whitelist(email):
        """
            Check if the given email is in the whitelist.

            Args:
                email (str): The email to check.

            Returns:
                bool: True if the email is in the whitelist, False otherwise.
        """
        from flask import current_app
        return True if email in current_app.config['ALLOWED_EMAILS'] else False
    
    def is_authorized(self):
        """
            Check if the user's email is in the whitelist.

            Returns:
                bool: True if the user is authorized, False otherwise.
        """
        return self.check_email_whitelist(self.email)

# Business Models
class Client(db.Model):
    __tablename__ = "clients"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    client_type = db.Column(db.Enum(ClientTypeEnum), nullable=False)
    status = db.Column(db.Enum(ClientStatusEnum), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    jobs = db.relationship("Job", back_populates="client", lazy='dynamic')

    def __repr__(self):
        return f"<Client(id={self.id}, name={self.name}, client_type={self.client_type}, status={self.status})>"

class JobType(db.Model):
    __tablename__ = "jobtype"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    jobs = db.relationship("Job", back_populates="job_type", lazy='dynamic')

    def __repr__(self):
        return f"<JobType(id={self.id}, name={self.name})>"

class Job(db.Model):
    __tablename__ = "job"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_type_id = db.Column(db.Integer, db.ForeignKey("jobtype.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    time_started = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    time_ended = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(255), nullable=True)

    # Relationships
    job_type = db.relationship("JobType", back_populates="jobs")
    client = db.relationship("Client", back_populates="jobs")
    payments = db.relationship("Payment", back_populates="job", lazy='dynamic')
    expenses = db.relationship("Expense", back_populates="job", lazy='dynamic')

    @property
    def total_paid(self):
        """Calculate total amount paid for this job"""
        return sum(payment.amount for payment in self.payments if payment.payment_status == PaymentStatus.PAID)
    
    @property
    def total_expenses(self):
        """Calculate total expenses for this job"""
        return sum(expense.amount for expense in self.expenses)
    
    @property
    def profit(self):
        """Calculate profit (total_amount - total_expenses)"""
        return self.total_amount - self.total_expenses

    def __repr__(self):
        return f"<Job(id={self.id}, client={self.client.name if self.client else 'None'}, total_amount={self.total_amount})>"

class Expense(db.Model):
    __tablename__ = "expenses"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    expense_type = db.Column(db.Enum(ExpenseType), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    job = db.relationship("Job", back_populates="expenses")

    def __repr__(self):
        return f"<Expense(id={self.id}, job_id={self.job_id}, expense_type={self.expense_type}, amount={self.amount})>"

class Payment(db.Model):
    __tablename__ = "payments"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), nullable=False)
    notes = db.Column(db.String(255), nullable=True)

    # Relationships
    job = db.relationship("Job", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, job_id={self.job_id}, amount={self.amount}, payment_status={self.payment_status})>"