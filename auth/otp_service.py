import random
import datetime
from database.models import User
from database.database import db
from extensions import mail
from flask_mail import Message

class OTPService:
    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_otp(user_id):
        user = db.session.get(User, user_id)
        if not user:
            return False
            
        otp = OTPService.generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
        db.session.commit()
        
        # Real Email Sending
        try:
            msg = Message('CogniMentor Verification Code',
                          sender='medadanbabi@gmail.com',
                          recipients=[user.email])
            msg.body = f"Hello {user.name},\n\nYour Admin Access / Verification Code is: {otp}\n\nThis code expires in 5 minutes.\n\nRegards,\nCogniMentor Team"
            mail.send(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def verify_otp(user_id, otp_input):
        user = db.session.get(User, user_id)
        if not user or not user.otp_code:
            return False, "Invalid Request"
            
        if user.otp_code != otp_input:
            return False, "Invalid OTP"
            
        if datetime.datetime.utcnow() > user.otp_expiry:
            return False, "OTP Expired"
            
        # Success
        user.is_verified = True
        user.otp_code = None
        user.otp_expiry = None
        db.session.commit()
        return True, "Verification Successful"
