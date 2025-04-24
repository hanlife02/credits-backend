from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timedelta

from app.db.base import Base


class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, index=True, nullable=False)
    code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # "registration" or "password_reset"
    expires_at = Column(DateTime(timezone=True), nullable=False, 
                        default=lambda: datetime.now() + timedelta(minutes=15))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @property
    def is_expired(self):
        return datetime.now() > self.expires_at
