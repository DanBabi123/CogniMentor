from models.notification import Notification
from database.database import db

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, type='info', link=None):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            link=link
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_unread_notifications(user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(notification_id):
        notification = db.session.get(Notification, notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False).update({Notification.is_read: True})
        db.session.commit()
