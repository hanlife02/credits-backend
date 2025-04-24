from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class TrainingProgram(Base):
    __tablename__ = "training_programs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    total_credits = Column(Float, nullable=False)
    is_public = Column(Boolean, default=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    categories = relationship("CourseCategory", back_populates="training_program", cascade="all, delete-orphan")
    user = relationship("User")
