from models.subject import Subject, Topic
from models.user import User
from models.quiz import QuizAttempt
from models.progress import LearningProgress
from database.database import db
from datetime import datetime, timedelta

class DashboardService:
    @staticmethod
    def get_dashboard_data(user):
        from sqlalchemy import func
        
        # B. Retrieve Persisted Selection
        selected_subject_id = user.current_subject_id
            
        if not selected_subject_id:
            first_sub = Subject.query.filter_by(category=user.selected_goal).first() if user.selected_goal else Subject.query.first()
            if first_sub:
                user.current_subject_id = first_sub.id
                db.session.commit()
                selected_subject_id = first_sub.id
            else:
                return None, "Please select a subject to continue."
            
        current_subject = db.session.get(Subject, selected_subject_id)
        if not current_subject:
            user.current_subject_id = None
            db.session.commit()
            return None, "Invalid subject."

        # Fetch Core Data
        all_topics = Topic.query.filter_by(subject_id=selected_subject_id).order_by(Topic.order_index).all()
        progress_records = LearningProgress.query.filter_by(user_id=user.id).all()
        all_attempts = QuizAttempt.query.filter_by(user_id=user.id).order_by(QuizAttempt.timestamp.desc()).all()
        
        subject_topic_ids = [t.id for t in all_topics]
        quiz_attempts = [q for q in all_attempts if q.topic_id in subject_topic_ids]
        
        # Calculate Progress
        total_topics = len(all_topics)
        completed_topics = sum(1 for p in progress_records if p.status == 'Completed' and p.topic_id in subject_topic_ids)
        overall_progress = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0
        
        # Calculate Streak
        streak = DashboardService.calculate_streak(all_attempts)
        
        # Average Score
        avg_score = 0
        if quiz_attempts:
            avg_score = int(sum(q.score / q.max_score * 100 for q in quiz_attempts) / len(quiz_attempts))
        
        strength_level = "Beginner"
        if avg_score > 85: strength_level = "Expert"
        elif avg_score > 60: strength_level = "Intermediate"
        
        # Timeline
        completed_topic_ids = {p.topic_id for p in progress_records if p.status == 'Completed'}
        timeline, current_active_topic = DashboardService.generate_timeline(all_topics, completed_topic_ids)

        return {
            'current_subject': current_subject,
            'all_topics': all_topics,
            'current_active_topic': current_active_topic,
            'stats': {
                'streak': streak,
                'overall_progress': overall_progress,
                'avg_score': avg_score,
                'strength': strength_level,
                'completed_count': completed_topics,
                'total_count': total_topics,
                'completed_topic_ids': completed_topic_ids
            },
            'show_completion': overall_progress >= 100
        }, None

    @staticmethod
    def calculate_streak(all_attempts):
        if not all_attempts:
            return 0
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
            return streak
        return 0

    @staticmethod
    def generate_timeline(all_topics, completed_topic_ids):
        timeline = []
        is_unlocked = True 
        current_active_topic = None
        
        for topic in all_topics:
            status = 'locked'
            is_completed = topic.id in completed_topic_ids
            
            if is_completed:
                status = 'completed'
            elif is_unlocked:
                status = 'active'
                current_active_topic = topic
                is_unlocked = False 
            
            if is_completed:
                is_unlocked = True
                
            timeline.append({
                'topic': topic,
                'status': status,
                'difficulty': topic.difficulty
            })
        return timeline, current_active_topic
