# from typing import Any  # 未使用
from pydantic_settings import BaseSettings
from pydantic import EmailStr, model_validator


class Settings(BaseSettings):
    # API settings
    API_KEY: str

    # Database settings
    DATABASE_URL: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Email settings
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: EmailStr

    # Admin users
    ADMIN_EMAILS: str = "admin@example.com"

    # Default admin password (used when creating new admin users)
    DEFAULT_ADMIN_PASSWORD: str = "admin123"

    # Frontend origins for CORS
    FRONTEND_ORIGINS: str = "http://localhost:3000"

    @model_validator(mode='after')
    def parse_admin_emails(self) -> 'Settings':
        if isinstance(self.ADMIN_EMAILS, str):
            self.ADMIN_EMAILS = [email.strip() for email in self.ADMIN_EMAILS.split(",") if email.strip()]
        return self

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
