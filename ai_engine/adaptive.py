from database.models import QuizAttempt, Topic, LearningProgress
from database.database import db

class AdaptiveEngine:
    def get_recommendation(self, user_id):
        # 1. Analyze Weak Areas (Score < 70%) to prioritize remediation
        weak_attempt = QuizAttempt.query.filter_by(user_id=user_id).filter(QuizAttempt.score < 70).order_by(QuizAttempt.timestamp.desc()).first()
        
        if weak_attempt:
            topic = db.session.get(Topic, weak_attempt.topic_id)
            return {
                "next_action": "Remediate",
                "recommended_topic": topic.title,
                "difficulty_level": "Review",
                "study_time": "20 mins",
                "reason": f"You scored {weak_attempt.score}% on {topic.title}. Let's turn that into a win!",
                "link": topic.id
            }

        # 2. If no weak areas, find the last successful topic and suggest the next one
        last_success = QuizAttempt.query.filter_by(user_id=user_id).filter(QuizAttempt.score >= 70).order_by(QuizAttempt.timestamp.desc()).first()
        
        if last_success:
            current_topic = db.session.get(Topic, last_success.topic_id)
            next_topic = Topic.query.filter(Topic.id > current_topic.id).order_by(Topic.id.asc()).first()
            
            if next_topic:
                 return {
                    "next_action": "Advance",
                    "recommended_topic": next_topic.title,
                    "difficulty_level": next_topic.difficulty,
                    "study_time": "45 mins",
                    "reason": f"Great job on {current_topic.title}! precise next step: {next_topic.title}.",
                    "link": next_topic.id
                }
        
        # 3. Fallback for new users (Start with first topic)
        first_topic = Topic.query.order_by(Topic.id.asc()).first()
        if first_topic:
             return {
                "next_action": "Start Journey",
                "recommended_topic": first_topic.title,
                "difficulty_level": first_topic.difficulty,
                "study_time": "30 mins",
                "reason": "Identify your first challenge. Let's begin!",
                "link": first_topic.id
            }
            
        return {
            "next_action": "Wait",
            "recommended_topic": "No Content",
            "difficulty_level": "-",
            "study_time": "0 mins",
            "reason": "Curriculum is empty. Please contact admin.",
            "link": None
        }

adaptive_engine = AdaptiveEngine()
