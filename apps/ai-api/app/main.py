from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="Singularity Mini KG AI API",
    version="0.1.0",
)

app.include_router(health_router)
