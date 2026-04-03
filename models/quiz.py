from database.database import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False) # List of strings ["Option A", "Option B", ...]
    correct_index = db.Column(db.Integer, nullable=False) # 0-indexed
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, default=100)
    time_taken = db.Column(db.Integer, nullable=True) # Seconds taken
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
