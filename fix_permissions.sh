#!/bin/bash
# 修复日志目录权限的脚本

# 创建日志目录（如果不存在）
mkdir -p ./logs
mkdir -p ./logs/emails

# 设置权限为777（所有用户可读写执行）
chmod -R 777 ./logs

echo "日志目录权限已修复"

# 重启容器
docker-compose down
docker-compose up -d

echo "容器已重启"

# 检查容器状态
docker-compose ps

echo "完成！"
