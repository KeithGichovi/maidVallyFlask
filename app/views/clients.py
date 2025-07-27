from app.models import Client, Job, Payment, PaymentStatus
from app.views import clients_bp
from flask import render_template, redirect, url_for, request
from flask_login import login_required
from app.forms.clients import AddClientForm, EditClientForm
from app.models import Client, db, ClientTypeEnum, ClientStatusEnum, Job
from flask import flash, jsonify
from datetime import datetime, timedelta


@clients_bp.route('/clients', methods=['GET', 'POST'])
@login_required
def clients():
    form = AddClientForm()

    if form.validate_on_submit():
        # Create new client
        new_client = Client(
            name=form.name.data,
            client_type=form.client_type.data,
            status=form.status.data
        )
        db.session.add(new_client)
        db.session.commit()
        
        flash('Client added successfully!', 'success')
        return redirect(url_for('clients.clients'))
    
    clients = Client.query.all()  # Fetch all clients
    return render_template(
        'clients/clients.html',
        clients=clients,
        form=form,
        ClientTypeEnum=ClientTypeEnum,
        ClientStatusEnum=ClientStatusEnum
    )

from datetime import datetime, timedelta

@clients_bp.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = EditClientForm(obj=client)  
    
    if form.validate_on_submit():
        client.name = form.name.data
        client.client_type = form.client_type.data
        client.status = form.status.data
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients.clients'))
    
    now = datetime.now()
    
    # Calculate month names
    current_month_name = now.strftime('%B %Y')
    previous_month = now.replace(day=1) - timedelta(days=1)
    previous_month_name = previous_month.strftime('%B %Y')
    
    # Calculate statistics properly
    all_jobs = client.jobs.all()
    
    # Current month jobs
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_jobs = [job for job in all_jobs if job.time_started >= current_month_start]
    current_month_amount = sum(job.total_amount for job in current_month_jobs)
    current_month_unpaid = [job for job in current_month_jobs if job.total_paid < job.total_amount]
    
    # All outstanding jobs
    outstanding_jobs = [job for job in all_jobs if job.total_paid < job.total_amount]
    outstanding_amount = sum(job.total_amount - job.total_paid for job in outstanding_jobs)
    
    # Total stats
    total_amount = sum(job.total_amount for job in all_jobs)
    total_paid = sum(job.total_paid for job in all_jobs)
    
    stats = {
        'total_jobs': len(all_jobs),
        'total_amount': total_amount,
        'total_paid': total_paid,
        'outstanding_amount': outstanding_amount,
        'current_month_jobs': len(current_month_jobs),
        'current_month_amount': current_month_amount,
        'current_month_unpaid': len(current_month_unpaid),
        'outstanding_jobs_count': len(outstanding_jobs)
    }
    
    return render_template('clients/edit_client.html', 
        form=form, 
        client=client,
        now=now,
        current_month_name=current_month_name,
        previous_month_name=previous_month_name,
        stats=stats
    )

@clients_bp.route('/deactivate/<int:client_id>', methods=['POST'])
@login_required
def deactivate_client(client_id):
    client = Client.query.get_or_404(client_id)
    client.status = 'INACTIVE'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Client deactivated successfully'})

@clients_bp.route('/activate/<int:client_id>', methods=['POST'])
@login_required
def activate_client(client_id):

    client = Client.query.get_or_404(client_id)
    client.status = 'ACTIVE'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Client activated successfully'})


@clients_bp.route('/generate_invoice/<int:client_id>')
@clients_bp.route('/generate_invoice/<int:client_id>/<period>')
@login_required
def generate_invoice(client_id, period=None):
    from datetime import datetime, timedelta
    
    client = Client.query.get_or_404(client_id)
    api_json = {
        "client_id": client.id,
        "client_name": client.name,
        "jobs": []
    }
    
    # Handle URL parameters - FIX: Convert string to boolean
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    unpaid_only_param = request.args.get('unpaid_only')
    
    # Convert string to boolean
    unpaid_only = unpaid_only_param in ['true', 'True', '1', 'yes', 'on'] if unpaid_only_param else False

    # Helper function to check if job should be included
    def should_include_job(job):
        if unpaid_only:
            payments = Payment.query.filter_by(job_id=job.id).first()
            is_unpaid = payments is None or payments.payment_status == PaymentStatus.UNPAID
            return is_unpaid
        return True
    
    if start_date and end_date:
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        
        list_of_jobs_in_custom_range = Job.query.filter_by(client_id=client_id).filter(
            Job.time_started.between(start_datetime, end_datetime)
        ).all()
        
        for job in list_of_jobs_in_custom_range:
            if should_include_job(job):
                job_details = {
                    "job_id": job.id,
                    "job_type": job.job_type.name,
                    "total_amount": job.total_amount,
                    "time_started": job.time_started.isoformat(),
                    "time_ended": job.time_ended.isoformat(),
                    "location": job.location,
                    "description": job.description
                }
                api_json["jobs"].append(job_details)
        
        return jsonify(api_json)

    elif period == 'current_month':
        print("DEBUG: Current month section")
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        list_of_jobs_in_current_month = Job.query.filter_by(client_id=client_id).filter(
            Job.time_started >= month_start
        ).all()
        
        print(f"DEBUG: Found {len(list_of_jobs_in_current_month)} jobs in current month")
        
        for job in list_of_jobs_in_current_month:
            if should_include_job(job):
                job_details = {
                    "job_id": job.id,
                    "job_type": job.job_type.name,
                    "total_amount": job.total_amount,
                    "time_started": job.time_started.isoformat(),
                    "time_ended": job.time_ended.isoformat(),
                    "location": job.location,
                    "description": job.description
                }
                api_json["jobs"].append(job_details)        
        return jsonify(api_json)

    elif period == 'last_month':
        now = datetime.now()
        last_month_end = now.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_end = last_month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        list_of_jobs_in_last_month = Job.query.filter_by(client_id=client_id).filter(
            Job.time_started.between(last_month_start, last_month_end)
        ).all()
        
        for job in list_of_jobs_in_last_month:
            if should_include_job(job):
                job_details = {
                    "job_id": job.id,
                    "job_type": job.job_type.name,
                    "total_amount": job.total_amount,
                    "time_started": job.time_started.isoformat(),
                    "time_ended": job.time_ended.isoformat(),
                    "location": job.location,
                    "description": job.description
                }
                api_json["jobs"].append(job_details)
        
        return jsonify(api_json)

    elif period == 'all_unpaid' or unpaid_only:
        list_of_jobs = Job.query.filter_by(client_id=client_id).all()
        for job in list_of_jobs:
            payments = Payment.query.filter_by(job_id=job.id).first()
            if payments is None or payments.payment_status == PaymentStatus.UNPAID:
                job_details = {
                    "job_id": job.id,
                    "job_type": job.job_type.name,
                    "total_amount": job.total_amount,
                    "time_started": job.time_started.isoformat(),
                    "time_ended": job.time_ended.isoformat(),
                    "location": job.location,
                    "description": job.description
                }
                api_json["jobs"].append(job_details)
        
        return jsonify(api_json)

    # Default - all jobs
    else:
        all_jobs = Job.query.filter_by(client_id=client_id).all()
        for job in all_jobs:
            if should_include_job(job):
                job_details = {
                    "job_id": job.id,
                    "job_type": job.job_type.name,
                    "total_amount": job.total_amount,
                    "time_started": job.time_started.isoformat(),
                    "time_ended": job.time_ended.isoformat(),
                    "location": job.location,
                    "description": job.description
                }
                api_json["jobs"].append(job_details)
        
        return jsonify(api_json)