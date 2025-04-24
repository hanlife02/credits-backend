from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# Shared properties
class TrainingProgramBase(BaseModel):
    name: str
    total_credits: float = Field(..., gt=0)


# Properties to receive via API on creation
class TrainingProgramCreate(TrainingProgramBase):
    pass


# Properties to receive via API on update
class TrainingProgramUpdate(BaseModel):
    name: Optional[str] = None
    total_credits: Optional[float] = Field(None, gt=0)
    is_public: Optional[bool] = None


# Properties to return via API
class TrainingProgram(TrainingProgramBase):
    id: str
    is_public: bool
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Properties for publishing a training program
class TrainingProgramPublish(BaseModel):
    is_public: bool = True
