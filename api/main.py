# api/main.py
from fastapi import FastAPI
from .routers import vulnerabilities
from . import crud
import asyncio

app = FastAPI(title="Vulnerabilities API - MongoDB", version="1.0")

app.include_router(vulnerabilities.router)

@app.on_event("startup")
async def startup_event():
    # Cargar datos al iniciar (opcional)
    await crud.load_json_data("data/processed/vulnerabilities_full.json")

@app.get("/")
def root():
    return {"message": "API MongoDB - 128 vulnerabilidades listas"}