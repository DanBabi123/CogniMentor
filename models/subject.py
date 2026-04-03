from database.database import db

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
