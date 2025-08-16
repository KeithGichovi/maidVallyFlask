from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.views import main_bp
from app.models import *
from datetime import datetime, timedelta


def get_jobs_for_month(month, year):
    """Get all jobs for a specific month and year"""
    all_jobs = Job.query.all()
    month_jobs = []
    for job in all_jobs:
        if job.time_started.month == month and job.time_started.year == year:
            month_jobs.append(job)
    return month_jobs

def calculate_completion_rate(jobs):
    """Calculate completion rate for a list of jobs"""
    if not jobs:
        return 0
    completed = [job for job in jobs if job.time_ended is not None]
    return round((len(completed) / len(jobs)) * 100)

def calculate_payment_rate(jobs):
    """Calculate payment rate for a list of jobs"""
    if not jobs:
        return 0
    paid = [job for job in jobs if job.total_paid > 0]
    return round((len(paid) / len(jobs)) * 100)

def calculate_avg_job_value(jobs):
    """Calculate average job value for a list of jobs"""
    if not jobs:
        return 0
    total = sum(job.total_amount for job in jobs)
    return total / len(jobs)

@main_bp.route('/')
def index():
    # Redirect to dashboard if logged in, otherwise to login
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Count all clients
    active_clients = len(Client.query.filter_by(status='ACTIVE').all())
    
    # Get all jobs and calculate totals
    jobs = Job.query.all()
    total_profit = sum(job.profit for job in jobs)
    total_paid = sum(job.total_paid for job in jobs)
    
    # Get current month and last month
    now = datetime.utcnow()
    current_month = now.month
    current_year = now.year
    
    if current_month == 1:
        last_month = 12
        last_year = current_year - 1
    else:
        last_month = current_month - 1
        last_year = current_year
    
    # Get jobs for both months
    this_month_jobs = get_jobs_for_month(current_month, current_year)
    last_month_jobs = get_jobs_for_month(last_month, last_year)
    
    # Calculate completion rates
    completion_rate = calculate_completion_rate(this_month_jobs)
    last_completion_rate = calculate_completion_rate(last_month_jobs)
    completion_trend = completion_rate - last_completion_rate
    
    # Calculate average job values
    avg_job_value = calculate_avg_job_value(this_month_jobs)
    last_avg_job_value = calculate_avg_job_value(last_month_jobs)
    
    if last_avg_job_value > 0:
        job_value_trend = round(((avg_job_value - last_avg_job_value) / last_avg_job_value * 100))
    else:
        job_value_trend = 0
    
    # Calculate job count trend
    total_jobs_month = len(this_month_jobs)
    if len(last_month_jobs) > 0:
        jobs_trend = round(((len(this_month_jobs) - len(last_month_jobs)) / len(last_month_jobs) * 100))
    else:
        jobs_trend = 0
    
    # Calculate payment rates
    payment_rate = calculate_payment_rate(this_month_jobs)
    last_payment_rate = calculate_payment_rate(last_month_jobs)
    payment_trend = payment_rate - last_payment_rate
    
    return render_template(
        'main/dashboard.html',
        user=current_user,
        active_clients=active_clients,
        total_profit=total_profit,
        total_paid=total_paid,
        # Performance metrics
        completion_rate=completion_rate,
        completion_trend=completion_trend,
        avg_job_value=avg_job_value,
        job_value_trend=job_value_trend,
        total_jobs_month=total_jobs_month,
        jobs_trend=jobs_trend,
        payment_rate=payment_rate,
        payment_trend=payment_trend
    )

@main_bp.route('/health')
def health_check():
    try:
        return 'OK', 200
    except Exception as e:
        return str(e), 500