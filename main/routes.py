from flask import render_template, abort, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from flask_login import login_required, current_user
from database.models import Subject, Topic, QuizAttempt, Question, User, LearningProgress
from database.database import db
from . import main
import random

@main.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.current_subject_id:
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('main.goal_selection'))
    return render_template('simple_pages/landing.html')

@main.route('/set_goal/<category>')
@login_required
def set_goal(category):
    # Validate Category
    valid_categories = ['Technology', 'Government Exams', 'GATE']
    if category not in valid_categories:
        flash('Invalid Goal Selected', 'error')
        return redirect(url_for('main.goal_selection'))
        
    # Save Goal
    current_user.selected_goal = category
    db.session.commit()
    
    # Redirect to Subject Selection (filtered)
    return redirect(url_for('main.subject_selection', category=category))

@main.route('/goals')
@login_required
def goal_selection():
    subjects = Subject.query.all()
    return render_template('dashboard/goal_selection.html', subjects=subjects)

@main.route('/subjects')
@login_required
def subject_selection():
    category = request.args.get('category')
    
    if category:
        subjects = Subject.query.filter_by(category=category).all()
        header_title = f"{category}"
        subtitle = "Select your specific field of study"
    else:
        # Fallback or Show All
        subjects = Subject.query.all()
        header_title = "All Subjects"
        subtitle = "Choose a subject to start learning"
        
    return render_template('dashboard/my_subjects.html', subjects=subjects, title=header_title, subtitle=subtitle)

@main.route('/contact')
def contact():
    return render_template('simple_pages/contact.html')

@main.route('/privacy')
def privacy():
    return render_template('simple_pages/privacy.html')

@main.route('/terms')
def terms():
    return render_template('simple_pages/terms.html')

