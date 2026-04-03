from database.database import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) # 'login', 'study_lesson', 'take_quiz', 'ai_chat'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, nullable=True) # Duration in seconds if applicable
    metadata_json = db.Column(db.JSON, nullable=True) # Additional details (e.g., topic_id, score)

