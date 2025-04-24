# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置生产环境变量
ENV PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

# 使用阿里云镜像源并安装系统依赖
RUN rm -rf /etc/apt/sources.list.d/* && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm main non-free-firmware contrib" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ bookworm-security main" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ bookworm-updates main non-free-firmware contrib" >> /etc/apt/sources.list && \
    apt-get clean && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 使用阿里云 PyPI 镜像源安装 Python 依赖
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir -r requirements.txt && \
    pip install -i https://mirrors.aliyun.com/pypi/simple/ gunicorn

# 创建数据和日志目录
RUN mkdir -p /app/data /app/logs /app/logs/emails && \
    chmod -R 777 /app/data /app/logs

# 复制启动脚本
COPY start.sh .
RUN chmod +x start.sh

# 复制应用代码
COPY . .

# 创建非 root 用户并设置权限
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["chmod +x start.sh"]

# 启动命令 - 使用启动脚本初始化数据库并启动应用
CMD ["./start.sh"]