@main.route('/dashboard')
@login_required
def dashboard():
    from ai_engine.adaptive import adaptive_engine
    from sqlalchemy import func
    from datetime import datetime, timedelta
    from database.models import Subject, Topic, QuizAttempt, LearningProgress
    
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    # --- 0. Subject Context Enforcement (DB Persistence) ---
    subject_id = request.args.get('subject_id', type=int)
    
    # A. New Selection via URL (Update DB)
    if subject_id:
        current_user.current_subject_id = subject_id
        if current_user.is_first_login:
            current_user.is_first_login = False
        db.session.commit()
    
    # B. Retrieve Persisted Selection
    selected_subject_id = current_user.current_subject_id
        
    if not selected_subject_id:
        flash("Please select a subject to continue.", "info")
        return redirect(url_for('main.my_subjects'))
        
    current_subject = db.session.get(Subject, selected_subject_id)
    if not current_subject:
        # Invalid ID in DB? clear it and redirect
        current_user.current_subject_id = None
        db.session.commit()
        return redirect(url_for('main.my_subjects'))
    
    # Use the persistent ID for proper filtering
    subject_id = selected_subject_id
    
    # --- 1. Fetch Core Data (Subject Specific) ---
    subjects = Subject.query.all() # Keep for dropdown/modal
    all_topics = Topic.query.filter_by(subject_id=subject_id).order_by(Topic.order_index).all()
    progress_records = LearningProgress.query.filter_by(user_id=current_user.id).all()
    
    # Filter progress for strictly this subject
    subject_topic_ids = [t.id for t in all_topics]
    
    # Global Quiz Attempts vs Subject Specific?
    # For "Streak" we usually want GLOBAL activity (did I study *anything* today?)
    # For "Performance" we want SUBJECT specific.
    all_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.timestamp.desc()).all()
    quiz_attempts = [q for q in all_attempts if q.topic_id in subject_topic_ids]
    
    # --- 2. Calculate Subject Progress ---
    total_topics = len(all_topics)
    # Filter completed topics that belong to THIS subject
    completed_topics = sum(1 for p in progress_records if p.status == 'Completed' and p.topic_id in subject_topic_ids)
    overall_progress = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0
    
    # --- 3. Calculate Streak (Global) ---
    streak = 0
    if all_attempts:
        today = datetime.utcnow().date()
        unique_dates = sorted(list(set(q.timestamp.date() for q in all_attempts)), reverse=True)
        
        if unique_dates[0] == today or unique_dates[0] == today - timedelta(days=1):
            streak = 1
            current_date = unique_dates[0]
            for i in range(1, len(unique_dates)):
                if unique_dates[i] == current_date - timedelta(days=1):
                    streak += 1
                    current_date = unique_dates[i]
                else:
                    break
    
    # --- 4. Average Score & Strength Level ---
    avg_score = 0
    if quiz_attempts:
        avg_score = int(sum(q.score / q.max_score * 100 for q in quiz_attempts) / len(quiz_attempts))
    
    strength_level = "Beginner"
    if avg_score > 85: strength_level = "Expert"
    elif avg_score > 60: strength_level = "Intermediate"
    
    # --- 5. Personalized Learning Path (Timeline) ---
    # Create a list of topic states: locked, active, completed
    completed_topic_ids = {p.topic_id for p in progress_records if p.status == 'Completed'}
    
    timeline = []
    is_unlocked = True # First topic is always unlocked
    current_active_topic = None
    
    for topic in all_topics:
        status = 'locked'
        is_completed = topic.id in completed_topic_ids
        
        if is_completed:
            status = 'completed'
        elif is_unlocked:
            status = 'active'
            current_active_topic = topic
            is_unlocked = False # Lock subsequent topics until this one is done
        
        # Override strict locking for demo purposes if needed, but strict is better for gamification
        # Check if we should unlock the next one
        if is_completed:
            is_unlocked = True
            
        timeline.append({
            'topic': topic,
            'status': status,
            'difficulty': topic.difficulty
        })

    # --- 6. Analytics Data (for Charts) ---
    # Subject-wise accuracy (Global context is better for Radar Chart)
    subject_stats = {}
    for sub in subjects:
        sub_topics = [t.id for t in sub.topics]
        sub_attempts = [q for q in all_attempts if q.topic_id in sub_topics]
        if sub_attempts:
            acc = int(sum(q.score/q.max_score*100 for q in sub_attempts) / len(sub_attempts))
            subject_stats[sub.name] = acc
        else:
            subject_stats[sub.name] = 0
            
    # Weakest Areas (for Recommendations) - filtered by current subject
    # Filter topics with attempts but low scores
    weak_areas = []
    subject_progress = [p for p in progress_records if p.topic_id in subject_topic_ids]
    for p in subject_progress:
        if p.mastery_level < 50:
            topic = next((t for t in all_topics if t.id == p.topic_id), None)
            if topic:
                weak_areas.append(topic)
    
    smart_rec = []
    if current_active_topic:
        smart_rec.append({
            'title': f"Continue: {current_active_topic.title}",
            'desc': " It's up next in your path.",
            'action': 'Resume',
            'link': url_for('main.topic_view', topic_id=current_active_topic.id)
        })
    
    if weak_areas:
        t = weak_areas[0]
        smart_rec.append({
            'title': f"Revise: {t.title}",
            'desc': f"Your mastery is only {p.mastery_level}%.",
            'action': 'Practice',
            'link': url_for('main.quiz_view', topic_id=t.id)
        })


    # --- 7. Completion Logic ---
    show_completion = False
    recommended_subjects = []
    
    if overall_progress >= 100:
        show_completion = True
        # Simple Recommendation Map
        rec_map = {
            "Python": ["Data Structures & Algorithms", "Full Stack Web Development"],
            "Data Structures & Algorithms": ["Artificial Intelligence", "GATE CSE / IT"],
            "Artificial Intelligence": ["Python", "Data Structures & Algorithms"],
            "Aptitude": ["Logical Reasoning", "Polity"],
            "History": ["Polity", "Geography"]
        }
        
        target_names = rec_map.get(current_subject.name, [])
        if target_names:
            recommended_subjects = Subject.query.filter(Subject.name.in_(target_names)).all()
        else:
            # Fallback: Same Category
            recommended_subjects = Subject.query.filter(Subject.category == current_subject.category, Subject.id != current_subject.id).limit(2).all()

    return render_template('dashboard/index.html', 
                           user=current_user,
                           subjects=subjects, 
                           selected_subject=current_subject,
                           current_active_topic=current_active_topic,
                           stats={
                               'streak': streak,
                               'overall_progress': overall_progress,
                               'avg_score': avg_score,
                               'strength': strength_level,
                               'completed_count': completed_topics,
                               'total_count': total_topics,
                               'completed_topic_ids': completed_topic_ids
                           },
                           subject_stats=subject_stats,
                           recommendations=smart_rec,
                           current_date=datetime.utcnow(),
                           # For Focus Layout
                           current_subject=current_subject,
                           all_topics=all_topics,
                           # Completion
                           show_completion=show_completion,
                           recommended_subjects=recommended_subjects)

