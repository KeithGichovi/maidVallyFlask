from app.forms.auth import LoginForm, RegistrationForm
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from app.views import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        # check if the user is in the database
        if user and check_password_hash(user.password_hash, form.password.data):            
            login_user(user)
            # if user has not confirmed email send them to email confirmation
            if not user.has_confirmed_email:
                return redirect(url_for('auth.email_confirmation'))
            
            # Simple redirect - always go to dashboard
            return redirect(url_for('main.dashboard'))
        
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():

        if User.query.filter_by(email=form.email.data).first():
            flash('Email is already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        if not User.check_email_whitelist(form.email.data):
            flash('Email is already registered', 'error')
            return render_template('auth/register.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/email_confirmation')
@login_required
def email_confirmation():
    if current_user.has_confirmed_email:
        return redirect(url_for('main.dashboard'))
    # This is where the celery task or flask mail function for sending email will go
    return render_template('auth/email_confirmation.html')