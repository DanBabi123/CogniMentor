from flask import render_template, abort, redirect, url_for
from flask_login import login_required, current_user
from flask_login import login_required, current_user
from database.models import Subject, Topic, QuizAttempt, Question, User
from database.database import db
from . import main
import random

@main.route('/')
def index():
    return render_template('simple_pages/landing.html')

@main.route('/contact')
def contact():
    return render_template('simple_pages/contact.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from ai_engine.adaptive import adaptive_engine
    
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    
    # Student Dashboard Logic
    subjects = Subject.query.all()
    recent_activity = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.timestamp.desc()).limit(5).all()
    recommendation = adaptive_engine.get_recommendation(current_user.id)
    
    return render_template('dashboard/index.html', 
                           subjects=subjects, 
                           recent_activity=recent_activity,
                           recommendation=recommendation)

@main.route('/subject/<int:subject_id>')
@login_required
def subject_view(subject_id):
    from database.models import LearningProgress
    
    subject = db.get_or_404(Subject, subject_id)
    topics = sorted(subject.topics, key=lambda t: t.order_index)
    
    # Fetch Progress
    progress_map = {
        p.topic_id: p 
        for p in LearningProgress.query.filter_by(user_id=current_user.id).all()
    }
    
    topic_status = []
    is_previous_completed = True # First one is unlocked
    
    for topic in topics:
        p = progress_map.get(topic.id)
        is_completed = p and p.status == 'Completed'
        
        status = {
            'topic': topic,
            'is_locked': not is_previous_completed,
            'is_completed': is_completed
        }
        topic_status.append(status)
        
        # Next one is unlocked only if this one is completed
        # But wait, if this one is unlocked but not completed, the NEXT one is locked. Correct.
        is_previous_completed = is_completed

    return render_template('dashboard/subject.html', subject=subject, topic_status=topic_status)

@main.route('/topic/<int:topic_id>')
@login_required
def topic_view(topic_id):
    from ai_engine.generator import ai_engine
    topic = db.get_or_404(Topic, topic_id)
    
    # Get all topics for sidebar navigation (ordered)
    all_topics = Topic.query.filter_by(subject_id=topic.subject_id).order_by(Topic.order_index).all()
    
    context = {
        'topic': topic,
        'all_topics': all_topics,
        'is_structured': False
    }

    if topic.content_payload:
        context['is_structured'] = True
        context['structured_data'] = topic.content_payload
    else:
        # Fallback to AI Generation
        context['content'] = {
            'beginner': ai_engine.generate_content(topic.title, 'beginner'),
            'concept': ai_engine.generate_content(topic.title, 'concept'),
            'analogy': ai_engine.generate_content(topic.title, 'analogy'),
            'visual': ai_engine.generate_content(topic.title, 'visual'),
            'mistakes': ai_engine.generate_content(topic.title, 'mistakes')
        }
    
    return render_template('dashboard/topic.html', **context)

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask import request, flash, redirect, url_for, current_app
    from werkzeug.utils import secure_filename
    import os
    from config import ALLOWED_EXTENSIONS
    from database.database import db

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        # Handle Profile Picture Upload
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Use User ID to prevent collisions and overwrite old pic
                file_ext = filename.rsplit('.', 1)[1].lower()
                new_filename = f"user_{current_user.id}.{file_ext}"
                
                # Create directory if not exists
                upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join(upload_folder, new_filename)
                file.save(file_path)
                
                current_user.profile_pic = new_filename
                db.session.commit()
                flash('Profile picture updated!', 'success')
            elif file.filename != '':
                 flash('Invalid file type. Allowed: png, jpg, jpeg, gif', 'error')
        
        # Handle other profile updates if any (e.g. name)
        if 'name' in request.form:
             current_user.name = request.form['name']
             db.session.commit()
             flash('Profile details updated.', 'success')

        return redirect(url_for('main.profile'))

    return render_template('dashboard/profile.html')

@main.route('/quiz/<int:topic_id>')
@login_required
def quiz_view(topic_id):
    from ai_engine.generator import ai_engine
    from flask import session
    from database.models import LearningProgress
    
    topic = db.get_or_404(Topic, topic_id)
    
    # Adaptive Logic: Determine Difficulty Mix
    progress = LearningProgress.query.filter_by(user_id=current_user.id, topic_id=topic.id).first()
    
    # Default: Balanced (Beginner)
    distribution = {'Easy': 2, 'Medium': 2, 'Hard': 1}
    
    if progress:
        cleared = progress.difficulty_cleared or {}
        # If struggling (last attempt low score? - we don't have last score handy easily here without query, assuming mastery_level proxies it)
        # Or simple check on cleared levels
        if cleared.get('Hard'):
            # Expert: Push for mastery
            distribution = {'Easy': 0, 'Medium': 1, 'Hard': 4}
        elif cleared.get('Medium'):
            # Intermediate: mix hard
            distribution = {'Easy': 1, 'Medium': 2, 'Hard': 2}
        elif cleared.get('Easy'):
            # Beginner passing easy
            distribution = {'Easy': 1, 'Medium': 3, 'Hard': 1}
        else:
            # Struggling or new
            distribution = {'Easy': 3, 'Medium': 2, 'Hard': 0}

    # Generate Dynamic Questions (Prioritize AI for adaptivity)
    questions = ai_engine.generate_quiz(topic.title, difficulty_distribution=distribution)
    
    # Store correct answers & difficulties in session for validation
    session['quiz_answers'] = {
        str(q['id']): {
            'correct': q['correct'],
            'difficulty': q.get('difficulty', 'Medium')
        } for q in questions
    }
    
    return render_template('dashboard/quiz.html', topic=topic, questions=questions)

