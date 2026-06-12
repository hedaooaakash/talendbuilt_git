from fastapi import FastAPI
from app.routers.auth import router as auth_router

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