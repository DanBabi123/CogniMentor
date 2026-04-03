from flask import render_template, abort, redirect, url_for, request, session, flash
from flask_login import login_required, current_user
from database.database import db
from models import Subject, Topic, QuizAttempt, Question, User, LearningProgress
from services.dashboard_service import DashboardService
from services.progress_service import ProgressService
from services.quiz_service import QuizService
from services.ai_service import AIService
from services.gamification_service import GamificationService
from datetime import datetime
import random
from . import main

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
    valid_categories = ['Technology', 'Government Exams', 'GATE', 'Data Science', 'Higher Studies', 'Startup']
    if category not in valid_categories:
        flash('Invalid Goal Selected', 'error')
        return redirect(url_for('main.goal_selection'))
        
    current_user.selected_goal = category
    db.session.commit()
    return redirect(url_for('main.subject_selection', category=category))

@main.route('/goals')
@login_required
def goal_selection():
    subjects = Subject.query.all()
    return render_template('dashboard/goal_selection.html', subjects=subjects)

@main.route('/generate_custom_roadmap', methods=['POST'])
@login_required
def generate_custom_roadmap():
    user_goal = request.form.get('user_goal')
    if not user_goal:
        flash('Please enter a learning goal', 'error')
        return redirect(url_for('main.goal_selection'))
    
    # Generate roadmap using AI
    roadmap = AIService.generate_custom_roadmap(user_goal)
    
    # Create a new Subject for the custom roadmap
    custom_subject = Subject(
        name=f"Custom: {user_goal}",
        description=f"A personalized learning path for {user_goal}, architected by AI.",
        category=f"Custom: {current_user.name}",
        icon="psychology"
    )
    db.session.add(custom_subject)
    db.session.flush() # Get ID
    
    # Create Topics from the roadmap
    for i, item in enumerate(roadmap):
        new_topic = Topic(
            subject_id=custom_subject.id,
            title=item.get('title', f'Module {i+1}'),
            difficulty=item.get('difficulty', 'Beginner'),
            order_index=i + 1
        )
        db.session.add(new_topic)
    
    # Set as current subject
    current_user.current_subject_id = custom_subject.id
    current_user.selected_goal = "Technology" # Default category for custom subjects
    db.session.commit()
    
    flash(f'AI has architected your custom roadmap for "{user_goal}"!', 'success')
    return redirect(url_for('main.dashboard'))

@main.route('/subjects')
@login_required
def subject_selection():
    category = request.args.get('category')
    if category:
        subjects = Subject.query.filter_by(category=category).all()
        header_title = f"{category}"
        subtitle = "Select your specific field of study"
    else:
        subjects = Subject.query.all()
        header_title = "All Subjects"
        subtitle = "Choose a subject to start learning"
        
    return render_template('dashboard/my_subjects.html', subjects=subjects, title=header_title, subtitle=subtitle)

@main.route('/contact', methods=['GET', 'POST'])
def contact(): 
    if request.method == 'POST':
        flash('Your message has been sent to our support team!', 'success')
        return redirect(url_for('main.contact'))
    return render_template('simple_pages/contact.html')

@main.route('/privacy')
def privacy(): return render_template('simple_pages/privacy.html')

