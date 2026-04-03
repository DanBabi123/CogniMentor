from models.progress import LearningProgress
from models.subject import Topic, Subject
from models.activity import ActivityLog
from models.user import User
from database.database import db
from datetime import datetime

class ProgressService:
    @staticmethod
    def get_learning_path(user):
        query = Topic.query.join(Subject).order_by(Topic.order_index)
        if user.selected_goal:
             query = query.filter(Subject.category == user.selected_goal)
             
        all_topics = query.all()
        progress_records = LearningProgress.query.filter_by(user_id=user.id).all()
        
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
        return timeline

    @staticmethod
    def update_topic_progress(user_id, topic_id, score_percent):
        progress = LearningProgress.query.filter_by(user_id=user_id, topic_id=topic_id).first()
        if not progress:
            progress = LearningProgress(user_id=user_id, topic_id=topic_id)
            db.session.add(progress)
        
        progress.last_accessed = datetime.utcnow()
        new_mastery = int(score_percent)
        
        # Award XP for improvement in mastery
        xp_to_award = 0
        if new_mastery > (progress.mastery_level or 0):
            xp_to_award = (new_mastery - (progress.mastery_level or 0)) // 2
            progress.mastery_level = new_mastery
            
        # Status update
        if score_percent >= 60:
            if progress.status != 'Completed':
                xp_to_award += 100 # First time completion bonus
            progress.status = 'Completed'
        elif progress.status != 'Completed':
            progress.status = 'In Progress'
            
        if xp_to_award > 0:
            user = db.session.get(User, user_id)
            if user:
                user.total_xp += xp_to_award
                
        return progress

    @staticmethod
    def track_study_session(user_id, topic_id, duration_seconds):
        user = db.session.get(User, user_id)
        if user:
            duration_minutes = duration_seconds // 60
            user.total_learning_time += duration_minutes
            
            # Award passive XP for studying (1 XP per minute)
            user.total_xp += duration_minutes
            
            # Log Activity
            log = ActivityLog(
                user_id=user_id,
                activity_type='study_lesson',
                duration=duration_seconds,
                metadata_json={'topic_id': topic_id}
            )
            db.session.add(log)
            db.session.commit()
            return True
        return False
