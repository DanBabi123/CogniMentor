# from flask import render_template, request, session, redirect, url_for
# from flask_login import login_required, current_user
# from . import advisor
# from models.subject import Subject

# @advisor.route('/start')
# @login_required
# def start():
#     # Fetch subjects from the database based on the user's selected goal
#     # If no goal is selected, default to 'Technology'
#     category = current_user.selected_goal or 'Technology'
#     db_subjects = Subject.query.filter_by(category=category).all()
    
#     return render_template('advisor/start.html', subjects=db_subjects)

# @advisor.route('/analyze/<int:subject_id>')
# @login_required
# def analyze(subject_id):
#     from ai_engine.advisor_engine import advisor_engine
    
#     subject_obj = Subject.query.get_or_404(subject_id)
    
#     # Get direct career utility analysis using the subject name and user's goal
#     analysis = advisor_engine.get_career_insight(
#         subject=subject_obj.name, 
#         selected_goal=current_user.selected_goal
#     )
    
#     return render_template('advisor/analysis.html', analysis=analysis, subject=subject_obj.name)

from flask import render_template, request, session, redirect, url_for
from flask_login import login_required, current_user
from . import advisor
from models import Subject #type: ignore

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

@advisor.route('/analyze/<string:subject_name>')
@login_required
def analyze(subject_name):
    return render_template('advisor/assess.html', subject=subject_name)

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
    roadmap = advisor_engine.generate_roadmap(subject, level, goal, time, current_user.name)#type: ignore
    
    return render_template('advisor/roadmap.html', roadmap=roadmap, subject=subject)