#!/bin/bash
set -e

# 初始化数据库
echo "正在初始化数据库..."
python init_db.py

# 启动应用
echo "启动应用服务器..."
exec gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 4 --log-level error
