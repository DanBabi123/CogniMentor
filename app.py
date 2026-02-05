from flask import Flask
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, SQLALCHEMY_TRACK_MODIFICATIONS, UPLOAD_FOLDER
from database.database import db

from dotenv import load_dotenv
import os

load_dotenv()

def create_app(test_config=None):

    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    # Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'medadanbabi@gmail.com'
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

    if test_config:
        app.config.update(test_config)

    # Initialize Extensions
    db.init_app(app)
    
    from extensions import mail
    mail.init_app(app)

    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # type: ignore
    login_manager.init_app(app)

    from database.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))


    # Register Blueprints
    from main.routes import main
    from auth.routes import auth
    from advisor.routes import advisor
    from chatbot.routes import chatbot
    from admin.routes import admin
    
    app.register_blueprint(main)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(advisor, url_prefix='/advisor')
    app.register_blueprint(chatbot, url_prefix='/chat')
    app.register_blueprint(admin)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
