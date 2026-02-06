from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database.database import db
from database.models import User, Subject, Topic, LearningProgress, QuizAttempt
from auth.decorators import admin_required
from sqlalchemy import func
from datetime import datetime, timedelta

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

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot delete your own admin account!', 'error')
        return redirect(url_for('admin.manage_users'))

    # Delete related data manually to ensure clean removal
    LearningProgress.query.filter_by(user_id=user.id).delete()
    QuizAttempt.query.filter_by(user_id=user.id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} has been deleted successfully.', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/content')
@login_required
@admin_required
def content_manager():
    subjects = Subject.query.all()
    return render_template('admin/content_manager.html', subjects=subjects)

@admin.route('/subjects', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        icon = request.form.get('icon')
        
        if not name or not category:
            flash('Name and Category are required!', 'error')
        else:
            new_subject = Subject(
                name=name, 
                description=description, 
                category=category, 
                icon=icon or 'school',
                image_file='default.jpg' # Logic for image upload can be added later
            )
            db.session.add(new_subject)
            db.session.commit()
            flash(f'Subject "{name}" added successfully!', 'success')
            return redirect(url_for('admin.manage_subjects'))
            
    subjects = Subject.query.all()
    return render_template('admin/manage_subjects.html', subjects=subjects)

@admin.route('/subjects/delete/<int:subject_id>', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject "{subject.name}" deleted.', 'success')
    return redirect(url_for('admin.manage_subjects'))
@admin.route('/analytics')
@login_required
@admin_required
def analytics():
    # 1. Key Metrics
    total_users = User.query.count()
    
    # Active Learners: Users with activity in last 30 days
    last_month = datetime.utcnow() - timedelta(days=30)
    active_users = db.session.query(LearningProgress.user_id).filter(
        LearningProgress.last_accessed >= last_month
    ).distinct().count() or 0
    
    # 2. Growth Data (Users created per month)
    # Note: SQLite 'strftime' usage.
    growth_query = db.session.query(
        func.strftime('%Y-%m', User.created_at).label('month'),
        func.count(User.id)
    ).group_by('month').order_by('month').limit(6).all()
    
    growth_labels = []
    growth_values = []
    
    for month_str, count in growth_query:
        try:
            d = datetime.strptime(month_str, '%Y-%m')
            growth_labels.append(d.strftime('%b'))
        except:
            growth_labels.append(month_str)
        growth_values.append(count)
        
    if not growth_values:
        growth_labels = ['No Data']
        growth_values = [0]
        
    # 3. Category Popularity
    cat_query = db.session.query(
        User.selected_goal, func.count(User.id)
    ).filter(User.selected_goal.isnot(None)).group_by(User.selected_goal).all()
    
    cat_labels = [r[0] for r in cat_query]
    cat_values = [r[1] for r in cat_query]
    
    # Fallback to Subject Categories if User Goals are empty
    if not cat_labels:
       cat_query_sub = db.session.query(Subject.category, func.count(Subject.id)).group_by(Subject.category).all()
       cat_labels = [r[0] for r in cat_query_sub]
       cat_values = [r[1] for r in cat_query_sub]

    subject_popularity = {
        'labels': cat_labels,
        'data': cat_values
    }
    
    return render_template('admin/analytics.html', 
                           total_users=total_users,
                           active_users=active_users,
                           growth_data=growth_values,
                           growth_labels=growth_labels,
                           subject_data=subject_popularity)

@admin.route('/settings')
@login_required
@admin_required
def settings():
    flash('Admin Settings coming soon!', 'info')
    return redirect(url_for('admin.dashboard'))
