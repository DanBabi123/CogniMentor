from database.database import db
from models.user import User, PasswordReset
from auth.otp_service import OTPService
import uuid
from datetime import datetime, timedelta
from extensions import mail
from flask_mail import Message
from flask import url_for
from models.activity import ActivityLog

class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            
            # Log Activity
            log = ActivityLog(user_id=user.id, activity_type='login')
            db.session.add(log)
            
            db.session.commit()
            return user, None
        return None, "Login Unsuccessful. Please check email and password"

    @staticmethod
    def register_user(name, email, password):
        if User.query.filter_by(email=email).first():
            return None, "Email already registered. Please log in."
        
        user = User()
        user.name = name
        user.email = email
        user.set_password(password)
        user.is_verified = False
        db.session.add(user)
        
        try:
            db.session.commit()
            OTPService.send_otp(user.id)
            return user, None
        except Exception as e:
            db.session.rollback()
            return None, "An error occurred during registration. Please try again."

    @staticmethod
    def verify_otp(user_id, otp_code):
        success, message = OTPService.verify_otp(user_id, otp_code)
        if success:
            user = db.session.get(User, user_id)
            user.is_verified = True
            db.session.commit()
            return user, None
        return None, message

    @staticmethod
    def request_password_reset(email):
        user = User.query.filter_by(email=email).first()
        if user:
            token = str(uuid.uuid4())
            reset_entry = PasswordReset(
                user_id=user.id,
                token=token,
                expires_at=datetime.utcnow() + timedelta(minutes=10)
            )
            db.session.add(reset_entry)
            db.session.commit()
            
            try:
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                msg = Message('Password Reset Request - CogniMentor',
                              sender='medadanbabi@gmail.com',
                              recipients=[user.email])
                msg.body = f"Hello {user.name},\n\nTo reset your password, visit the following link:\n{reset_url}\n\nIf you did not make this request then simply ignore this email and no changes will be made.\n\nRegards,\nCogniMentor Team"
                mail.send(msg)
                return True, "An email has been sent with instructions to reset your password."
            except Exception as e:
                print(f"Error sending email: {e}")
                return False, "Error sending email. Please try again later."
        return True, "If an account exists for that email, a reset link has been sent."

    @staticmethod
    def reset_password(token, new_password):
        reset_entry = PasswordReset.query.filter_by(token=token).first()
        if not reset_entry or reset_entry.expires_at < datetime.utcnow():
            return False, "Invalid or expired token."
        
        user = db.session.get(User, reset_entry.user_id)
        if not user:
            return False, "User not found."
            
        user.set_password(new_password)
        db.session.delete(reset_entry)
        db.session.commit()
        return True, "Your password has been updated! You can now login."

        db.session.commit()
