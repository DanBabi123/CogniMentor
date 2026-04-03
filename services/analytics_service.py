from database.database import db
from models.quiz import QuizAttempt
from models.activity import ActivityLog
from models.subject import Subject, Topic
from datetime import datetime, timedelta
from collections import defaultdict
import math

class AnalyticsService:
    @staticmethod
    def get_deep_analytics(user_id):
        # 1. Basic Stats
        attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(QuizAttempt.timestamp.asc()).all()
        total_quizzes = len(attempts)
        avg_score = int(sum(a.score/a.max_score*100 for a in attempts)/total_quizzes) if total_quizzes > 0 else 0
        
        # 2. Time Tracking
        logs = ActivityLog.query.filter_by(user_id=user_id).all()
        total_seconds = sum(log.duration for log in logs if log.duration)
        total_minutes = total_seconds // 60
        
        # 3. Weekly Trends (Last 7 Days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        weekly_logs = [log for log in logs if log.timestamp >= seven_days_ago]
        daily_minutes = defaultdict(int)
        for log in weekly_logs:
            day = log.timestamp.strftime('%a')
            daily_minutes[day] += (log.duration or 0) // 60
        
        days_order = [(datetime.utcnow() - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]
        weekly_trend_data = [daily_minutes[d] for d in days_order]
        
        # 4. Accuracy Rate Calculation
        total_questions = sum(a.max_score for a in attempts)
        total_correct = sum(a.score for a in attempts)
        accuracy_rate = int((total_correct / total_questions * 100)) if total_questions > 0 else 0
        
        # 5. Peak Performance Time (The "AI" Insight)
        # Group quiz scores by hour of the day
        hour_stats = defaultdict(list)
        for a in attempts:
            hour = a.timestamp.hour
            hour_stats[hour].append(a.score / a.max_score)
            
        peak_hour = -1
        max_avg = -1
        for hour, scores in hour_stats.items():
            avg = sum(scores) / len(scores)
            if avg > max_avg:
                max_avg = avg
                peak_hour = hour
        
        peak_time_str = f"{peak_hour}:00" if peak_hour != -1 else "N/A"
        if peak_hour != -1:
            end_hour = (peak_hour + 2) % 24
            peak_time_str = f"{peak_hour}:00 - {end_hour}:00"
            
        # 6. Weak vs Strong Subjects
        subject_map = defaultdict(list)
        for a in attempts:
            if a.topic and a.topic.subject:
                subject_map[a.topic.subject.name].append(a.score / a.max_score)
        
        subject_performance = []
        for name, scores in subject_map.items():
            avg = int((sum(scores) / len(scores)) * 100)
            # Find a valid topic_id for this subject to enable retrying
            sample_attempt = next((a for a in attempts if a.topic and a.topic.subject.name == name), None)
            topic_id = sample_attempt.topic_id if sample_attempt else None
            
            subject_performance.append({
                'name': name,
                'avg': avg,
                'topic_id': topic_id,
                'is_weak': avg < 60
            })
            
        subject_performance.sort(key=lambda x: x['avg'])
        weakest = [s for s in subject_performance if s['is_weak']]
        strongest = [s for s in subject_performance if s['avg'] >= 80]
        
        # 7. Focus Score (Weighted between consistency and accuracy)
        # Consistency: Days active in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_days = len(set(log.timestamp.date() for log in logs if log.timestamp >= thirty_days_ago))
        consistency_factor = min(active_days / 20.0, 1.0) # 20 days = 100% consistency
        accuracy_factor = accuracy_rate / 100.0
        focus_score = int((consistency_factor * 40) + (accuracy_factor * 60)) # Weighted 40/60
        
        # 8. Behavioral Insights
        behavioral_insights = []
        if peak_hour != -1:
            behavioral_insights.append({
                'type': 'time',
                'text': f"Your neural focus peaks around {peak_time_str}. Try tackling complex topics then!",
                'icon': 'schedule_send'
            })
            
        if weakest:
            behavioral_insights.append({
                'type': 'subject',
                'text': f"Your clarity scores drop slightly in {weakest[0]['name']}. Let's revisit the fundamental modules there.",
                'icon': 'trending_down'
            })
        else:
            behavioral_insights.append({
                'type': 'general',
                'text': "You're maintaining a steady performance curve across all your active subjects. Keep it up!",
                'icon': 'verified'
            })
            
        if focus_score > 80:
            behavioral_insights.append({
                'type': 'streak',
                'text': "Your focus score is elite. You're currently in a high-retention state.",
                'icon': 'bolt'
            })

        return {
            'total_quizzes': total_quizzes,
            'avg_score': avg_score,
            'accuracy_rate': accuracy_rate,
            'total_minutes': total_minutes,
            'focus_score': focus_score,
            'peak_time': peak_time_str,
            'weekly_trend_labels': days_order,
            'weekly_trend_data': weekly_trend_data,
            'subject_performance': subject_performance,
            'behavioral_insights': behavioral_insights,
            'attempts': sorted(attempts, key=lambda x: x.timestamp, reverse=True)
        }