@main.route('/terms')
def terms(): return render_template('simple_pages/terms.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    subject_id = request.args.get('subject_id', type=int)
    if subject_id:
        current_user.current_subject_id = subject_id
        if current_user.is_first_login:
            current_user.is_first_login = False
        db.session.commit()
    
    data, error = DashboardService.get_dashboard_data(current_user)
    if error:
        flash(error, "info")
        return redirect(url_for('main.my_subjects'))
    
    # Analytics & Recommendations (Still in route for now, or move to DashboardService)
    subjects = Subject.query.all()
    if current_user.selected_goal:
        subjects = [s for s in subjects if s.category == current_user.selected_goal]
    
    subject_stats = {}
    all_attempts = QuizAttempt.query.filter_by(user_id=current_user.id).all()
    for sub in subjects:
        sub_topics = [t.id for t in sub.topics]
        sub_attempts = [q for q in all_attempts if q.topic_id in sub_topics]
        subject_stats[sub.name] = int(sum(q.score/q.max_score*100 for q in sub_attempts)/len(sub_attempts)) if sub_attempts else 0
            
    recommendations = []
    if data['current_active_topic']:
        recommendations.append({
            'title': f"Continue: {data['current_active_topic'].title}",
            'desc': " It's up next in your path.",
            'action': 'Resume',
            'link': url_for('main.topic_view', topic_id=data['current_active_topic'].id)
        })

    recommended_subjects = []
    if data['show_completion']:
        recommended_subjects = Subject.query.filter(Subject.category == data['current_subject'].category, Subject.id != data['current_subject'].id).limit(2).all()

    # Advanced Cross-Skill & Performance Recommendation Engine (USP)
    CROSS_SKILL_MAP = {
        'Python': ['Data Structures & Algorithms', 'Pandas & NumPy', 'Machine Learning'],
        'Full Stack Web Development': ['SQL', 'Digital Marketing', 'Startup Fundamentals'],
        'Java': ['Data Structures & Algorithms', 'System Design', 'Operating Systems'],
        'Machine Learning': ['Deep Learning & NLP', 'Mathematics', 'Logical Reasoning'],
        'Business Fundamentals': ['Digital Marketing', 'Product Management', 'Aptitude'],
        'Aptitude': ['Logical Reasoning', 'GATE CSE / IT', 'Data Analytics']
    }

    # 1. Performance Analysis
    avg_score = 0
    if all_attempts:
        avg_score = sum(q.score/q.max_score for q in all_attempts) / len(all_attempts) * 100

    # 2. Derive smart recommendation
    current_sub_name = data['current_subject'].name if data.get('current_subject') else None
    reason = "Broaden your expertise with a new domain."
    suggested_sub = None

    if avg_score < 50 and all_attempts:
        # Struggling -> Suggest foundation
        suggested_sub = Subject.query.filter(Subject.name.in_(['Logical Reasoning', 'Aptitude'])).filter(Subject.id != (data['current_subject'].id if data.get('current_subject') else 0)).first()
        reason = "We noticed your recent scores are low. Strengthening your logic will help you master complex topics."
    elif current_sub_name in CROSS_SKILL_MAP:
        # Excelling or Normal -> Suggest natural neighbor
        neighbors = CROSS_SKILL_MAP[current_sub_name]
        suggested_sub = Subject.query.filter(Subject.name.in_(neighbors)).filter(Subject.id != data['current_subject'].id).first()
        if suggested_sub:
            reason = f"Based on your interest in {current_sub_name}, this is the perfect next step for your career path."
    
    # Fallback to general cross-skill if none found
    if not suggested_sub:
        suggested_sub = Subject.query.filter(Subject.category != (data['current_subject'].category if data.get('current_subject') else 'None')).first()
        reason = "Expand your skill set by exploring a completely different field of study."

    if suggested_sub:
        recommendations.append({
            'title': f"Smart Suggesion: {suggested_sub.name}",
            'desc': suggested_sub.description[:60] + "..." if suggested_sub.description else "Explore new concepts.",
            'reason': reason,
            'link': url_for('main.subject_view', subject_id=suggested_sub.id),
            'icon': suggested_sub.icon if hasattr(suggested_sub, 'icon') else 'auto_awesome'
        })
        
    # Additional Context for the Dashboard
    recent_activity = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.timestamp.desc()).limit(5).all()
    completed_ids = data['stats']['completed_topic_ids']
    upcoming_tasks = [t for t in data['all_topics'] if t.id not in completed_ids][:3]
    subject_progress = {}
    for sub in subjects:
        total = len(sub.topics)
        done = sum(1 for t in sub.topics if t.id in completed_ids)
        subject_progress[sub.name] = int((done/total)*100) if total else 0

    # Intelligent Next-Action Engine
    next_action = None
    if data.get('current_subject'):
        from models.progress import MockTestProgress
        mock_progress = MockTestProgress.query.filter_by(user_id=current_user.id, subject_id=data['current_subject'].id).all()
        completed_mocks = [m.checkpoint_level for m in mock_progress if m.is_passed]
        
        all_topics = sorted(data['current_subject'].topics, key=lambda t: t.order_index)
        
        for index, topic in enumerate(all_topics):
            if index > 0 and index % 5 == 0:
                cp_level = index // 5
                if cp_level not in completed_mocks:
                    next_action = {
                        'type': 'mock_test',
                        'title': f"Checkpoint {cp_level} Exam",
                        'reason': f"You've crushed {cp_level * 5} straight modules! Validate your retention before advancing.",
                        'url': url_for('main.mock_test_view', subject_id=data['current_subject'].id, level=cp_level),
                        'icon': 'military_tech'
                    }
                    break
            
            is_completed = topic.id in completed_ids
            if not is_completed:
                reason = "Let's learn something new today!"
                if index > 0:
                    reason = f"You successfully completed '{all_topics[index-1].title}'. This is the logical next step."
                next_action = {
                    'type': 'topic',
                    'title': topic.title,
                    'reason': reason,
                    'url': url_for('main.topic_view', topic_id=topic.id),
                    'icon': 'play_circle_filled'
                }
                break

        if not next_action:
            next_action = {
                'type': 'finished',
                'title': "Course Completed!",
                'reason': "Incredible work. You have mastered every single topic in this course.",
                'url': url_for('main.my_subjects'),
                'icon': 'workspace_premium'
            }

    return render_template('dashboard/index.html', 
                           user=current_user,
                           subjects=subjects, 
                           selected_subject=data['current_subject'],
                           current_active_topic=data['current_active_topic'],
                           stats=data['stats'],
                           subject_stats=subject_stats,
                           subject_progress=subject_progress,
                           recommendations=recommendations,
                           current_date=datetime.utcnow(),
                           current_subject=data['current_subject'],
                           all_topics=data['all_topics'],
                           show_completion=data['show_completion'],
                           recommended_subjects=recommended_subjects,
                           recent_activity=recent_activity,
                           upcoming_tasks=upcoming_tasks,
                           next_action=next_action)

