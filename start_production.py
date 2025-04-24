#!/usr/bin/env python3
"""
生产环境启动脚本
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import uvicorn

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import engine, Base
from app.core.config import settings
from app.models.user import User
from app.core.security import get_password_hash

# 配置日志
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 创建日志处理器
file_handler = RotatingFileHandler(
    f"{log_dir}/app.log", 
    maxBytes=10485760,  # 10MB
    backupCount=5
)
console_handler = logging.StreamHandler()

# 配置日志格式
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 获取根日志记录器并配置
root_logger = logging.getLogger()
root_logger.setLevel(logging.ERROR)  # 生产环境只记录错误
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

def setup_db():
    """
    设置数据库，创建表并初始化管理员用户
    """
    try:
        # 创建表
        Base.metadata.create_all(bind=engine)
        logging.info("数据库表创建成功")
        
        # 创建会话
        from sqlalchemy.orm import Session
        from app.db.base import SessionLocal
        
        db = SessionLocal()
        
        # 检查是否有管理员用户
        admin_emails = settings.ADMIN_EMAILS.split(",") if "," in settings.ADMIN_EMAILS else [settings.ADMIN_EMAILS]
        
        for admin_email in admin_emails:
            admin_email = admin_email.strip()
            if not admin_email:
                continue
                
            # 检查用户是否存在
            user = db.query(User).filter(User.email == admin_email).first()
            if not user:
                logging.info(f"创建管理员用户: {admin_email}")
                user = User(
                    email=admin_email,
                    hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                    is_active=True,
                    is_admin=True,
                )
                db.add(user)
                db.commit()
        
        db.close()
        logging.info("数据库设置完成")
    except Exception as e:
        logging.error(f"数据库设置失败: {str(e)}")
        raise

def start_app():
    """
    启动应用
    """
    try:
        logging.info("启动生产服务器...")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            workers=4,  # 根据服务器CPU核心数调整
            log_level="error"  # 生产环境中只记录错误
        )
    except Exception as e:
        logging.error(f"服务器启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        setup_db()
        start_app()
    except Exception as e:
        logging.error(f"应用启动失败: {str(e)}")
        sys.exit(1)
