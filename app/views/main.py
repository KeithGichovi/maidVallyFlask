# app/views/main.py
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.views import main_bp

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
    return render_template('main/dashboard.html', user=current_user)