@main.route('/continue')
@login_required
def continue_learning():
    if not current_user.current_subject_id:
        flash("Please select a valid subject to continue learning.", "info")
        return redirect(url_for('main.my_subjects'))

    subject_topics = Topic.query.filter_by(subject_id=current_user.current_subject_id).order_by(Topic.order_index).all()
    if not subject_topics:
        flash("This subject currently has no content. Check back later!", "info")
        return redirect(url_for('main.dashboard'))

    completed_topic_ids = {p.topic_id for p in LearningProgress.query.filter_by(user_id=current_user.id).all() if p.status == 'Completed'}
    
    # Chronological scan for first uncompleted topic
    for topic in subject_topics:
        if topic.id not in completed_topic_ids:
            return redirect(url_for('main.topic_view', topic_id=topic.id))
            
    # Fallback if entire course is naturally completed
    flash("Incredible! You have officially completed every single topic in this course.", "success")
    return redirect(url_for('main.dashboard'))

from models.progress import MockTestProgress

@main.route('/subject/<int:subject_id>')
@login_required
def subject_view(subject_id):
    subject = db.get_or_404(Subject, subject_id)
    topics = sorted(subject.topics, key=lambda t: t.order_index)
    progress_map = {p.topic_id: p for p in LearningProgress.query.filter_by(user_id=current_user.id).all()}
    
    mock_progress = MockTestProgress.query.filter_by(user_id=current_user.id, subject_id=subject.id).all()
    completed_mocks = [m.checkpoint_level for m in mock_progress if m.is_passed]
    
    topic_status = []
    is_prev_completed = True
    for index, topic in enumerate(topics):
        if index > 0 and index % 5 == 0:
            if (index // 5) not in completed_mocks:
                is_prev_completed = False
                
        is_completed = topic.id in progress_map and progress_map[topic.id].status == 'Completed'
        topic_status.append({'topic': topic, 'is_locked': not is_prev_completed, 'is_completed': is_completed})
        is_prev_completed = is_completed

    return render_template('dashboard/subject.html', subject=subject, topic_status=topic_status, completed_mocks=completed_mocks)

@main.route('/topic/<int:topic_id>')
@login_required
def topic_view(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    progress = LearningProgress.query.filter_by(user_id=current_user.id, topic_id=topic.id).first()
    prev_score = progress.mastery_level if progress else 0
    level = 'beginner'
    if prev_score > 40: level = 'intermediate'
    if prev_score > 70: level = 'advanced'

    if not topic.content_payload or request.args.get('refresh'):
         topic.content_payload = AIService.generate_lesson(topic.subject.name, topic.title, level, prev_score)
         db.session.commit()

    # Layout Context
    subject_topics = sorted(Topic.query.filter_by(subject_id=topic.subject_id).all(), key=lambda t: t.order_index)
    completed_topic_ids = {p.topic_id for p in LearningProgress.query.filter_by(user_id=current_user.id).all() if p.status == 'Completed'}
    
    mock_progress = MockTestProgress.query.filter_by(user_id=current_user.id, subject_id=topic.subject_id).all()
    completed_mocks = [m.checkpoint_level for m in mock_progress if m.is_passed]
    
    topic_status = []
    is_prev_completed = True
    for index, t in enumerate(subject_topics):
        if index > 0 and index % 5 == 0:
            if (index // 5) not in completed_mocks:
                is_prev_completed = False
                
        is_completed = t.id in completed_topic_ids
        topic_status.append({'topic': t, 'is_locked': not is_prev_completed, 'is_completed': is_completed})
        is_prev_completed = is_completed
    
    completed_in_subject = len(completed_topic_ids.intersection({t.id for t in subject_topics}))
    overall_progress = int((completed_in_subject / len(subject_topics) * 100)) if subject_topics else 0
    
    return render_template('dashboard/topic.html', 
                           topic=topic, 
                           topic_status=topic_status,
                           completed_mocks=completed_mocks,
                           is_structured=True, 
                           structured_data=topic.content_payload,
                           current_subject=topic.subject,
                           current_active_topic=topic,
                           stats={'overall_progress': overall_progress, 'completed_count': completed_in_subject, 'total_count': len(subject_topics), 'completed_topic_ids': completed_topic_ids})

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        if 'profile_pic' in request.files:
            import os
            from werkzeug.utils import secure_filename
            from flask import current_app
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                new_filename = f"user_{current_user.id}.{filename.rsplit('.', 1)[1].lower()}"
                upload_folder = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, new_filename))
                current_user.profile_pic = new_filename
                db.session.commit()
                flash('Profile picture updated!', 'success')
        
        if 'name' in request.form:
             current_user.name = request.form['name']
             current_user.phone = request.form.get('phone')
             current_user.address = request.form.get('address')
             current_user.bio = request.form.get('bio')
             db.session.commit()
             flash('Profile details updated.', 'success')
        return redirect(url_for('main.profile'))
    return render_template('dashboard/profile.html')

@main.route('/quiz/<int:topic_id>')
@login_required
def quiz_view(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    questions = QuizService.generate_quiz_for_topic(current_user.id, topic_id)
    session['quiz_answers'] = {str(q.get('id', i)): {'correct': q.get('correct', 0), 'difficulty': q.get('difficulty', 'Medium')} for i, q in enumerate(questions)}
    return render_template('dashboard/quiz.html', topic=topic, questions=questions)

@main.route('/quiz/<int:topic_id>/submit', methods=['POST'])
@login_required
def quiz_submit(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    time_taken = request.form.get('time_taken', type=int)
    result = QuizService.process_quiz_submission(current_user.id, topic_id, request.form, session.get('quiz_answers', {}), time_taken=time_taken)
    subject_topics = Topic.query.filter_by(subject_id=topic.subject_id).order_by(Topic.order_index).all()
    next_topic = None
    for i, t in enumerate(subject_topics):
        if t.id == topic.id and i + 1 < len(subject_topics):
            next_topic = subject_topics[i+1]
            break

    return render_template('dashboard/result.html', 
                           attempt=result['attempt'], 
                           feedback=result['feedback'], 
                           score_percent=result['score_percent'], 
                           report=result['report'],
                           strength_level="Strong" if result['score_percent'] > 80 else "Average",
                           is_passed=result['is_passed'],
                           diff_stats=result['diff_stats'],
                           xp_earned=result['xp_earned'],
                           next_topic=next_topic)

@main.route('/mock_test/<int:subject_id>/<int:level>')
@login_required
def mock_test_view(subject_id, level):
    subject = db.get_or_404(Subject, subject_id)
    questions, topics = QuizService.generate_mock_test(subject_id, level)
    session['mock_answers'] = {str(q.get('id', i)): {'correct': q.get('correct', 0), 'difficulty': q.get('difficulty', 'Medium')} for i, q in enumerate(questions)}
    dummy_topic = type('Dummy', (object,), {'title': f"Checkpoint {level} Exam", 'subject': subject})()
    return render_template('dashboard/quiz.html', topic=dummy_topic, questions=questions, is_mock=True, level=level, subject=subject)

@main.route('/mock_test/<int:subject_id>/<int:level>/submit', methods=['POST'])
@login_required
def mock_test_submit(subject_id, level):
    subject = db.get_or_404(Subject, subject_id)
    time_taken = request.form.get('time_taken', type=int)
    result = QuizService.process_mock_submission(current_user.id, subject_id, level, request.form, session.get('mock_answers', {}), time_taken=time_taken)
    
    subject_topics = sorted(subject.topics, key=lambda t: t.order_index)
    next_topic_idx = level * 5
    next_topic = subject_topics[next_topic_idx] if next_topic_idx < len(subject_topics) else None
    
    dummy_attempt = type('Dummy', (object,), {'score': int((result['score_percent']*10)/100), 'max_score': 10, 'topic_id': None})()
    
    return render_template('dashboard/result.html', 
                           attempt=dummy_attempt, 
                           feedback=result['feedback'], 
                           score_percent=result['score_percent'], 
                           report=result['report'],
                           strength_level="Strong" if result['score_percent'] > 80 else "Average",
                           is_passed=result['is_passed'],
                           diff_stats=result['diff_stats'],
                           xp_earned=result['xp_earned'],
                           next_topic=next_topic,
                           is_mock=True,
                           subject=subject,
                           level=level)

@main.route('/topic/<int:topic_id>/record_time', methods=['POST'])
@login_required
def record_study_time(topic_id):
    duration = request.json.get('duration', 0)
    if duration > 5: # Only record if more than 5 seconds spent
        ProgressService.track_study_session(current_user.id, topic_id, duration)
    return {'status': 'success'}

@main.route('/my_subjects')
@login_required
def my_subjects():
    query = Subject.query
    if current_user.selected_goal:
        query = query.filter_by(category=current_user.selected_goal)
    return render_template('dashboard/my_subjects.html', subjects=query.all(), category=current_user.selected_goal)

@main.route('/analytics')
@login_required
def analytics():
    from services.analytics_service import AnalyticsService
    data = AnalyticsService.get_deep_analytics(current_user.id)
    
    return render_template('dashboard/analytics.html', 
                           total_quizzes=data['total_quizzes'], 
                           avg_score=data['avg_score'],
                           accuracy_rate=data['accuracy_rate'],
                           total_minutes=data['total_minutes'],
                           focus_score=data['focus_score'],
                           peak_time=data['peak_time'],
                           trend_dates=data['weekly_trend_labels'],
                           trend_scores=data['weekly_trend_data'],
                           subject_performance=data['subject_performance'],
                           behavioral_insights=data['behavioral_insights'],
                           attempts=data['attempts'])

@main.route('/leaderboard')
@login_required
def leaderboard():
    top_users = GamificationService.get_leaderboard()
    user_rank = GamificationService.get_user_rank(current_user.id)
    return render_template('dashboard/leaderboard.html', 
                            top_users=top_users, 
                            user_rank=user_rank)

@main.route('/notifications')
@login_required
def notifications():
    from services.notification_service import NotificationService
    all_notifications = NotificationService.get_unread_notifications(current_user.id)
    # We display all unread, and maybe some recent read
    from models.notification import Notification
    recent_read = Notification.query.filter_by(user_id=current_user.id, is_read=True).order_by(Notification.created_at.desc()).limit(10).all()
    return render_template('dashboard/notifications.html', unread=all_notifications, read=recent_read)

@main.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_read():
    from services.notification_service import NotificationService
    NotificationService.mark_all_as_read(current_user.id)
    return redirect(url_for('main.notifications'))

