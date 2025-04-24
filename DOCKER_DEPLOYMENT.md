# Docker 部署指南

本文档提供了使用 Docker 和 Docker Compose 部署毕业学分审查系统的详细说明。

## 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)
- 基本的 Docker 和命令行知识

## 部署步骤

### 1. 准备环境变量

复制 `.env.example` 文件到 `.env`：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写实际的配置值：

```bash
# 数据库设置
DATABASE_URL=sqlite:///./data/credits.db

# 安全设置
SECRET_KEY=your-secure-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 邮件设置
SMTP_HOST=smtp.your-email-provider.com
SMTP_PORT=465
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
FROM_EMAIL=your-email@example.com

# API 密钥
API_KEY=your-secure-api-key

# 管理员用户
ADMIN_EMAILS=admin@your-domain.com

# 默认管理员密码
DEFAULT_ADMIN_PASSWORD=your-secure-admin-password

# 前端域名（用于 CORS）
FRONTEND_ORIGINS=https://your-frontend-domain.com,https://www.your-frontend-domain.com
```

### 2. 构建和启动容器

使用 Docker Compose 构建和启动容器：

```bash
# 构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

这将在后台启动 API 服务。

### 3. 验证部署

检查容器是否正在运行：

```bash
docker-compose ps
```

检查 API 健康状态：

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/health
```

### 4. 查看日志

```bash
# 查看实时日志
docker-compose logs -f api

# 查看最近 100 行日志
docker-compose logs --tail=100 api
```

### 5. 停止和重启服务

```bash
# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并移除容器（保留数据卷）
docker-compose down
```

## 使用 PostgreSQL 数据库（可选）

如果您想使用 PostgreSQL 而不是 SQLite，请按照以下步骤操作：

1. 取消注释 `docker-compose.yml` 文件中的 `db` 服务部分
2. 在 `.env` 文件中添加以下变量：

```bash
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_NAME=credits
```

3. 更新 `DATABASE_URL` 变量：

```bash
DATABASE_URL=postgresql://postgres:your-secure-password@db:5432/credits
```

4. 重新启动服务：

```bash
docker-compose down
docker-compose up -d
```

## 生产环境注意事项

1. **安全性**：

   - 使用强密码和 API 密钥
   - 限制 Docker 容器的资源使用
   - 定期更新 Docker 镜像和依赖项

2. **备份**：

   - 定期备份数据卷：`docker volume backup credits-data`
   - 如果使用 PostgreSQL，设置定期数据库备份

3. **监控**：

   - 使用 Docker 的健康检查功能
   - 考虑设置容器监控工具（如 Prometheus + Grafana）

4. **扩展**：
   - 对于高负载场景，考虑使用 Docker Swarm 或 Kubernetes 进行扩展

## 故障排除

1. **容器无法启动**：

   - 检查 Docker 日志：`docker-compose logs api`
   - 验证环境变量是否正确设置

2. **API 无法访问**：

   - 检查端口映射：`docker-compose ps`
   - 确认防火墙设置允许访问端口 8000

3. **数据库连接问题**：
   - 如果使用 PostgreSQL，确保数据库容器已启动
   - 验证 `DATABASE_URL` 是否正确

## 更新应用

要更新应用到新版本，请按照以下步骤操作：

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重新启动容器
docker-compose up -d
```
