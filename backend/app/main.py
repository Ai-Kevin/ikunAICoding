from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, cases, dashboard, plans, projects
from app.core.config import settings
from app.seed import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AutoTest Pro 自动化测试平台后端 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", tags=["健康检查"])
def root():
    return {"app": settings.PROJECT_NAME, "status": "ok"}


api_prefix = settings.API_V1_PREFIX
app.include_router(auth.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(projects.router, prefix=api_prefix)
app.include_router(cases.router, prefix=api_prefix)
app.include_router(plans.router, prefix=api_prefix)
