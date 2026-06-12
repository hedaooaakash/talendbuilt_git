from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.pipeline import router as pipeline_router
from app.routers.pipeline_step import router as pipeline_step_router
from app.routers.connection import router as connection_router
from app.routers.ai import (
    router as ai_router
)

app = FastAPI(
    title="ETL Platform",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "status": "running",
        "product": "ETL Platform"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

app.include_router(auth_router)
app.include_router(pipeline_router)
app.include_router(pipeline_step_router)
app.include_router(connection_router)
app.include_router(ai_router)