@main.route('/learning_path')
@login_required
def learning_path():
    from database.models import LearningProgress
    
    # Filter topics based on User's Selected Goal
    # If a specific subject is active, maybe show that? 
    # But usually Learning Path covers the whole Goal trajectory if not specific.
    # Let's prioritize: 1. Goal Category
    
    query = Topic.query.join(Subject).order_by(Topic.order_index)
    
    if current_user.selected_goal:
         query = query.filter(Subject.category == current_user.selected_goal)
         
    all_topics = query.all()
    progress_records = LearningProgress.query.filter_by(user_id=current_user.id).all()
    
    # Calculate Path Logic
    completed_topic_ids = {p.topic_id for p in progress_records if p.status == 'Completed'}
    
    timeline = []
    is_unlocked = True 
    
    for topic in all_topics:
        status = 'locked'
        is_completed = topic.id in completed_topic_ids
        
        if is_completed:
            status = 'completed'
        elif is_unlocked:
            status = 'active'
            is_unlocked = False 
        
        if is_completed:
            is_unlocked = True
            
        timeline.append({
            'topic': topic,
            'status': status,
            'difficulty': topic.difficulty
        })
        
    return render_template('dashboard/learning_path.html', timeline=timeline)

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
    from database.models import LearningProgress
    from flask import request
    
    topic = db.get_or_404(Topic, topic_id)
    subject = topic.subject
    
    # Get all topics for sidebar navigation
    all_topics = Topic.query.filter_by(subject_id=topic.subject_id).order_by(Topic.order_index).all()
    
    # Get user progress to determining level
    progress = LearningProgress.query.filter_by(user_id=current_user.id, topic_id=topic.id).first()
    prev_score = progress.mastery_level if progress else 0
    level = 'beginner'
    if prev_score > 40: level = 'intermediate'
    if prev_score > 70: level = 'advanced'

    context = {
        'topic': topic,
        'all_topics': all_topics,
        'is_structured': True, # Always true now with new engine
        'structured_data': {}
    }

    # Generate complete lesson module
    # We cache this in topic.content_payload if we want, or just generate live.
    # For "Dynamic Per Topic" request, we might want to generate fresh or check cache.
    # The prompt says "Generate content ONLY for selected topic".
    
    # Check if we have valid payload
    if topic.content_payload and not request.args.get('refresh'):
         context['structured_data'] = topic.content_payload
    else:
         # Generate New
         lesson_json = ai_engine.generate_lesson_module(
             subject=subject.name, 
             topic=topic.title, 
             user_level=level, 
             previous_score=prev_score
         )
         
         # Assuming lesson_json matches expected structure
         if lesson_json and 'topic_content' in lesson_json:
             # Map formatting if needed. Our template expects 'sections' list usually, 
             # but the new prompt returns raw HTML in 'topic_content'.
             # Let's adapt the template or wrap this.
             # The new prompt returns: { "topic_content": "<html>...</html>", "quiz": [...] }
             
             # We'll save the whole JSON
             topic.content_payload = lesson_json
             db.session.commit()
             context['structured_data'] = lesson_json
         else:
             # Fallback
             context['structured_data'] = {'topic_content': "<p>Error loading content.</p>"}

    # --- Layout Context Preparation ---
    current_subject = topic.subject
    
    # Calculate stats for the header progress bar
    progress_records = LearningProgress.query.filter_by(user_id=current_user.id).all()
    completed_topic_ids = {p.topic_id for p in progress_records if p.status == 'Completed'}
    
    subject_topics = Topic.query.filter_by(subject_id=topic.subject_id).all()
    subject_topic_ids = {t.id for t in subject_topics}
    
    completed_in_subject = len(completed_topic_ids.intersection(subject_topic_ids))
    total_in_subject = len(subject_topics)
    overall_progress = int((completed_in_subject / total_in_subject * 100)) if total_in_subject > 0 else 0
    
    stats = {
        'overall_progress': overall_progress,
        'completed_count': completed_in_subject,
        'total_count': total_in_subject,
        'completed_topic_ids': completed_topic_ids
    }

    return render_template('dashboard/topic.html', 
                           topic=topic, 
                           all_topics=all_topics, 
                           is_structured=context['is_structured'], 
                           structured_data=context['structured_data'],
                           # Layout Context
                           current_subject=current_subject,
                           current_active_topic=topic,
                           stats=stats)

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
    distribution = {'Easy': 3, 'Medium': 4, 'Hard': 3}
    
    if progress:
        cleared = progress.difficulty_cleared or {}
        # If struggling (last attempt low score? - we don't have last score handy easily here without query, assuming mastery_level proxies it)
        # Or simple check on cleared levels
        if cleared.get('Hard'):
            # Expert: Push for mastery
            distribution = {'Easy': 2, 'Medium': 3, 'Hard': 5}
        elif cleared.get('Medium'):
            # Intermediate: mix hard
            distribution = {'Easy': 2, 'Medium': 4, 'Hard': 4}
        elif cleared.get('Easy'):
            # Beginner passing easy
            distribution = {'Easy': 2, 'Medium': 5, 'Hard': 3}
        else:
            # Struggling or new
            distribution = {'Easy': 4, 'Medium': 4, 'Hard': 2}

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
    # Unlock next if: Global Score >= 70% (Strict User Rule)
    is_passed = score_percent >= 70
    
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

