from pydantic import BaseModel, EmailStr
from datetime import datetime


class VerificationRequest(BaseModel):
    email: EmailStr


class VerificationConfirm(BaseModel):
    email: EmailStr
    code: str
