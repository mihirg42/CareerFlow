from fastapi import FastAPI
from app.routers.applications import router

app = FastAPI(
    title="CareerFlow",
    description="Job Application Management Platform",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
