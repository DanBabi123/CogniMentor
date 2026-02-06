from database.database import db
from database.models import Subject, Topic, User, LearningProgress, QuizAttempt

def seed_database():
    print("Seeding Database with Strict Curriculum...")
    
    # Define Subjects and their Topics (W3Schools Style Order)
    curriculum = {
        "Python": {
            "icon": "code",
            "category": "Technology",
            "topics": [
                "Python Intro", "Python Syntax", "Python Variables", "Python Data Types", 
                "Python Numbers", "Python Casting", "Python Strings", "Python Booleans",
                "Python Operators", "Python Lists", "Python Tuples", "Python Sets",
                "Python Dictionaries", "Python If...Else", "Python While Loops", "Python For Loops",
                "Python Functions", "Python Lambda", "Python Arrays", "Python Classes/Objects",
                "Python Inheritance", "Python Iterators", "Python Scope", "Python Modules",
                "Python Dates", "Python Math", "Python JSON", "Python PIP", "Python Try...Except"
            ]
        },
        "Data Structures & Algorithms": {
            "icon": "account_tree",
            "category": "Technology",
            "topics": [
                "DSA Intro", "Time Complexity", "Space Complexity", "Arrays", "Linked Lists",
                "Stacks", "Queues", "Hash Tables", "Recursion", "Linear Search", "Binary Search",
                "Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort",
                "Trees", "Binary Search Trees", "AVL Trees", "Graphs", "BFS & DFS",
                "Dijkstra's Algorithm", "Dynamic Programming Intro", "Greedy Algorithms"
            ]
        },
        "Full Stack Web Development": {
            "icon": "language",
            "category": "Technology",
            "topics": [
                "Web Dev Intro", "HTML Basics", "HTML Forms & Media", "CSS Basics",
                "CSS Flexbox & Grid", "Responsive Design", "JavaScript Basics",
                "JS DOM Manipulation", "JS ES6+ Features", "Async JavaScript",
                "React Intro", "React Components", "React Hooks", "State Management",
                "Node.js Basics", "Express.js", "MongoDB Intro", "RESTful APIs",
                "Authentication (JWT)", "Deployment"
            ]
        },
        "Artificial Intelligence": {
            "icon": "smart_toy",
            "category": "Technology",
            "topics": [
                "AI Intro", "Intelligent Agents", "Problem Solving & Search",
                "Heuristic Search (A*)", "Adversarial Search (Minimax)",
                "Knowledge Representation", "Machine Learning Intro",
                "Supervised Learning", "Unsupervised Learning", "Reinforcement Learning",
                "Linear Regression", "Logistic Regression", "Decision Trees",
                "Neural Networks Intro", "Deep Learning Overview", "NLP Basics"
            ]
        },
        "GATE CSE / IT": {
            "icon": "school",
            "category": "GATE",
            "topics": [
                "Propositional Logic", "First Order Logic", "Graph Theory", "Set Theory",
                "Combinatorics", "Linear Algebra", "Calculus", "Probability",
                "Digital Logic", "Computer Organization", "Programming & Data Structures",
                "Algorithms", "Theory of Computation", "Compiler Design",
                "Operating Systems", "Databases", "Computer Networks"
            ]
        },
        "Aptitude": {
            "icon": "psychology",
            "category": "Government Exams",
            "topics": [
                "Number System", "HCF & LCM", "Averages", "Percentages",
                "Profit & Loss", "Simple Interest", "Compound Interest",
                "Ratio & Proportion", "Time & Work", "Time, Speed & Distance",
                "Permutations & Combinations", "Probability"
            ]
        },
        "Logical Reasoning": {
            "icon": "lightbulb",
            "category": "Government Exams",
            "topics": [
                "Coding-Decoding", "Blood Relations", "Direction Sense",
                "Seating Arrangement", "Syllogism", "Clocks & Calendars",
                "Venn Diagrams", "Analogy", "Classification"
            ]
        },
        "History": {
            "icon": "history_edu",
            "category": "Government Exams",
            "topics": ["Ancient India", "Medieval India", "Modern India", "World History", "Art & Culture", "Freedom Struggle"]
        },
        "Polity": {
            "icon": "gavel",
            "category": "Government Exams",
            "topics": ["Constitution Intro", "Preamble", "Fundamental Rights", "Directive Principles", "Parliament", "President", "Judiciary", "State Govt", "Panchayati Raj"]
        },
        "Geography": {
            "icon": "public",
            "category": "Government Exams",
            "topics": ["Physical Geography", "Indian Geography", "World Geography", "Climate & Weather", "Natural Resources", "Agriculture", "Transport"]
        }
    }

    for sub_name, data in curriculum.items():
        subject = Subject.query.filter_by(name=sub_name).first()
        if not subject:
            subject = Subject(name=sub_name, icon=data['icon'], category=data.get('category', 'Technology'))
            db.session.add(subject)
            db.session.commit()
            print(f"Created Subject: {sub_name} ({subject.category})")
        else:
            # Update category if exists
            subject.category = data.get('category', 'Technology')
            db.session.commit()
        
        # Add Topics
        for idx, topic_title in enumerate(data['topics']):
            topic = Topic.query.filter_by(subject_id=subject.id, title=topic_title).first()
            if not topic:
                topic = Topic(
                    subject_id=subject.id,
                    title=topic_title,
                    order_index=idx,
                    difficulty='Beginner' if idx < 5 else 'Medium' if idx < 15 else 'Advanced'
                )
                db.session.add(topic)
                print(f"  - Added Topic: {topic_title}")
            else:
                topic.order_index = idx
        
        db.session.commit()

    # Ensure Admin User Exists
    admin_email = 'admin@cogni.com'
    admin_user = User.query.filter_by(email=admin_email).first()
    if not admin_user:
        admin_user = User(
            name='System Admin',
            email=admin_email,
            role='admin',
            is_verified=True,
            is_first_login=False # Admins skip goal selection
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        print(f"Created Admin User: {admin_email}")
    
    db.session.commit()
    print("Database Seeding Complete!")
