'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 13:19:36
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 15:15:26
FilePath: /credits-backend/app/api/deps.py
Description: 

Copyright (c) 2025 by Ethan, All Rights Reserved. 
'''
from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import verify_password
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

# OAuth2 scheme for JWT token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="请输入您的 API 密钥")


def verify_api_key(api_key: str = Security(api_key_header)) -> None:
    """
    验证 API 密钥是否有效
    """
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无效的API密钥",
        )


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    从令牌中获取当前用户
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活",
        )
    return user


def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前用户并验证其是否为管理员
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足（非管理员用户）",
        )
    return current_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    通过邮箱和密码验证用户
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
