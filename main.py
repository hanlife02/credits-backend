'''
Author: Ethan && ethan@hanlife02.com
Date: 2025-04-24 13:17:39
LastEditors: Ethan && ethan@hanlife02.com
LastEditTime: 2025-04-24 17:10:09
FilePath: /credits-backend/main.py
Description:

Copyright (c) 2025 by Ethan, All Rights Reserved.
'''
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.api_v1.api import api_router
# from app.core.config import settings  # 未使用
from app.api.deps import verify_api_key

from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="毕业学分审查系统",
    description="用于管理毕业学分和要求的API",
    version="1.1.1",
    docs_url=None,  # 禁用默认的 docs 路径
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "首页", "description": "首页重定向"},
        {"name": "健康检查", "description": "API健康状态检查"},
        {"name": "认证", "description": "用户认证和授权"},
        {"name": "用户", "description": "用户管理"},
        {"name": "培养方案", "description": "培养方案管理"},
        {"name": "课程类别", "description": "课程类别管理"},
        {"name": "课程", "description": "课程管理"},
        {"name": "仪表盘", "description": "学分和进度统计"},
    ],
)

# 自定义 Swagger UI 路径
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API 文档 v1.1.1",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
        oauth2_redirect_url=None,
        init_oauth=None,
    )

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS middleware with production settings
from app.core.config import settings

# 从环境变量中获取前端域名
frontend_origins = settings.FRONTEND_ORIGINS.split(",") if settings.FRONTEND_ORIGINS else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    # 限制允许的方法
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    # 限制允许的头部
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# Include API router with API key verification
app.include_router(api_router, prefix="/api/v1", dependencies=[Depends(verify_api_key)])

# Root path redirect to docs
from fastapi.responses import RedirectResponse

@app.get("/", tags=["首页"])
async def root():
    return RedirectResponse(url="/docs")

# 健康检查端点，需要 API 密钥验证
@app.get("/health", tags=["健康检查"], dependencies=[Depends(verify_api_key)])
async def health_check():
    return {
        "status": "ok",
        "message": "API正在运行",
        "version": "1.1.1",
        "api_key_status": "valid"
    }

if __name__ == "__main__":
    # 生产环境配置，移除热重载功能
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,  # 根据服务器CPU核心数调整
        log_level="error"  # 生产环境中只记录错误
    )
