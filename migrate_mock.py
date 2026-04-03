from app import create_app
from database.database import db

app = create_app()
with app.app_context():
    print("Migrating MockTestProgress table...")
    db.create_all()
    print("Migration complete!")
