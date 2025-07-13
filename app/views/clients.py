from app.models import Client, Job, Payment
from app.views import clients_bp
from flask import render_template, redirect, url_for
from flask_login import login_required
from app.forms.clients import AddClientForm, EditClientForm
from app.models import Client, db, ClientTypeEnum, ClientStatusEnum
from flask import flash, jsonify


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

@clients_bp.route('/edit_client/<int:client_id>', methods=['GET', 'POST'])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    form = EditClientForm(obj=client)  
    
    if form.validate_on_submit():
        client.name = form.name.data
        client.client_type = form.client_type.data
        client.status = form.status.data
        
        # No need for db.session.add() when updating existing objects
        db.session.commit()
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients.clients'))
    
    return render_template('clients/edit_client.html', form=form, client=client)

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