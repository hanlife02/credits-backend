from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


# Shared properties
class UserBase(BaseModel):
    email: EmailStr


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


# Properties to receive via API on update
class UserUpdate(BaseModel):
    password: Optional[str] = Field(None, min_length=8)
    default_training_program_id: Optional[str] = None


# Properties to return via API
class User(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    default_training_program_id: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


# Properties for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Token response
class Token(BaseModel):
    access_token: str
    token_type: str


# Token payload
class TokenPayload(BaseModel):
    sub: Optional[str] = None


# Password reset
class PasswordReset(BaseModel):
    email: EmailStr


# Password reset confirmation
class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(..., min_length=8)
