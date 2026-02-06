from .database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True) # Nullable for OAuth users
    oauth_provider = db.Column(db.String(50), nullable=True) # google, facebook, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(150), nullable=True, default='default.jpg')
    role = db.Column(db.String(20), default='student') # student, admin
    selected_goal = db.Column(db.String(50), nullable=True) # Technology, Govt, GATE
    
    # Security / OTP fields
    is_verified = db.Column(db.Boolean, default=False)
    is_first_login = db.Column(db.Boolean, default=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    progress = db.relationship('LearningProgress', backref='user', lazy=True)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    
    # Track current focus subject
    current_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    current_subject = db.relationship('Subject', foreign_keys=[current_subject_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='school') # Material Icon Name
    category = db.Column(db.String(50), default='Technology') # Technology, Government, GATE
    
    # Relationships
    topics = db.relationship('Topic', backref='subject', lazy=True)

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    difficulty = db.Column(db.String(50), default='Beginner') 
    slug = db.Column(db.String(200), nullable=True)
    order_index = db.Column(db.Integer, default=0)
    
    # Structured Content for "W3Schools" style pages
    # Stores JSON: { "objectives": [], "sections": [ { "heading": "", "content": "", "code": "" } ] }
    content_payload = db.Column(db.JSON, nullable=True) 
    
    # Relationships
    attempts = db.relationship('QuizAttempt', backref='topic', lazy=True)
    questions = db.relationship('Question', backref='topic', lazy=True)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False) # List of strings ["Option A", "Option B", ...]
    correct_index = db.Column(db.Integer, nullable=False) # 0-indexed
    explanation = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='Medium') # Easy, Medium, Hard

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    status = db.Column(db.String(50), default='Not Started') # Not Started, In Progress, Completed
    mastery_level = db.Column(db.Integer, default=0) # 0-100
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    difficulty_cleared = db.Column(db.JSON, default={}) # e.g. {'easy': True, 'medium': False}

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, default=100)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
