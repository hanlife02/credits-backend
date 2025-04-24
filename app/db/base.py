'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 13:17:59
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 13:28:30
FilePath: /credits-backend/app/db/base.py
Description:

Copyright (c) 2025 by Ethan, All Rights Reserved.
'''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Enable foreign key constraints for SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