@main.route('/quiz/<int:topic_id>/submit', methods=['POST'])
@login_required
def quiz_submit(topic_id):
    from ai_engine.generator import ai_engine
    from flask import session, request
    from database.database import db
    from database.models import LearningProgress, Subject
    
    topic = db.get_or_404(Topic, topic_id)
    answers_data = session.get('quiz_answers', {})
    
    score = 0
    total_questions = len(answers_data)

    # Track performance per difficulty
    diff_stats = {'Easy': {'total': 0, 'correct': 0}, 
                  'Medium': {'total': 0, 'correct': 0}, 
                  'Hard': {'total': 0, 'correct': 0}}
    
    correct_answers_map = {} 
    
    for q_id, q_data in answers_data.items():
        if q_data is None:
            continue
            
        correct_opt = q_data['correct']
        difficulty = q_data.get('difficulty', 'Medium')
        
        diff_stats.setdefault(difficulty, {'total': 0, 'correct': 0})
        diff_stats[difficulty]['total'] += 1
        
        user_answer = request.form.get(f'q_{q_id}')
        
        is_correct = False
        if user_answer and int(user_answer) == correct_opt:
            score += 1
            diff_stats[difficulty]['correct'] += 1
            is_correct = True
            
        correct_answers_map[q_id] = correct_opt

    # Update Progress
    progress = LearningProgress.query.filter_by(user_id=current_user.id, topic_id=topic.id).first()
    if not progress:
        progress = LearningProgress(user_id=current_user.id, topic_id=topic.id)
        db.session.add(progress)
    
    # Update difficulty cleared status
    # Rule: If > 60% accuracy in a difficulty, mark it cleared? 
    # Or stricter: 100% for passing a level? Let's say 60% for now to be forgiving.
    current_cleared = progress.difficulty_cleared or {}
    
    for diff, stats in diff_stats.items():
        if stats['total'] > 0:
            accuracy = stats['correct'] / stats['total']
            if accuracy >= 0.6: 
                current_cleared[diff] = True
            # Note: We don't un-clear if they fail this time, usually mastery is stickier.
            
    progress.difficulty_cleared = current_cleared
    progress.last_accessed = db.session.query(db.func.now()).scalar() # Use DB timestamp
    
    # Calculate Mastery & Status
    score_percent = (score / total_questions) * 100 if total_questions > 0 else 0
    progress.mastery_level = max(progress.mastery_level or 0, int(score_percent))
    
    # Progression Logic
    # Unlock next if: Global Score >= 70% AND (Medium Cleared or Hard Cleared)
    is_passed = score_percent >= 70 and (current_cleared.get('Medium') or current_cleared.get('Hard'))
    
    if is_passed:
        progress.status = 'Completed'
    elif progress.status != 'Completed':
        progress.status = 'In Progress'
        
    # Save Attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        topic_id=topic.id,
        score=score,
        max_score=total_questions
    )
    db.session.add(attempt)
    db.session.commit()
    
    # Generate Feedback
    feedback = ai_engine.generate_feedback(score, total_questions, topic.title)
    
    # Determine Strength Level
    strength_level = "Average"
    if current_cleared.get('Hard') and score_percent > 80:
        strength_level = "Strong"
    elif not current_cleared.get('Medium') and score_percent < 50:
        strength_level = "Weak"

    # Prepare detailed report
    report = []
    for q_id, q_data in answers_data.items():
        correct_opt = q_data['correct']
        
        q_text = "Dynamic Question (Text not persisted)"
        explanation = "Check concept content."
        
        # Try DB fetch if numeric ID
        try:
            if q_id.isdigit():
                 q_db = Question.query.get(int(q_id))
                 if q_db:
                     q_text = q_db.text
                     explanation = q_db.explanation
        except:
             pass

        user_val = request.form.get(f'q_{q_id}')
        user_ans_text = "Skipped"
        is_correct = False
        
        correct_ans_text = f"Option {chr(65+correct_opt)}" # Default A, B, C...

        if user_val:
            try:
                u_idx = int(user_val)
                if u_idx == correct_opt:
                    is_correct = True
                user_ans_text = f"Option {chr(65+u_idx)}"
            except:
                pass
                
        report.append({
            'question': q_text,
            'user_answer': user_ans_text,
            'correct_answer': correct_ans_text,
            'explanation': explanation,
            'is_correct': is_correct,
            'difficulty': q_data.get('difficulty', '-')
        })
    
    return render_template('dashboard/result.html', 
                           attempt=attempt, 
                           feedback=feedback, 
                           score_percent=score_percent, 
                           report=report,
                           strength_level=strength_level,
                           is_passed=is_passed,
                           diff_stats=diff_stats)

@main.route('/my_subjects')
@login_required
def my_subjects():
    from database.models import Subject
    # For now, show all subjects as "My Subjects" or filtering by enrollment if we had that model.
    # Assuming user has access to all for MVP.
    subjects = Subject.query.all()
    return render_template('dashboard/my_subjects.html', subjects=subjects)

@main.route('/content_generator', methods=['GET', 'POST'])
@login_required
def content_generator():
    from ai_engine.generator import ai_engine
    from flask import request
    
    generated_content = ""
    topic_title = ""
    
    if request.method == 'POST':
        topic_title = request.form.get('topic')
        mode = request.form.get('mode', 'beginner')
        
        if topic_title:
            generated_content = ai_engine.generate_content(topic_title, mode)
            
    return render_template('dashboard/content_generator.html', 
                           generated_content=generated_content, 
                           topic_title=topic_title)
