from database.database import db
from datetime import datetime

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    status = db.Column(db.String(50), default='Not Started') # Not Started, In Progress, Completed
    mastery_level = db.Column(db.Integer, default=0) # 0-100
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    difficulty_cleared = db.Column(db.JSON, default={}) # e.g. {'easy': True, 'medium': False}

class MockTestProgress(db.Model):
    __tablename__ = 'mock_test_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    checkpoint_level = db.Column(db.Integer, nullable=False)
    is_passed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
