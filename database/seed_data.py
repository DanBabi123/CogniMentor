from database.database import db
from models import Subject, Topic, User, LearningProgress, QuizAttempt, Badge

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
        "Java": {
            "icon": "coffee",
            "category": "Technology",
            "topics": [
                "Java Intro", "Java Syntax", "Java Variables", "Java Data Types",
                "Java Type Casting", "Java Operators", "Java Strings", "Java Math",
                "Java Booleans", "Java If...Else", "Java Switch", "Java While Loop",
                "Java For Loop", "Java Break/Continue", "Java Arrays", "Java Methods",
                "Java OOP Basics", "Java Classes/Objects", "Java Class Attributes", "Java Class Methods",
                "Java Constructors", "Java Modifiers", "Java Encapsulation", "Java Packages/API",
                "Java Inheritance", "Java Polymorphism", "Java Inner Classes", "Java Abstraction",
                "Java Interfaces", "Java Enums", "Java User Input", "Java Dates",
                "Java ArrayList", "Java LinkedList", "Java HashMap", "Java HashSet",
                "Java Iterator", "Java Wrapper Classes", "Java Exceptions", "Java RegEx",
                "Java Threads", "Java Lambda", "Java File Handling"
            ]
        },
        "C": {
            "icon": "terminal",
            "category": "Technology",
            "topics": [
                "C Intro", "C Syntax", "C Output", "C Comments", "C Variables",
                "C Data Types", "C Constants", "C Operators", "C Booleans",
                "C If...Else", "C Switch", "C While Loop", "C For Loop",
                "C Break/Continue", "C Arrays", "C Strings", "C User Input",
                "C Memory Address", "C Pointers", "C Functions", "C Function Parameters",
                "C Math", "C Files", "C Structures", "C Enums", "C Memory Management"
            ]
        },
        "SQL": {
            "icon": "storage",
            "category": "Technology",
            "topics": [
                "SQL Intro", "SQL Syntax", "SQL Select", "SQL Select Distinct",
                "SQL Where", "SQL And, Or, Not", "SQL Order By", "SQL Insert Into",
                "SQL Null Values", "SQL Update", "SQL Delete", "SQL Select Top",
                "SQL Min & Max", "SQL Count, Avg, Sum", "SQL Like", "SQL Wildcards",
                "SQL In", "SQL Between", "SQL Aliases", "SQL Joins", "SQL Inner Join",
                "SQL Left Join", "SQL Right Join", "SQL Full Join", "SQL Self Join",
                "SQL Union", "SQL Group By", "SQL Having", "SQL Exists", "SQL Any, All",
                "SQL Select Into", "SQL Insert Into Select", "SQL Case", "SQL Null Functions",
                "SQL Stored Procedures", "SQL Comments", "SQL Operators"
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

        "GATE CSE / IT": {
            "icon": "school",
            "category": "GATE",
            "topics": [
                "Propositional Logic", "First Order Logic", "Graph Theory", "Set Theory",
                "Combinatorics", "Linear Algebra", "Calculus", "Probability",
                "Digital Logic", "Computer Organization", "Programming & Data Structures",
                "Algorithms", "Theory of Computation", "Compiler Design"
            ]
        },
        "Operating Systems": {
            "icon": "settings_suggest",
            "category": "GATE",
            "topics": [
                "OS Intro & Types", "Process Management", "CPU Scheduling Algorithms",
                "Process Synchronization", "Deadlocks", "Memory Management",
                "Virtual Memory & Paging", "File Systems", "Disk Scheduling",
                "System Calls & Protection"
            ]
        },
        "Computer Networks": {
            "icon": "lan",
            "category": "GATE",
            "topics": [
                "Networking Intro", "OSI vs TCP/IP Models", "Physical Layer Basics",
                "Data Link Layer & Framing", "Error & Flow Control", "Medium Access Control",
                "IP Addressing & Subnetting", "Routing Algorithms", "TCP & UDP Protocols",
                "Application Layer (HTTP/DNS/SMTP)", "Network Security"
            ]
        },
        "Database Management Systems": {
            "icon": "database",
            "category": "GATE",
            "topics": [
                "DBMS Architecture", "ER Model to Relational Mapping", "Relational Algebra",
                "SQL: Queries & Joins", "Normalization (1NF, 2NF, 3NF, BCNF)",
                "Transaction Management (ACID)", "Concurrency Control",
                "Indexing & B-Trees", "NoSQL vs SQL Overview"
            ]
        },
        "Object Oriented Programming": {
            "icon": "category",
            "category": "GATE",
            "topics": [
                "OOP Principles Intro", "Classes & Objects", "Encapsulation & Data Hiding",
                "Inheritance & Types", "Polymorphism (Static & Dynamic)",
                "Abstraction & Interfaces", "Constructors & Destructors",
                "Exception Handling", "OOP in C++ vs Java", "Design Patterns Basics"
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
        },
        "R Programming": {
            "icon": "calculate",
            "category": "Data Science",
            "topics": [
                "R Intro", "R Syntax", "R Variables", "R Data Types", 
                "R Vectors", "R Lists", "R Matrices", "R Data Frames", 
                "R Factors", "R dplyr Basics", "R Data Cleaning", 
                "R ggplot2 Visualization", "R Statistical Modules"
            ]
        },
        "TensorFlow & PyTorch": {
            "icon": "memory",
            "category": "Data Science",
            "topics": [
                "Deep Learning Frameworks Intro", "Tensors in PyTorch", 
                "TensorFlow Graph Basics", "Keras Sequential API", "PyTorch Autograd", 
                "Building Custom Datasets", "Training Loops", "Loss Functions", 
                "Optimizers (Adam, SGD)", "Model Deployment"
            ]
        },
        "Pandas & NumPy": {
            "icon": "table_chart",
            "category": "Data Science",
            "topics": [
                "NumPy Arrays", "NumPy Matrix Math", "NumPy Indexing",
                "Pandas Series", "Pandas DataFrames", "Pandas Filtering", 
                "Pandas GroupBy", "Pandas Merge & Join", "Pandas Missing Data", 
                "Pandas Time Series"
            ]
        },
        "Scikit-Learn": {
            "icon": "model_training",
            "category": "Data Science",
            "topics": [
                "Scikit-Learn Pipeline", "Data Preprocessing", "Train-Test Split",
                "Feature Scaling", "Cross Validation", "Grid Search CV",
                "Regression Models", "Classification Models", "Clustering Models",
                "Model Saving (Pickle/Joblib)"
            ]
        },
        "Machine Learning": {
            "icon": "psychology",
            "category": "Data Science",
            "topics": [
                "ML Intro", "Supervised Learning", "Unsupervised Learning", 
                "Linear Regression", "Logistic Regression", "Decision Trees", 
                "Random Forest", "Support Vector Machines", "K-Nearest Neighbors", 
                "K-Means Clustering", "PCA", "Model Evaluation", "Bias-Variance Tradeoff"
            ]
        },
        "Deep Learning & NLP": {
            "icon": "smart_toy",
            "category": "Data Science",
            "topics": [
                "Deep Learning Intro", "Neural Networks Basics", "Activation Functions",
                "Backpropagation", "Convolutional Neural Networks (CNNs)", 
                "Recurrent Neural Networks (RNNs)", "LSTMs", "Attention Mechanisms", 
                "Transformers Basics", "NLP Intro", "Word Embeddings", "Text Classification"
            ]
        },
        "Data Analytics": {
            "icon": "analytics",
            "category": "Data Science",
            "topics": [
                "Data Analytics Intro", "Python Pandas", "Data Cleaning", 
                "Data Visualization (Matplotlib)", "Data Visualization (Seaborn)", 
                "Exploratory Data Analysis", "Statistical Testing", "SQL for Data Science", 
                "Power BI Basics", "Tableau Basics"
            ]
        },
        "GRE Preparation": {
            "icon": "auto_stories",
            "category": "Higher Studies",
            "topics": [
                "GRE Intro", "Quantitative Reasoning Basics", "Arithmetic & Algebra", 
                "Geometry", "Data Analysis", "Verbal Reasoning Basics", 
                "Text Completion", "Sentence Equivalence", "Reading Comprehension", 
                "Analytical Writing (AWA)"
            ]
        },
        "TOEFL / IELTS": {
            "icon": "record_voice_over",
            "category": "Higher Studies",
            "topics": [
                "Exam Overview", "Reading Section Strategies", "Listening Section Strategies",
                "Speaking Section Strategies", "Writing Section Strategies", 
                "Vocabulary Building", "Grammar Essentials", "Mock Test Analysis"
            ]
        },
        "Research Methodology": {
            "icon": "science",
            "category": "Higher Studies",
            "topics": [
                "Research Intro", "Literature Review", "Hypothesis Formulation", 
                "Research Design", "Data Collection Methods", "Qualitative Analysis", 
                "Quantitative Analysis", "Writing Research Papers", "Citation & Plagiarism"
            ]
        },
        "Business Fundamentals": {
            "icon": "business",
            "category": "Startup",
            "topics": [
                "Business Intro", "Value Proposition", "Business Models", 
                "Market Research", "Competitor Analysis", "Lean Startup Methodology", 
                "Financial Basics", "Unit Economics", "Legal Structures", 
                "Pitch Deck Creation"
            ]
        },
        "Product Management": {
            "icon": "inventory",
            "category": "Startup",
            "topics": [
                "Product Management Intro", "User Personas", "User Journeys", 
                "Agile & Scrum", "Minimum Viable Product (MVP)", "Wireframing Basics", 
                "Product Metrics (KPIs)", "A/B Testing", "Go-To-Market Strategy"
            ]
        },
        "Digital Marketing": {
            "icon": "campaign",
            "category": "Startup",
            "topics": [
                "Marketing Intro", "SEO Basics", "Content Marketing", 
                "Social Media Marketing", "Email Marketing", "PPC & Google Ads", 
                "Facebook/Meta Ads", "Conversion Rate Optimization", "Growth Hacking"
            ]
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
            is_first_login=False, # Admins skip goal selection
            phone='+1 234 567 890',
            address='123 Admin Lane, Silicon Valley, CA 94025, USA'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        print(f"Created Admin User: {admin_email}")
    
    # Seed Badges
    badges = [
        {'name': 'Legendary Learner', 'description': 'Reached 1000 XP milestone', 'icon': 'military_tech', 'xp': 1000},
        {'name': 'Week Warrior', 'description': 'Maintained a 7-day learning streak', 'icon': 'local_fire_department', 'xp': 0},
        {'name': 'Quiz Master', 'description': 'Scored perfect on 5 quizzes', 'icon': 'fact_check', 'xp': 0},
        {'name': 'AI Explorer', 'description': 'Had 10 meaningful conversations with AI', 'icon': 'psychology', 'xp': 0},
        {'name': 'Steady Scholar', 'description': 'Spent over 10 hours learning', 'icon': 'timer', 'xp': 0}
    ]
    
    for b_data in badges:
        badge = Badge.query.filter_by(name=b_data['name']).first()
        if not badge:
            badge = Badge(
                name=b_data['name'],
                description=b_data['description'],
                icon=b_data['icon'],
                xp_requirement=b_data['xp']
            )
            db.session.add(badge)
            print(f"Created Badge: {b_data['name']}")

    db.session.commit()
    print("Database Seeding Complete!")
