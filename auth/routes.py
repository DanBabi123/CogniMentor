from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from database.database import db
from database.models import User
from . import auth
from .forms import LoginForm, SignupForm

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from database.database import db
from database.models import User
from . import auth
from .forms import LoginForm, SignupForm, VerificationForm, ResetRequestForm, ResetPasswordForm
from .otp_service import OTPService

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if not user.is_verified:
                flash('Please verify your account first.', 'warning')
                OTPService.send_otp(user.id)
                session['verification_user_id'] = user.id
                return redirect(url_for('auth.verify'))
            
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'error')
            
    return render_template('auth/login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = SignupForm()
    if form.validate_on_submit():
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.set_password(form.password.data)
        user.is_verified = False # Enforce OTP
        db.session.add(user)
        db.session.commit()
        
        # Send OTP
        OTPService.send_otp(user.id)
        session['verification_user_id'] = user.id
        
        flash('Account created! Please verify your email.', 'info')
        return redirect(url_for('auth.verify'))
        
    return render_template('auth/signup.html', form=form)

@auth.route('/verify', methods=['GET', 'POST'])
def verify():
    user_id = session.get('verification_user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
        
    form = VerificationForm()
    if form.validate_on_submit():
        success, message = OTPService.verify_otp(user_id, form.otp.data)
        if success:
            user = db.session.get(User, user_id)
            login_user(user)
            flash('Account Verified! Welcome.', 'success')
            session.pop('verification_user_id', None)
            return redirect(url_for('main.dashboard'))
        else:
            flash(message, 'error')
            
    return render_template('auth/verify.html', form=form)

from .forms import LoginForm, SignupForm, VerificationForm, ResetRequestForm, ResetPasswordForm
import uuid
from datetime import datetime, timedelta
from database.models import PasswordReset

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Generate Token
            token = str(uuid.uuid4())
            reset_entry = PasswordReset()
            reset_entry.user_id = user.id
            reset_entry.token = token
            reset_entry.expires_at = datetime.utcnow() + timedelta(minutes=10)
            db.session.add(reset_entry)
            db.session.commit()
            
            # Send Email (Mock)
            flash(f'Reset link sent to {user.email}: /auth/reset_password/{token}', 'info')
        else:
            flash('If email exists, reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_request.html', form=form)

@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    reset_entry = PasswordReset.query.filter_by(token=token).first()
    if not reset_entry or reset_entry.expires_at < datetime.utcnow():
        flash('Invalid or expired token.', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = db.session.get(User, reset_entry.user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('auth.reset_password_request'))
        user.set_password(form.password.data)
        db.session.delete(reset_entry) # Cleanup
        db.session.commit()
        flash('Your password has been updated! You can now login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', form=form)
