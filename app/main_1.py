from fastapi import FastAPI

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