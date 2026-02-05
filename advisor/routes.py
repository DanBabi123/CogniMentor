from flask import render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from . import advisor
from database.models import Subject

@advisor.route('/start')
@login_required
def start():
    subjects = [
        "Python Programming",
        "Data Structures & Algorithms",
        "Web Development",
        "Machine Learning",
        "Artificial Intelligence",
        "Databases (SQL)",
        "Quantitative Aptitude",
        "GATE CSE"
    ]
    return render_template('advisor/start.html', subjects=subjects)

@advisor.route('/assess', methods=['POST'])
@login_required
def assess():
    selected_subject = request.form.get('subject')
    session['advisor_subject'] = selected_subject
    return render_template('advisor/assess.html', subject=selected_subject)

@advisor.route('/generate', methods=['POST'])
@login_required
def generate():
    from ai_engine.advisor_engine import advisor_engine
    
    # Collect inputs
    level = request.form.get('level')     # Beginner, Intermediate, Advanced
    goal = request.form.get('goal')       # Exams, Job, Project, Hobby
    time = request.form.get('time')       # 30 mins, 1 hr, 2 hrs+
    subject = session.get('advisor_subject')
    
    if not subject:
        return redirect(url_for('advisor.start'))
        
    # Generate Roadmap
    roadmap = advisor_engine.generate_roadmap(subject, level, goal, time, current_user.name)
    
    return render_template('advisor/roadmap.html', roadmap=roadmap, subject=subject)
