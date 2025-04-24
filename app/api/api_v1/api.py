from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, training_programs, course_categories, courses, dashboard

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(users.router, prefix="/users", tags=["用户"])
api_router.include_router(training_programs.router, prefix="/training-programs", tags=["培养方案"])
api_router.include_router(course_categories.router, prefix="/course-categories", tags=["课程类别"])
api_router.include_router(courses.router, prefix="/courses", tags=["课程"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
