from datetime import timedelta
from typing import Any
import logging

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import authenticate_user, get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.models.user import User
from app.models.verification import VerificationCode
from app.schemas.user import User as UserSchema, UserCreate, Token, PasswordReset, PasswordResetConfirm
from app.schemas.verification import VerificationRequest, VerificationConfirm
from app.services.email import generate_verification_code, send_verification_email, send_password_reset_email

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register/request", response_model=dict)
def register_request(
    verification_request: VerificationRequest,
    db: Session = Depends(get_db),
) -> Any:
    """
    请求注册邮箱验证

    发送验证码到指定邮箱用于注册账户
    """
    try:
        logger.info(f"收到注册验证码请求: {verification_request.email}")

        # Check if user already exists
        user = db.query(User).filter(User.email == verification_request.email).first()
        if user:
            logger.info(f"邮箱已注册: {verification_request.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已经注册",
            )

        # Generate verification code
        code = generate_verification_code()
        logger.info(f"为邮箱 {verification_request.email} 生成验证码")

        # Save verification code to database
        verification = VerificationCode(
            email=verification_request.email,
            code=code,
            purpose="registration",
        )
        db.add(verification)
        db.commit()
        logger.info(f"验证码已保存到数据库: {verification_request.email}")

        # Send verification email
        logger.info(f"尝试发送验证邮件到: {verification_request.email}")
        email_sent = send_verification_email(verification_request.email, code)

        if not email_sent:
            logger.error(f"发送验证邮件失败: {verification_request.email}")
            # 即使邮件发送失败，也不删除数据库中的验证码记录
            # 这样用户可以请求重新发送验证码
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="发送验证邮件失败，请稍后重试或联系管理员",
            )

        logger.info(f"验证邮件发送成功: {verification_request.email}")
        return {"message": "验证码已发送到邮箱"}
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录未预期的错误
        logger.error(f"处理注册验证码请求时发生错误: {str(e)}")
        # 返回通用错误消息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理请求时发生错误，请稍后重试",
        )


@router.post("/register/confirm", response_model=UserSchema)
def register_confirm(
    verification_confirm: VerificationConfirm = None,
    user_create: UserCreate = None,
    email: str = Body(None),
    code: str = Body(None),
    password: str = Body(None),
    db: Session = Depends(get_db),
) -> Any:
    # 支持简化的请求格式
    if verification_confirm is None and email is not None and code is not None:
        verification_confirm = VerificationConfirm(email=email, code=code)

    if user_create is None and email is not None and password is not None:
        user_create = UserCreate(email=email, password=password)

    if verification_confirm is None or user_create is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少必要的参数",
        )
    """
    使用验证码完成注册

    验证邮箱验证码并创建新用户
    """
    # Check if user already exists
    user = db.query(User).filter(User.email == verification_confirm.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已经注册",
        )

    # Verify the code
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == verification_confirm.email,
        VerificationCode.code == verification_confirm.code,
        VerificationCode.purpose == "registration",
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码无效",
        )

    if verification.is_expired:
        db.delete(verification)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期",
        )

    # Create new user
    is_admin = verification_confirm.email in settings.ADMIN_EMAILS
    user = User(
        email=verification_confirm.email,
        hashed_password=get_password_hash(user_create.password),
        is_admin=is_admin,
    )
    db.add(user)

    # Delete verification code
    db.delete(verification)
    db.commit()

    return user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    登录并获取访问令牌

    兼容 OAuth2 的令牌登录，获取用于后续请求的访问令牌
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/password-reset/request", response_model=dict)
def password_reset_request(
    password_reset: PasswordReset,
    db: Session = Depends(get_db),
) -> Any:
    """
    请求重置密码

    发送密码重置验证码到指定邮箱
    """
    try:
        logger.info(f"收到密码重置验证码请求: {password_reset.email}")

        # Check if user exists
        user = db.query(User).filter(User.email == password_reset.email).first()
        if not user:
            # Don't reveal that the user doesn't exist
            logger.info(f"邮箱不存在，但不透露此信息: {password_reset.email}")
            return {"message": "如果邮箱已注册，密码重置验证码已发送"}

        # Generate verification code
        code = generate_verification_code()
        logger.info(f"为邮箱 {password_reset.email} 生成密码重置验证码")

        # Save verification code to database
        verification = VerificationCode(
            email=password_reset.email,
            code=code,
            purpose="password_reset",
        )
        db.add(verification)
        db.commit()
        logger.info(f"密码重置验证码已保存到数据库: {password_reset.email}")

        # Send password reset email
        logger.info(f"尝试发送密码重置邮件到: {password_reset.email}")
        email_sent = send_password_reset_email(password_reset.email, code)

        if not email_sent:
            logger.error(f"发送密码重置邮件失败: {password_reset.email}")
            # 即使邮件发送失败，也不删除数据库中的验证码记录
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="发送密码重置邮件失败，请稍后重试或联系管理员",
            )

        logger.info(f"密码重置邮件发送成功: {password_reset.email}")
        return {"message": "如果邮箱已注册，密码重置验证码已发送"}
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        # 记录未预期的错误
        logger.error(f"处理密码重置验证码请求时发生错误: {str(e)}")
        # 返回通用错误消息
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理请求时发生错误，请稍后重试",
        )


@router.post("/password-reset/confirm", response_model=dict)
def password_reset_confirm(
    password_reset_confirm: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Any:
    """
    使用验证码确认密码重置

    验证密码重置验证码并更新用户密码
    """
    # Check if user exists
    user = db.query(User).filter(User.email == password_reset_confirm.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱或验证码无效",
        )

    # Verify the code
    verification = db.query(VerificationCode).filter(
        VerificationCode.email == password_reset_confirm.email,
        VerificationCode.code == password_reset_confirm.code,
        VerificationCode.purpose == "password_reset",
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱或验证码无效",
        )

    if verification.is_expired:
        db.delete(verification)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码已过期",
        )

    # Update user password
    user.hashed_password = get_password_hash(password_reset_confirm.new_password)

    # Delete verification code
    db.delete(verification)
    db.commit()

    return {"message": "密码重置成功"}
