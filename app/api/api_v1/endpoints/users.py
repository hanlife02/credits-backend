from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_admin, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserSchema)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取当前用户信息

    返回当前登录用户的详细信息
    """
    return current_user


@router.put("/me", response_model=UserSchema)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    更新当前用户信息

    更新当前登录用户的信息，如密码
    """
    if user_update.password:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{user_id}", response_model=UserSchema)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
) -> Any:
    """
    根据ID获取特定用户（仅管理员）

    管理员可以根据用户ID查询用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    return user
