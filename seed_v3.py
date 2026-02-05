from app import create_app
from database.database import db
from database.models import Subject, Topic, User, Question

app = create_app()

def seed_v3():
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        db.create_all()

        # Users (Admin)
        admin = User(name="Admin User", email="admin@cogni.com", is_verified=True, role='admin')
        admin.set_password("admin123")
        db.session.add(admin)
        print("Admin user created.")

        # Helper to add topic with questions
        def add_topic(subject_id, title, difficulty, order, content, questions_data):
            topic = Topic(
                subject_id=subject_id,
                title=title,
                difficulty=difficulty,
                order_index=order,
                content_payload=content
            )
            db.session.add(topic)
            db.session.commit() # Commit to get ID
            
            for q in questions_data:
                question = Question(
                    topic_id=topic.id,
                    text=q['text'],
                    options=q['options'],
                    correct_index=q['correct'],
                    explanation=q.get('explanation', ''),
                    difficulty=q.get('difficulty', 'Medium')
                )
                db.session.add(question)
            db.session.commit()

        # ==========================================
        # 1. PYTHON PROGRAMMING (Beginner -> Advanced)
        # ==========================================
        python = Subject(name="Python Programming", description="Complete Python Bootcamp: Beginner to Expert.", icon="code")
        db.session.add(python)
        db.session.commit()

        # Python Content & Questions
        py_topics = [
            {
                "title": "Python Basics: Variables & Types",
                "difficulty": "Beginner",
                "order": 1,
                "content": {
                    "objectives": ["Python Syntax", "Variables", "Data Types"],
                    "sections": [
                        {"heading": "Introduction", "content": "Python is a high-level, interpreted language known for its readability.", "code": "print('Hello World')"},
                        {"heading": "Variables", "content": "Variables store data. Python is dynamically typed.", "code": "x = 5\nname = 'Alice'"}
                    ]
                },
                "questions": [
                    {"text": "Which of the following is a valid variable name in Python?", "options": ["1var", "var-name", "_var_name", "var name"], "correct": 2, "explanation": "Variable names cannot start with numbers or contain hyphens/spaces.", "difficulty": "Easy"},
                    {"text": "What is the output of print(type(5.0))?", "options": ["<class 'int'>", "<class 'float'>", "<class 'str'>", "<class 'double'>"], "correct": 1, "explanation": "5.0 is a floating point number.", "difficulty": "Easy"},
                    {"text": "How do you create a comment in Python?", "options": ["// Comment", "# Comment", "/* Comment */", "<!-- Comment -->"], "correct": 1, "explanation": "# is used for single-line comments.", "difficulty": "Easy"},
                    {"text": "Which data type is immutable?", "options": ["List", "Dictionary", "Set", "Tuple"], "correct": 3, "explanation": "Tuples are immutable sequences.", "difficulty": "Medium"},
                    {"text": "What is the result of 3 ** 2?", "options": ["6", "5", "9", "Error"], "correct": 2, "explanation": "** is the exponentiation operator.", "difficulty": "Easy"}
                ]
            },
            {
                "title": "Control Flow: Loops & Conditionals",
                "difficulty": "Beginner",
                "order": 2,
                "content": {
                    "objectives": ["If/Else", "For Loops", "While Loops"],
                    "sections": [
                        {"heading": "If Statements", "content": "Decisions are made using if...elif...else.", "code": "if x > 5: print('Big')"},
                        {"heading": "Loops", "content": "Iterate over sequences with for loops.", "code": "for i in range(5): print(i)"}
                    ]
                },
                "questions": [
                    {"text": "What keyword is used to skip the current iteration of a loop?", "options": ["break", "stop", "continue", "pass"], "correct": 2, "explanation": "continue skips the rest of the code inside the loop for the current iteration.", "difficulty": "Medium"},
                    {"text": "How many times will 'for i in range(3):' execute?", "options": ["2", "3", "4", "0"], "correct": 1, "explanation": "range(3) produces 0, 1, 2.", "difficulty": "Easy"},
                    {"text": "Which statement is used to exit a loop prematurely?", "options": ["exit", "break", "continue", "return"], "correct": 1, "explanation": "break terminates the loop.", "difficulty": "Easy"}
                ]
            },
            {
                "title": "Functions & Modules",
                "difficulty": "Intermediate",
                "order": 3,
                "content": {
                    "objectives": ["Defining Functions", "Arguments", "Imports"],
                    "sections": [
                        {"heading": "Functions", "content": "Blocks of reusable code.", "code": "def greet(name):\n  return f'Hello {name}'"},
                        {"heading": "Modules", "content": "Files containing Python code.", "code": "import math\nprint(math.pi)"}
                    ]
                },
                "questions": [
                    {"text": "Which keyword is used to define a function?", "options": ["func", "def", "function", "define"], "correct": 1, "explanation": "def is the keyword.", "difficulty": "Easy"},
                    {"text": "What is the correct way to import only 'sqrt' from 'math'?", "options": ["import sqrt from math", "from math import sqrt", "import math.sqrt", "using math.sqrt"], "correct": 1, "explanation": "from ... import syntax is used for specific specific items.", "difficulty": "Medium"},
                    {"text": "What is a lambda function?", "options": ["A large function", "A recursive function", "An anonymous small function", "A loop"], "correct": 2, "explanation": "Lambda functions are small, anonymous functions defined with the lambda keyword.", "difficulty": "Medium"}
                ]
            },
            {
                "title": "OOPs Concepts",
                "difficulty": "Advanced",
                "order": 4,
                "content": {
                    "objectives": ["Classes", "Inheritance", "Polymorphism"],
                    "sections": [
                        {"heading": "Classes", "content": "Blueprints for creating objects.", "code": "class Dog:\n  def bark(self): print('Woof')"}
                    ]
                },
                "questions": [
                    {"text": "Which keyword refers to the current instance of the class?", "options": ["this", "self", "me", "it"], "correct": 1, "explanation": "self is the convention in Python.", "difficulty": "Easy"},
                    {"text": "What is inheritance?", "options": ["Creating a new class from an existing one", "Hiding data", "Polymorphism", "Error handling"], "correct": 0, "explanation": "Inheritance allows a class to derive attributes and methods from another class.", "difficulty": "Medium"},
                    {"text": "Which method is the constructor?", "options": ["__init__", "__start__", "__main__", "__construct__"], "correct": 0, "explanation": "__init__ initializes the object.", "difficulty": "Medium"}
                ]
            },
             {
                "title": "Advanced Python: Decorators & Generators",
                "difficulty": "Expert",
                "order": 5,
                "content": {
                    "objectives": ["Decorators", "Generators", "Context Managers"],
                    "sections": [
                        {"heading": "Decorators", "content": "Modify the behavior of functions.", "code": "@my_decorator\ndef func(): pass"},
                        {"heading": "Generators", "content": "Functions that yield values one by one.", "code": "def gen(): yield 1"}
                    ]
                },
                "questions": [
                    {"text": "What keyword is used in a generator function?", "options": ["return", "yield", "emit", "send"], "correct": 1, "explanation": "yield produces a value and pauses the function.", "difficulty": "Advanced"},
                    {"text": "What does a decorator accept as an argument?", "options": ["A class", "A string", "A function", "A list"], "correct": 2, "explanation": "Decorators wrap functions.", "difficulty": "Advanced"}
                ]
            }
        ]

        for t in py_topics:
            add_topic(python.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])

        # ==========================================
        # 2. DSA (Beginner -> Advanced)
        # ==========================================
        dsa = Subject(name="Data Structures & Algorithms", description="Master DSA for FAANG interviews.", icon="dns")
        db.session.add(dsa)
        db.session.commit()

        dsa_topics = [
            {
                "title": "Arrays & Hashing",
                "difficulty": "Beginner",
                "order": 1,
                "content": {"objectives": ["Arrays", "Hash Maps"], "sections": []},
                "questions": [
                    {"text": "What is the time complexity to access an element in an array by index?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "correct": 0, "explanation": "Array indexing is constant time.", "difficulty": "Easy"},
                    {"text": "Which data structure handles collisions using chaining or open addressing?", "options": ["Stack", "Queue", "Hash Table", "Tree"], "correct": 2, "explanation": "Hash tables use these methods for collision resolution.", "difficulty": "Medium"},
                    {"text": "What is the worst-case search time in a Hash Table?", "options": ["O(1)", "O(n)", "O(log n)", "O(n log n)"], "correct": 1, "explanation": "O(n) if all keys hash to the same bucket.", "difficulty": "Medium"}
                ]
            },
            {
                "title": "Linked Lists",
                "difficulty": "Intermediate",
                "order": 2,
                "content": {"objectives": ["Singly Linked List", "Floyd's Cycle Detection"], "sections": []},
                "questions": [
                    {"text": "What is the time complexity to insert at the beginning of a Linked List?", "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"], "correct": 0, "explanation": "It only involves updating the head pointer.", "difficulty": "Easy"},
                    {"text": "Which algorithm detects a cycle in a Linked List?", "options": ["Binary Search", "Floyd's Tortoise and Hare", "KMP Algorithm", "Dijkstra"], "correct": 1, "explanation": "Floyd's algorithm uses two pointers moving at different speeds.", "difficulty": "Medium"}
                ]
            },
            {
                "title": "Trees & Graphs",
                "difficulty": "Advanced",
                "order": 3,
                "content": {"objectives": ["BST", "BFS", "DFS"], "sections": []},
                "questions": [
                    {"text": "In a Binary Search Tree (BST), the left child is always...", "options": ["Greater than the root", "Smaller than the root", "Equal to the root", "Random"], "correct": 1, "explanation": "BST property: Left < Root < Right.", "difficulty": "Easy"},
                    {"text": "Which traversal is used for BFS?", "options": ["Level Order", "Inorder", "Preorder", "Postorder"], "correct": 0, "explanation": "BFS visits nodes level by level.", "difficulty": "Medium"},
                    {"text": "What is the time complexity of DFS?", "options": ["O(V)", "O(E)", "O(V+E)", "O(V*E)"], "correct": 2, "explanation": "Vertices + Edges.", "difficulty": "Medium"}
                ]
            }
        ]
        
        for t in dsa_topics:
             add_topic(dsa.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])

        # ==========================================
        # 3. GATE CSE / IT
        # ==========================================
        gate = Subject(name="GATE CSE & IT", description="Comprehensive preparation for GATE.", icon="menu_book")
        db.session.add(gate)
        db.session.commit()

        gate_topics = [
            {
                "title": "Theory of Computation (TOC)",
                "difficulty": "Advanced",
                "order": 1,
                "content": {"objectives": ["Automata", "Grammars"], "sections": []},
                "questions": [
                    {"text": "A DFA accepts what kind of language?", "options": ["Context Sensitive", "Recursive", "Regular", "Context Free"], "correct": 2, "explanation": "Finite Automata accept Regular Languages.", "difficulty": "Medium"},
                    {"text": "The intersection of two regular languages is...", "options": ["Regular", "Context Free", "Non-Regular", "None"], "correct": 0, "explanation": "Regular languages are closed under intersection.", "difficulty": "Hard"}
                ]
            },
            {
                "title": "Operating Systems",
                "difficulty": "Advanced",
                "order": 2,
                "content": {"objectives": ["Semaphores", "Paging"], "sections": []},
                "questions": [
                    {"text": "Which of these is NOT a scheduling algorithm?", "options": ["Round Robin", "SJF", "Dijkstra", "FCFS"], "correct": 2, "explanation": "Dijkstra is a shortest path algorithm for graphs.", "difficulty": "Easy"},
                    {"text": "What is the solution to the Critical Section problem?", "options": ["Paging", "Semaphores", "Segmentation", "Caching"], "correct": 1, "explanation": "Semaphores are synchronization tools.", "difficulty": "Medium"}
                ]
            },
            {
                "title": "DBMS",
                "difficulty": "Advanced",
                "order": 3,
                "content": {"objectives": ["Normalization", "SQL", "Transactions"], "sections": []},
                "questions": [
                    {"text": "Which Normal Form eliminates transitive dependency?", "options": ["1NF", "2NF", "3NF", "BCNF"], "correct": 2, "explanation": "3NF requires no transitive dependencies.", "difficulty": "Medium"},
                    {"text": "What does ACID stand for?", "options": ["Atomicity, Consistency, Isolation, Durability", "Accuracy, Consistency, Isolation, Data", "Atomicity, Code, Integrity, Data", "None"], "correct": 0, "explanation": "Standard transaction properties.", "difficulty": "Easy"}
                ]
            }
        ]
        
        for t in gate_topics:
             add_topic(gate.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])

        # ==========================================
        # 4. APTITUDE & REASONING
        # ==========================================
        apt = Subject(name="Aptitude & Reasoning", description="Quant and Logic for competitive exams.", icon="calculate")
        db.session.add(apt)
        db.session.commit()

        apt_topics = [
            {
                "title": "Quantitative Aptitude",
                "difficulty": "Intermediate",
                "order": 1,
                "content": {"objectives": ["Maths"], "sections": []},
                "questions": [
                    {"text": "If A completes work in 10 days and B in 15 days, how long together?", "options": ["5 days", "6 days", "8 days", "7.5 days"], "correct": 1, "explanation": "1/10 + 1/15 = 5/30 = 1/6. So 6 days.", "difficulty": "Medium"},
                    {"text": "What is 20% of 500?", "options": ["100", "50", "200", "20"], "correct": 0, "explanation": "0.20 * 500 = 100", "difficulty": "Easy"}
                ]
            }
        ]
        
        for t in apt_topics:
             add_topic(apt.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])


        # ==========================================
        # 5. GOVERNMENT EXAMS
        # ==========================================
        govt = Subject(name="Government Exams", description="SSC, Banking, Railways prep.", icon="account_balance")
        db.session.add(govt)
        db.session.commit()
        
        govt_topics = [
            {
                "title": "General Awareness",
                "difficulty": "Intermediate",
                "order": 1,
                "content": {"objectives": ["GK"], "sections": []},
                "questions": [
                    {"text": "Who is known as the Iron Man of India?", "options": ["Gandhi", "Nehru", "Sardar Patel", "Bose"], "correct": 2, "explanation": "Sardar Vallabhbhai Patel.", "difficulty": "Easy"},
                    {"text": "RBI Headquarter is located in...", "options": ["Delhi", "Mumbai", "Kolkata", "Chennai"], "correct": 1, "explanation": "Mumbai.", "difficulty": "Easy"}
                ]
            }
        ]
        
        for t in govt_topics:
             add_topic(govt.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])

        # ==========================================
        # 6. AI & ML
        # ==========================================
        ai = Subject(name="AI & Machine Learning", description="Future tech: AI, ML, DL, and GenAI.", icon="psychology")
        db.session.add(ai)
        db.session.commit()

        ai_topics = [
            {
                "title": "Machine Learning Basics",
                "difficulty": "Beginner",
                "order": 1,
                "content": {"objectives": ["Supervised", "Unsupervised"], "sections": []},
                "questions": [
                    {"text": "Which of these is a Supervised Learning algorithm?", "options": ["K-Means", "Linear Regression", "PCA", "Apriori"], "correct": 1, "explanation": "Linear Regression uses labeled data.", "difficulty": "Medium"},
                    {"text": "Overfitting happens when...", "options": ["Model is too simple", "Model learns noise/training data too well", "Data is insufficient", "None"], "correct": 1, "explanation": "High variance, low bias.", "difficulty": "Medium"}
                ]
            },
            {
                "title": "Deep Learning & Neural Networks",
                "difficulty": "Advanced",
                "order": 2,
                "content": {"objectives": ["ANN", "CNN"], "sections": []},
                "questions": [
                    {"text": "What is the activation function used for?", "options": ["To calculate error", "To introduce non-linearity", "To initialize weights", "To optimization"], "correct": 1, "explanation": "Without it, a NN is just a linear regression.", "difficulty": "Medium"},
                    {"text": "What does CNN stand for?", "options": ["Central Neural Network", "Convolutional Neural Network", "Complex Neural Network", "Cyber Neural Network"], "correct": 1, "explanation": "Used primarily for image processing.", "difficulty": "Easy"}
                ]
            }
        ]

        for t in ai_topics:
             add_topic(ai.id, t['title'], t['difficulty'], t['order'], t['content'], t['questions'])


        print("Database Seeded Successfully with V3 Content (Questions Included)!")

if __name__ == '__main__':
    seed_v3()
