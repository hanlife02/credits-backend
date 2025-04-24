from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class CourseCategory(Base):
    __tablename__ = "course_categories"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    required_credits = Column(Float, nullable=False)
    training_program_id = Column(String, ForeignKey("training_programs.id"), nullable=False)
    parent_id = Column(String, ForeignKey("course_categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    training_program = relationship("TrainingProgram", back_populates="categories")
    parent = relationship("CourseCategory", remote_side=[id], backref="subcategories")
    courses = relationship("Course", back_populates="category", cascade="all, delete-orphan")
