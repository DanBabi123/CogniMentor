from app import create_app
from database.database import db
from database.seed_data import seed_database
import os

if __name__ == "__main__":
    app = create_app()
    print("Resetting Database...")
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("Dropped all tables.")
        
        # Create all tables
        db.create_all()
        print("Created all tables.")
        
        # Seed data
        seed_database()
        print("Database Reset Complete.")
