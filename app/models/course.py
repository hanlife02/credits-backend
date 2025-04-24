from sqlalchemy import Column, String, Float, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base import Base


class GradingSystem(str, enum.Enum):
    PERCENTAGE = "percentage"
    PASS_FAIL = "pass_fail"


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    credits = Column(Float, nullable=False)
    grading_system = Column(Enum(GradingSystem), nullable=False)
    grade = Column(Float, nullable=True)  # For percentage system
    passed = Column(Boolean, nullable=True)  # For pass/fail system
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    category_id = Column(String, ForeignKey("course_categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    category = relationship("CourseCategory", back_populates="courses")
    
    @property
    def gpa(self):
        """Calculate GPA for this course based on the grade"""
        if self.grading_system == GradingSystem.PERCENTAGE and self.grade is not None:
            # GPA formula: 4 - 3 * (100 - x)^2 / 1600
            return round(4 - 3 * ((100 - self.grade) ** 2) / 1600, 3)
        return None
