from app import create_app
from database.database import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("Attempting to add 'selected_goal' column to users table...")
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN selected_goal VARCHAR(50)"))
            conn.commit()
        print("Success: Column added.")
    except Exception as e:
        print(f"Operation failed (Column might already exist): {e}")
