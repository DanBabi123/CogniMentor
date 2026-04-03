from database.database import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(150), nullable=True, default='default.jpg')
    role = db.Column(db.String(20), default='student') # student, admin
    selected_goal = db.Column(db.String(50), nullable=True) # Technology, Govt, GATE
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.String(500), nullable=True)
    
    # Tracking / Gamification
    total_xp = db.Column(db.Integer, default=0)
    streak_count = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, nullable=True)
    total_learning_time = db.Column(db.Integer, default=0) # Total minutes spent learning
    
    # Security / OTP fields
    is_verified = db.Column(db.Boolean, default=False)
    is_first_login = db.Column(db.Boolean, default=True)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade="all, delete-orphan")
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True, cascade="all, delete-orphan")
    activities = db.relationship('ActivityLog', backref='user_ref', lazy=True, cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='receiver', lazy=True, cascade="all, delete-orphan")
    earned_badges = db.relationship('UserBadge', backref='owner', lazy=True, cascade="all, delete-orphan")
    password_resets = db.relationship('PasswordReset', backref='user_account', lazy=True, cascade="all, delete-orphan")
    
    # Track current focus subject
    current_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    current_subject = db.relationship('Subject', foreign_keys=[current_subject_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
