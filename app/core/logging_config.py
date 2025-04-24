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

# 日志目录
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# 配置根日志记录器
def setup_logging():
    """
    配置应用程序日志
    """
    # 创建日志处理器
    file_handler = RotatingFileHandler(
        f"{LOG_DIR}/app.log", 
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    console_handler = logging.StreamHandler()

    # 配置日志格式
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 设置日志级别
    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # 配置特定模块的日志级别
    logging.getLogger("app.services.email").setLevel(logging.DEBUG)
    logging.getLogger("app.api.api_v1.endpoints.auth").setLevel(logging.DEBUG)

    # 减少一些不必要的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger
