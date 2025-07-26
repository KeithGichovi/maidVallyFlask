from app.models import Client, Job, Payment
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
    client = Client.query.get_or_404(client_id)
    
    # Handle URL parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    unpaid_only = request.args.get('unpaid_only')
    
    if start_date and end_date:
        # Custom date range
        pass
    elif period == 'current_month':
        # Current month logic
        pass
    elif period == 'last_month':
        # Previous month logic
        pass
    elif period == 'all_unpaid':
        # All unpaid jobs
        pass
    
    # Generate invoice and return
    flash(f'Invoice generated for {client.name}', 'success')
    return redirect(url_for('clients.edit_client', client_id=client_id))