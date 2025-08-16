from app.forms.auth import LoginForm, RegistrationForm
from flask import render_template, redirect, url_for, flash, current_app
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from app.views import auth_bp
from flask_mail import Message
from app import mail

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
        print("User already confirmed - redirecting to dashboard")
        return redirect(url_for('main.dashboard'))

    try:
        send_confirmation_email(current_user.email)
        flash('Email confirmation sent', 'success')
    except Exception as e:
        flash('Email confirmation failed', 'error')
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    return render_template('auth/email_confirmation.html')


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Verify the token (expires after 1 hour)
        email = serializer.loads(token, salt='email-confirmation', max_age=3600)
    except SignatureExpired:
        flash('Confirmation link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.email_confirmation'))
    except BadSignature:
        flash('Invalid confirmation link.', 'error')
        return redirect(url_for('auth.email_confirmation'))
    
    # Find the user and confirm their email
    user = User.query.filter_by(email=email).first()
    if user:
        user.has_confirmed_email = True
        db.session.commit()
        flash('Email confirmed successfully!', 'success')
        return redirect(url_for('main.dashboard'))
    else:
        flash('User not found.', 'error')
        return redirect(url_for('auth.login'))

def generate_token(user_email):
    """
    Generate a unique token for the user
    """
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(user_email, salt='email-confirmation')


def send_confirmation_email(user_email):
    token = generate_token(user_email)
    confirm_url = url_for('auth.confirm_email', token=token, _external=True)
    
    subject = "Confirm your email - MaidVally"
    
    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Confirm Your Email - MaidVally</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8f9fa;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 300;">
                    🏠 MaidVally
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">
                    Professional Cleaning Services
                </p>
            </div>
            
            <!-- Main Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #2c3e50; margin: 0 0 20px 0; font-size: 24px; font-weight: 400;">
                    Welcome aboard! 🎉
                </h2>
                
                <p style="color: #555; line-height: 1.6; margin: 0 0 25px 0; font-size: 16px;">
                    Thank you for joining MaidVally! We're excited to help you connect with trusted cleaning professionals in your area.
                </p>
                
                <p style="color: #555; line-height: 1.6; margin: 0 0 30px 0; font-size: 16px;">
                    To complete your registration and start booking services, please confirm your email address:
                </p>
                
                <!-- Call to Action Button -->
                <div style="text-align: center; margin: 35px 0;">
                    <a href="{confirm_url}" 
                       style="background: linear-gradient(135deg, #28a745, #20c997); 
                              color: white; 
                              text-decoration: none; 
                              padding: 16px 32px; 
                              border-radius: 8px; 
                              font-size: 16px; 
                              font-weight: 600; 
                              display: inline-block; 
                              box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                              transition: all 0.3s ease;">
                        ✅ Confirm My Email Address
                    </a>
                </div>
                
                <!-- Alternative Link -->
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin: 30px 0; border-left: 4px solid #667eea;">
                    <p style="margin: 0 0 10px 0; color: #666; font-size: 14px; font-weight: 600;">
                        Can't click the button? Copy and paste this link:
                    </p>
                    <p style="margin: 0; word-break: break-all; color: #667eea; font-size: 13px; font-family: monospace;">
                        {confirm_url}
                    </p>
                </div>
                
                <!-- What's Next Section -->
                <div style="background: linear-gradient(135deg, #e3f2fd, #f3e5f5); padding: 25px; border-radius: 8px; margin: 30px 0;">
                    <h3 style="color: #2c3e50; margin: 0 0 15px 0; font-size: 18px;">
                        🚀 What's next?
                    </h3>
                    <ul style="color: #555; margin: 0; padding-left: 20px; line-height: 1.8;">
                        <li>Complete your profile setup</li>
                        <li>Browse your past cleaning jobs</li>
                        <li>Schedule your cleaning service</li>
                        <li>Enjoy serving your customers ✨</li>
                    </ul>
                </div>
                
                <!-- Security Notice -->
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 6px; margin: 25px 0;">
                    <p style="margin: 0; font-size: 14px;">
                        <strong>⏰ Important:</strong> This confirmation link will expire in 1 hour for your security.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #2c3e50; padding: 30px; text-align: center;">
                <p style="color: #bdc3c7; margin: 0 0 15px 0; font-size: 16px; font-weight: 500;">
                    Here to help!
                </p>
                
                <hr style="border: none; border-top: 1px solid #34495e; margin: 20px 0;">
                
                <p style="color: #95a5a6; margin: 0; font-size: 12px; line-height: 1.4;">
                    If you didn't create an account with MaidVally, please ignore this email.<br>
                    This email was sent from an automated system, please do not reply.
                </p>
                <hr style="border: none; border-top: 1px solid #34495e; margin: 20px 0;">
                </p>
                
                <p style="color: #7f8c8d; margin: 15px 0 0 0; font-size: 12px;">
                    © 2025 MaidVally. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = Message(
        subject=subject,
        recipients=[user_email],
        html=html_body,
        sender=current_app.config['MAIL_USERNAME']
    )

    mail.send(message)

class SignatureExpired(Exception):
    pass

class BadSignature(Exception):
    pass