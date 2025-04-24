'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 13:24:41
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 19:51:39
FilePath: /credits-backend/run.py
Description: 

Copyright (c) 2025 by Ethan, All Rights Reserved. 
'''
import uvicorn
import os
import sys

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 创建日志目录
if not os.path.exists("logs"):
    os.makedirs("logs")

if __name__ == "__main__":
    # 先初始化日志配置
    from app.core.logging_config import setup_logging
    logger = setup_logging()
    logger.info("开发服务器启动中...")

    # 启动开发服务器
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