@main.route('/generator', methods=['GET', 'POST'])
@login_required
def generator():
    from ai_engine.generator import ai_engine
    
    generated_content = None
    topic_request = None
    
    if request.method == 'POST':
        topic_request = request.form.get('topic')
        level_request = request.form.get('level', 'beginner')
        
        if topic_request:
            # We reuse generate_lesson_module
            generated_content = ai_engine.generate_lesson_module(
                subject="General Learning", 
                topic=topic_request, 
                user_level=level_request, 
                previous_score=0
            )
            
    return render_template('dashboard/generator.html', 
                           generated_content=generated_content,
                           topic=topic_request)

@main.route('/my_subjects')
@login_required
def my_subjects():
    from database.models import Subject
    
    # Default: All subjects
    query = Subject.query
    
    # Filter by user's selected goal if set
    if current_user.selected_goal:
        query = query.filter_by(category=current_user.selected_goal)
        
    subjects = query.all()
    
    return render_template('dashboard/my_subjects.html', subjects=subjects, category=current_user.selected_goal)


@main.route('/analytics')
@login_required
def analytics():
    from sqlalchemy import func
    from collections import defaultdict
    
    # Fetch all attempts
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.timestamp.asc()).all()
    
    # 1. Summary Stats
    total_quizzes = len(attempts)
    avg_score = 0
    if total_quizzes > 0:
        avg_score = int(sum(a.score / a.max_score * 100 for a in attempts) / total_quizzes)

    # 2. Line Chart Data (Trend)
    trend_dates = [a.timestamp.strftime('%b %d') for a in attempts]
    trend_scores = [int(a.score / a.max_score * 100) for a in attempts]

    # 3. Bar Chart Data (Subject Accuracy)
    subject_map = defaultdict(list)
    for a in attempts:
        if a.topic and a.topic.subject:
            percent = (a.score / a.max_score) * 100
            subject_map[a.topic.subject.name].append(percent)
    
    subject_names = list(subject_map.keys())
    subject_scores = [int(sum(scores)/len(scores)) for scores in subject_map.values()]

    # 4. Radar Chart Data (Difficulty/Strength)
    # Using Topic difficulty as a proxy for now
    difficulty_map = {'Easy': [], 'Medium': [], 'Hard': []}
    for a in attempts:
        if a.topic:
            raw_diff = a.topic.difficulty
            diff = 'Medium'
            
            if raw_diff:
                if raw_diff in ['Easy', 'Beginner']:
                    diff = 'Easy'
                elif raw_diff in ['Hard', 'Advanced']:
                    diff = 'Hard'
                else:
                    diff = 'Medium'
            
            percent = (a.score / a.max_score) * 100
            difficulty_map[diff].append(percent)
    
    radar_labels = ['Easy', 'Medium', 'Hard']
    radar_data = []
    for d in radar_labels:
        scores = difficulty_map.get(d, [])
        radar_data.append(int(sum(scores)/len(scores)) if scores else 0)
        
    # Re-reverse attempts for the table view (newest first)
    recent_attempts = sorted(attempts, key=lambda x: x.timestamp, reverse=True)

    return render_template('dashboard/analytics.html', 
                           attempts=recent_attempts,
                           total_quizzes=total_quizzes, 
                           avg_score=avg_score,
                           trend_dates=trend_dates,
                           trend_scores=trend_scores,
                           subject_names=subject_names,
                           subject_scores=subject_scores,
                           radar_labels=radar_labels,
                           radar_data=radar_data)

@main.route('/bookmarks')
@login_required
def bookmarks():
    # Placeholder for now
    return render_template('dashboard/bookmarks.html')

