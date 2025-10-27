from fastapi import FastAPI
from .routers import vulnerabilities
from . import models, database

app = FastAPI(title="Vulnerabilities API", version="1.0")

# Crear tablas
models.Base.metadata.create_all(bind=database.engine)

app.include_router(vulnerabilities.router)

@app.get("/")
def root():
    return {"message": "API de Vulnerabilidades - CRUD completo"}