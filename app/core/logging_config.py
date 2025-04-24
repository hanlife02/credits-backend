'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 19:30:00
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 19:30:00
FilePath: /credits-backend/app/core/logging_config.py
Description: 日志配置模块

Copyright (c) 2025 by Ethan, All Rights Reserved.
'''
import os
import logging
from logging.handlers import RotatingFileHandler

# 日志目录 - 使用绝对路径指向项目根目录的logs文件夹
import os.path

# 获取当前文件的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 获取项目根目录
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))

# 日志目录设置为项目根目录下的logs文件夹
LOG_DIR = os.path.join(ROOT_DIR, "logs")

# 确保日志目录存在
try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    print(f"日志目录设置为: {LOG_DIR}")
except Exception as e:
    print(f"无法创建日志目录: {e}")

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 配置根日志记录器
def setup_logging():
    """
    配置应用程序日志
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # 清除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 配置日志格式
    formatter = logging.Formatter(LOG_FORMAT)

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    # 尝试添加文件处理器
    try:
        # 确保日志目录存在
        os.makedirs(LOG_DIR, exist_ok=True)

        # 检查文件权限
        log_file = f"{LOG_DIR}/app.log"

        # 尝试创建文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)

        print(f"成功配置日志文件: {log_file}")
    except (IOError, PermissionError) as e:
        # 如果无法创建文件处理器，记录错误但继续运行
        print(f"警告: 无法创建日志文件处理器: {str(e)}")
        print("日志将只输出到控制台")

    # 配置特定模块的日志级别
    logging.getLogger("app.services.email").setLevel(logging.DEBUG)
    logging.getLogger("app.api.api_v1.endpoints.auth").setLevel(logging.DEBUG)

    # 减少一些不必要的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger
