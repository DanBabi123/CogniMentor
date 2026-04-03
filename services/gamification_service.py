from models.user import User
from models.gamification import Badge, UserBadge
from services.notification_service import NotificationService
from database.database import db
from datetime import datetime

class GamificationService:
    @staticmethod
    def get_leaderboard(limit=10):
        return User.query.filter(User.role == 'student').order_by(User.total_xp.desc()).limit(limit).all()

    @staticmethod
    def get_user_rank(user_id):
        user = db.session.get(User, user_id)
        if not user: return None
        
        # Simple subquery rank
        rank = User.query.filter(User.role == 'student', User.total_xp > user.total_xp).count() + 1
        return rank

    @staticmethod
    def check_and_award_badges(user_id):
        user = db.session.get(User, user_id)
        if not user: return []
        
        new_badges = []
        # Example Logic: Top Learner (1000 XP)
        if user.total_xp >= 1000:
            badge = Badge.query.filter_by(name="Legendary Learner").first()
            if badge and not any(ub.badge_id == badge.id for ub in user.badges):
                ub = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(ub)
                new_badges.append(badge)
                NotificationService.create_notification(
                    user_id=user.id,
                    title="New Badge Earned!",
                    message=f"Congratulations! You've earned the '{badge.name}' badge.",
                    type='badge'
                )
        
        # Streak Badge
        if user.streak_count >= 7:
            badge = Badge.query.filter_by(name="Week Warrior").first()
            if badge and not any(ub.badge_id == badge.id for ub in user.badges):
                ub = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(ub)
                new_badges.append(badge)
                NotificationService.create_notification(
                    user_id=user.id,
                    title="Streak Milestone!",
                    message=f"You've earned the '{badge.name}' badge for your 7-day streak!",
                    type='badge'
                )

        db.session.commit()
        return new_badges
