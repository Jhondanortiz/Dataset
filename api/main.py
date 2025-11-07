from fastapi import FastAPI
from .routers import vulnerabilities
from .database import create_indexes

app = FastAPI(title="Dataset Vulnerabilidades 128", version="1.0")

app.include_router(vulnerabilities.router)

@app.on_event("startup")
async def startup():
    await create_indexes()

@app.get("/")
def home():
    return {"status": "API funcionando", "total": 128}