from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# Shared properties
class CourseCategoryBase(BaseModel):
    name: str
    required_credits: float = Field(..., ge=0)
    parent_id: Optional[str] = None


# Properties to receive via API on creation
class CourseCategoryCreate(CourseCategoryBase):
    training_program_id: str


# Properties to receive via API on update
class CourseCategoryUpdate(BaseModel):
    name: Optional[str] = None
    required_credits: Optional[float] = Field(None, ge=0)


# Properties to return via API
class CourseCategory(CourseCategoryBase):
    id: str
    training_program_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True


# Recursive model for nested categories
class CourseCategoryWithChildren(CourseCategory):
    subcategories: List['CourseCategoryWithChildren'] = []

    class Config:
        orm_mode = True
        from_attributes = True


# Complete the recursive reference
CourseCategoryWithChildren.model_rebuild()
