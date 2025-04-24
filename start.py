'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 13:36:42
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 14:13:52
FilePath: /credits-backend/start.py
Description:

Copyright (c) 2025 by Ethan, All Rights Reserved.
'''
import os
import sys
import uuid
import secrets
from dotenv import load_dotenv

# Check if .env file exists, if not create it
if not os.path.exists(".env"):
    print("Creating .env file...")
    with open(".env.example", "r") as example_file:
        example_content = example_file.read()

    # Generate a secure random API key and secret key
    api_key = secrets.token_hex(32)
    secret_key = secrets.token_hex(32)

    # Replace placeholders with generated values
    env_content = example_content.replace("your-api-key-here", api_key)
    env_content = env_content.replace("your-secret-key-here", secret_key)

    with open(".env", "w") as env_file:
        env_file.write(env_content)

    print("Created .env file with random API key and secret key")

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
    admin_email = settings.ADMIN_EMAILS
    if isinstance(admin_email, list):
        admin_emails = admin_email
    else:
        admin_emails = [admin_email]

    for admin_email in admin_emails:
        user = db.query(User).filter(User.email == admin_email).first()
        if not user:
            print(f"Creating admin user: {admin_email}")
            user = User(
                id=str(uuid.uuid4()),
                email=admin_email,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                is_admin=True,
            )
            db.add(user)

    db.commit()
    db.close()

    print("Database setup complete!")


def start_app():
    """Start the application"""
    import uvicorn
    print("\nStarting the application...")
    print("API will be available at http://localhost:8000")
    print("API documentation will be available at http://localhost:8000/docs")
    print("\nDefault admin credentials:")
    admin_email = settings.ADMIN_EMAILS
    if isinstance(admin_email, list) and admin_email:
        display_email = admin_email[0]
    else:
        display_email = admin_email if isinstance(admin_email, str) else 'admin@example.com'
    print(f"Email: {display_email}")
    print(f"Password: {settings.DEFAULT_ADMIN_PASSWORD}")
    print("\nPress Ctrl+C to stop the server")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    setup_db()
    start_app()
