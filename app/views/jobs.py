from app.forms.jobs import AddJobForm
from app.models import Job, db, Payment, PaymentStatus
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.views import jobs_bp
from datetime import datetime

@jobs_bp.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    form = AddJobForm()
    
    # Handle form submission (like handleAddJob in React)
    if form.validate_on_submit():
        job = Job(
            job_type_id=form.job_type_id.data,
            client_id=form.client_id.data,
            total_amount=form.total_amount.data,
            time_started=form.time_started.data,
            time_ended=form.time_ended.data,
            location=form.location.data,
            description=form.description.data
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash('Job added successfully!', 'success')
        return redirect(url_for('jobs.jobs'))
    else:
        # Debug: Print form errors if validation fails
        if form.errors:
            print("Form validation errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"{field}: {error}", 'danger')
    
    # Get all jobs with related data (like fetchJobs in React)
    jobs = Job.query.options(
        db.joinedload(Job.client),
        db.joinedload(Job.job_type)
    ).order_by(Job.time_started.desc()).all()
    
    # Get search term from URL params
    search_term = request.args.get('search', '')
    
    # Filter jobs if search term exists
    if search_term:
        jobs = [job for job in jobs if 
            search_term.lower() in job.client.name.lower() or
            search_term.lower() in job.job_type.name.lower() or
            (job.description and search_term.lower() in job.description.lower()) or
            (job.location and search_term.lower() in job.location.lower())
        ]
    
    return render_template('jobs/jobs.html', 
        form=form, 
        jobs=jobs, 
        search_term=search_term)

# Fixed route with payment_method parameter
@jobs_bp.route('/toggle_payment/<int:job_id>/', methods=['POST'])
@login_required
def toggle_payment(job_id):
    job = Job.query.get_or_404(job_id)

    if job.total_paid >= job.total_amount:
        # Mark as unpaid - remove all payments
        Payment.query.filter_by(job_id=job_id).delete()
        flash('Job marked as unpaid!', 'warning')
    else:
        # Mark as paid - create a payment record with specified method
        payment = Payment(
            job_id=job_id,
            amount=job.total_amount,
            payment_date=datetime.now(),
            due_date=datetime.now(),
            payment_status=PaymentStatus.PAID
        )
        db.session.add(payment)
    
    db.session.commit()
    return redirect(url_for('jobs.jobs'))

@jobs_bp.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.total_paid > 0:
        flash('Cannot delete job with payments', 'danger')
        return redirect(url_for('jobs.jobs'))
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for('jobs.jobs'))