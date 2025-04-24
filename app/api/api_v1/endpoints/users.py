from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_admin, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.training_program import TrainingProgram
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()


@router.post("/me/default-training-program/{training_program_id}", response_model=Dict[str, str])
def set_default_training_program(
    training_program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    设置默认培养方案

    设置用户的默认培养方案，以便在仪表盘中自动显示
    """
    # 检查培养方案是否存在
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培养方案不存在",
        )

    # 检查用户是否有权限访问该培养方案
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )

    # 设置默认培养方案
    current_user.default_training_program_id = training_program_id
    db.commit()
    db.refresh(current_user)

    return {"message": "默认培养方案设置成功"}


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
