from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import vulnerabilities
from .database import create_indexes

app = FastAPI(title="Dataset Vulnerabilidades 128", version="1.0")

# ⭐ AGREGAR CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vulnerabilities.router)

@app.on_event("startup")
async def startup():
    await create_indexes()

@app.get("/")
def home():
    return {"status": "API funcionando", "total": 128}