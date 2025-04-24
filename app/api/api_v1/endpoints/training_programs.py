from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_active_admin, get_db
from app.models.user import User
from app.models.training_program import TrainingProgram
from app.schemas.training_program import (
    TrainingProgram as TrainingProgramSchema,
    TrainingProgramCreate,
    TrainingProgramUpdate,
    TrainingProgramPublish,
)

router = APIRouter()


@router.post("/", response_model=TrainingProgramSchema)
def create_training_program(
    training_program_in: TrainingProgramCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    创建新培养方案

    创建一个新的培养方案，包含名称和总学分要求
    """
    training_program = TrainingProgram(
        **training_program_in.model_dump(),
        user_id=current_user.id,
    )
    db.add(training_program)
    db.commit()
    db.refresh(training_program)
    return training_program


@router.get("/", response_model=List[TrainingProgramSchema])
def read_training_programs(
    skip: int = 0,
    limit: int = 100,
    public_only: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    获取培养方案列表

    普通用户：只能看到自己的培养方案和公开的培养方案
    管理员用户：可以看到所有培养方案
    """
    query = db.query(TrainingProgram)

    if not current_user.is_admin:
        # Regular users can only see their own programs and public programs
        query = query.filter(
            (TrainingProgram.user_id == current_user.id) | (TrainingProgram.is_public == True)
        )

    if public_only is not None:
        query = query.filter(TrainingProgram.is_public == public_only)

    training_programs = query.offset(skip).limit(limit).all()
    return training_programs


@router.get("/{training_program_id}", response_model=TrainingProgramSchema)
def read_training_program(
    training_program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    根据ID获取特定培养方案

    获取指定培养方案的详细信息
    """
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培养方案不存在",
        )

    # Check if user has access to this training program
    if not current_user.is_admin and training_program.user_id != current_user.id and not training_program.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )

    return training_program


@router.put("/{training_program_id}", response_model=TrainingProgramSchema)
def update_training_program(
    training_program_id: str,
    training_program_in: TrainingProgramUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    更新培养方案

    根据需求，普通用户不能修改培养方案的课程类别和学分数
    要想修改只能删除原有的并重新创建新的培养方案
    管理员可以更新任何培养方案
    """
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培养方案不存在",
        )

    # Check if user has permission to update this training program
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，普通用户不能修改培养方案，请删除并重新创建",
        )

    # Update fields
    update_data = training_program_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(training_program, field, value)

    db.commit()
    db.refresh(training_program)
    return training_program


@router.delete("/{training_program_id}", response_model=dict)
def delete_training_program(
    training_program_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    删除培养方案

    普通用户只能删除自己的培养方案
    管理员可以删除任何培养方案
    """
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培养方案不存在",
        )

    # Check if user has permission to delete this training program
    if not current_user.is_admin and training_program.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足",
        )

    db.delete(training_program)
    db.commit()
    return {"message": "培养方案删除成功"}


@router.post("/{training_program_id}/publish", response_model=TrainingProgramSchema)
def publish_training_program(
    training_program_id: str,
    publish_data: TrainingProgramPublish,
    # current_user 参数虽然未直接使用，但通过 get_current_active_admin 依赖项确保只有管理员可以访问
    _: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
) -> Any:
    """
    发布或取消发布培养方案（仅管理员）

    管理员可以将培养方案设置为公开或非公开
    """
    training_program = db.query(TrainingProgram).filter(TrainingProgram.id == training_program_id).first()
    if not training_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="培养方案不存在",
        )

    training_program.is_public = publish_data.is_public
    db.commit()
    db.refresh(training_program)
    return training_program
