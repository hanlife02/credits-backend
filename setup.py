import os
import sys
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.base import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.core.config import settings


def setup_db() -> None:
    """Initialize the database with tables and admin user"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if admin user exists
    admin_emails = settings.ADMIN_EMAILS
    for admin_email in admin_emails:
        user = db.query(User).filter(User.email == admin_email).first()
        if not user:
            print(f"Creating admin user: {admin_email}")
            user = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                hashed_password=get_password_hash("admin123"),  # Change this in production
                is_admin=True,
            )
            db.add(user)
    
    db.commit()
    db.close()
    
    print("Database setup complete!")
    print("\nYou can now run the application with:")
    print("python run.py")
    print("\nAPI will be available at http://localhost:8000")
    print("API documentation will be available at http://localhost:8000/docs")


if __name__ == "__main__":
    setup_db()
