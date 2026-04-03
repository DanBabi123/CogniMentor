from ai_engine.content_engine import ai_engine
from models.quiz import QuizAttempt, Question
from models.progress import LearningProgress
from models.subject import Topic
from database.database import db
from services.progress_service import ProgressService

class QuizService:
    @staticmethod
    def generate_quiz_for_topic(user_id, topic_id):
        topic = db.session.get(Topic, topic_id)
        progress = LearningProgress.query.filter_by(user_id=user_id, topic_id=topic_id).first()
        
        distribution = {'Easy': 2, 'Medium': 2, 'Hard': 1}
        if progress:
            cleared = progress.difficulty_cleared or {}
            if cleared.get('Hard'):
                distribution = {'Easy': 1, 'Medium': 2, 'Hard': 2}
            elif cleared.get('Medium'):
                distribution = {'Easy': 1, 'Medium': 3, 'Hard': 1}
            elif cleared.get('Easy'):
                distribution = {'Easy': 1, 'Medium': 3, 'Hard': 1}
            else:
                distribution = {'Easy': 3, 'Medium': 2, 'Hard': 0}

        # Provide full context to AI so it knows what subject the module belongs to
        contextual_topic = f"Subject: {topic.subject.name}, Topic/Module: {topic.title}"
        questions = ai_engine.generate_quiz(contextual_topic, difficulty_distribution=distribution)
        
        # Ensure strict ramping: Easy -> Medium -> Hard
        difficulty_order = {'Easy': 0, 'Medium': 1, 'Hard': 2, 'Beginner': 0, 'Advanced': 2}
        sorted_questions = sorted(questions, key=lambda x: difficulty_order.get(x.get('difficulty', 'Medium'), 1))
        
        return sorted_questions

    @staticmethod
    def process_quiz_submission(user_id, topic_id, form_data, session_answers, time_taken=None):
        score = 0
        total_questions = len(session_answers)
        diff_stats = {'Easy': {'total': 0, 'correct': 0}, 
                      'Medium': {'total': 0, 'correct': 0}, 
                      'Hard': {'total': 0, 'correct': 0}}
        
        report = []
        xp_earned = 0
        
        # Difficulty Normalization
        def normalize_diff(d):
            d = str(d).capitalize()
            if 'Easy' in d or 'Beginner' in d: return 'Easy'
            if 'Hard' in d or 'Advanced' in d: return 'Hard'
            return 'Medium'

        for q_id, q_data in session_answers.items():
            if q_data is None: continue
                
            correct_opt = q_data['correct']
            difficulty = normalize_diff(q_data.get('difficulty', 'Medium'))
            
            if difficulty not in diff_stats:
                diff_stats[difficulty] = {'total': 0, 'correct': 0}
            diff_stats[difficulty]['total'] += 1
            
            user_answer = form_data.get(f'q_{q_id}')
            is_correct = False
            if user_answer and str(user_answer).isdigit() and int(user_answer) == correct_opt:
                score += 1
                diff_stats[difficulty]['correct'] += 1
                is_correct = True
                
                # Award XP
                xp_earned += 10
                if difficulty == 'Hard': xp_earned += 5
                if difficulty == 'Medium': xp_earned += 2
            
            # Prepare Report Entry
            q_text = "Dynamic Question"
            explanation = "Check concept content."
            try:
                if q_id.isdigit():
                    q_db = Question.query.get(int(q_id))
                    if q_db:
                        q_text = q_db.text
                        explanation = q_db.explanation
            except: pass

            report.append({
                'question': q_text,
                'user_answer': f"Option {chr(65+int(user_answer))}" if user_answer and str(user_answer).isdigit() else "Skipped",
                'correct_answer': f"Option {chr(65+correct_opt)}",
                'explanation': explanation,
                'is_correct': is_correct,
                'difficulty': difficulty
            })

        score_percent = (score / total_questions * 100) if total_questions > 0 else 0
        
        if score_percent >= 60:
            xp_earned += 50 # Passing bonus
            
        # Update Progress
        progress = ProgressService.update_topic_progress(user_id, topic_id, score_percent)
        
        # Update Cleared Difficulties
        current_cleared = progress.difficulty_cleared or {}
        for diff, stats in diff_stats.items():
            if stats['total'] > 0 and (stats['correct'] / stats['total']) >= 0.6:
                current_cleared[diff] = True
        progress.difficulty_cleared = current_cleared
        
        # Save Attempt
        attempt = QuizAttempt(
            user_id=user_id, 
            topic_id=topic_id, 
            score=score, 
            max_score=total_questions,
            time_taken=time_taken
        )
        db.session.add(attempt)
        db.session.commit()
        
        # Award XP and Log Activity (handled in routes or here)
        # We'll stick to returning for now to maintain consistency
        
        feedback = ai_engine.generate_feedback(score, total_questions, "") if score >= (total_questions * 0.6) else "Below expectations. Please review."
        
        return {
            'attempt': attempt, 
            'is_passed': score_percent >= 60,
            'score_percent': score_percent,
            'feedback': feedback,
            'report': report,
            'diff_stats': diff_stats,
            'xp_earned': xp_earned,
            'strength_level': "Strong" if score_percent >= 70 else "Average"
        }

    @staticmethod
    def generate_mock_test(subject_id, level):
        from models.subject import Topic
        subject_topics = sorted(Topic.query.filter_by(subject_id=subject_id).all(), key=lambda t: t.order_index)
        start_idx = (level - 1) * 5
        end_idx = level * 5
        topics = subject_topics[start_idx:end_idx]
        
        if topics:
            subject_name = topics[0].subject.name
            prompt_topic = f"Subject: {subject_name}. Comprehensive Review Checkpoint spanning these concepts: " + ", ".join([t.title for t in topics])
        else:
            prompt_topic = "Comprehensive Review Checkpoint"
            
        distribution = {'Easy': 4, 'Medium': 4, 'Hard': 2} # 10 questions total
        
        return ai_engine.generate_quiz(prompt_topic, difficulty_distribution=distribution), topics

    @staticmethod
    def process_mock_submission(user_id, subject_id, level, form_data, session_answers, time_taken=None):
        score = 0
        total_questions = len(session_answers)
        diff_stats = {'Easy': {'total': 0, 'correct': 0}, 
                      'Medium': {'total': 0, 'correct': 0}, 
                      'Hard': {'total': 0, 'correct': 0}}
        report = []
        xp_earned = 0
        
        def normalize_diff(d):
            d = str(d).capitalize()
            if 'Easy' in d or 'Beginner' in d: return 'Easy'
            if 'Hard' in d or 'Advanced' in d: return 'Hard'
            return 'Medium'

        for q_id, q_data in session_answers.items():
            if q_data is None: continue
            correct_opt = q_data['correct']
            difficulty = normalize_diff(q_data.get('difficulty', 'Medium'))
            
            if difficulty not in diff_stats:
                diff_stats[difficulty] = {'total': 0, 'correct': 0}
            diff_stats[difficulty]['total'] += 1
            
            user_answer = form_data.get(f'q_{q_id}')
            is_correct = False
            
            if user_answer and str(user_answer).isdigit() and int(user_answer) == correct_opt:
                score += 1
                diff_stats[difficulty]['correct'] += 1
                is_correct = True
                xp_earned += 15
                if difficulty == 'Hard': xp_earned += 10
            
            report.append({
                'question': "Dynamic Exam Question",
                'user_answer': f"Option {chr(65+int(user_answer))}" if user_answer and str(user_answer).isdigit() else "Skipped",
                'correct_answer': f"Option {chr(65+correct_opt)}",
                'explanation': "Concept heavily covered in prior modules.",
                'is_correct': is_correct,
                'difficulty': difficulty
            })
            
        score_percent = (score / total_questions * 100) if total_questions > 0 else 0
        is_passed = score_percent >= 60
        
        if is_passed:
            from models.progress import MockTestProgress
            from models.user import User
            
            xp_earned += 100 # Big bonus for passing Checkpoint
            prog = MockTestProgress.query.filter_by(user_id=user_id, subject_id=subject_id, checkpoint_level=level).first()
            if not prog:
                prog = MockTestProgress(user_id=user_id, subject_id=subject_id, checkpoint_level=level)
                db.session.add(prog)
            prog.is_passed = True
            
            user = db.session.get(User, user_id)
            if user: 
                user.total_xp += xp_earned
            
            db.session.commit()
            
        return {
            'score_percent': score_percent,
            'xp_earned': xp_earned,
            'report': report,
            'is_passed': is_passed,
            'feedback': "Excellent work proving your mastery across these modules!" if is_passed else "Please firmly revise the preceding 5 chapters.",
            'diff_stats': diff_stats,
            'attempt': type('Dummy', (object,), {'score': score, 'max_score': total_questions, 'topic_id': None})()
        }
