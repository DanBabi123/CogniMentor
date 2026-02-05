from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database.database import db
from database.models import User, Subject, Topic
from auth.decorators import admin_required

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_subjects': Subject.query.count(),
        'system_health': 'Good'
    }
    return render_template('dashboard/admin_dashboard.html', stats=stats)

@admin.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/content')
@login_required
@admin_required
def content_manager():
    subjects = Subject.query.all()
    return render_template('admin/content_manager.html', subjects=subjects)

@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # Stub for analytics
    stats = {
        'total_users': User.query.count(),
        'total_subjects': Subject.query.count(),
        'system_health': 'Good'
    }
    return render_template('dashboard/admin_dashboard.html', stats=stats) # Re-use dashboard for now

@admin.route('/settings')
@login_required
@admin_required
def settings():
    flash('Admin Settings coming soon!', 'info')
    return redirect(url_for('admin.dashboard'))
