from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.models.course import GradingSystem


# Shared properties
class CourseBase(BaseModel):
    name: str
    credits: float = Field(..., gt=0)
    grading_system: GradingSystem
    category_id: str


# Properties to receive via API on creation
class CourseCreate(CourseBase):
    grade: Optional[float] = Field(None, ge=0, le=100)
    passed: Optional[bool] = None


# Properties to receive via API on update
class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[float] = Field(None, gt=0)
    grading_system: Optional[GradingSystem] = None
    grade: Optional[float] = Field(None, ge=0, le=100)
    passed: Optional[bool] = None
    category_id: Optional[str] = None


# Properties to return via API
class Course(CourseBase):
    id: str
    user_id: str
    grade: Optional[float] = None
    passed: Optional[bool] = None
    gpa: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
