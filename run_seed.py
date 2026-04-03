from app import create_app
from database.database import db
from database.seed_data import seed_database
import os

def run():
    app = create_app()
    with app.app_context():
        # Create database within app context
        print("Creating database tables...")
        db.create_all()
        
        # Seed the database
        seed_database()
        print("\nSuccess! Database initialized and seeded.")
        print("Admin Credentials: admin@cogni.com / admin123")

if __name__ == "__main__":
    run()
