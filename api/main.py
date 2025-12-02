# api/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os

# Routers
from .routers import vulnerabilities

# Database & indexes
from .database import create_indexes

app = FastAPI(
    title="VulneraDB - Dataset de 128 Vulnerabilidades Críticas",
    description="API REST completa con filtros por grupo, subgrupo, CVSS, año, búsqueda full-text y más",
    version="2.0",
    contact={"name": "Daniel Crack", "email": "tuemail@estudiante.com"}
)

# ===================== CORS =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en producción, usar dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== CONEXIÓN A MONGODB =====================
client = MongoClient("mongodb://localhost:27017/")
db = client["vulnerabilities_db"]
col_groups = db["groups"]
col_subgroups = db["subgroups"]

# ===================== INCLUSIÓN ROUTERS =====================
app.include_router(
    vulnerabilities.router, 
    prefix="/api/vulnerabilities",
    tags=["Vulnerabilidades"]
)

# ===================== STARTUP =====================
@app.on_event("startup")
async def startup_event():
    await create_indexes()
    print("Índices creados correctamente")
    print("API VulneraDB iniciada - ¡Listo para dominar el proyecto!")

# ===================== ROOT =====================
@app.get("/")
async def root():
    total = db.vulnerabilities.count_documents({})
    return {
        "message": "API VulneraDB activa y funcionando al 100%",
        "total_vulnerabilidades": total,
        "endpoints_disponibles": [
            "/docs",
            "/api/vulnerabilities",
            "/api/groups",
            "/api/subgroups",
            "/api/subgroups/bygroup/{group_id}"
        ]
    }

# ===================== GRUPOS =====================
@app.get("/api/groups")
async def get_groups():
    """
    Devuelve todos los grupos.
    """
    groups = list(col_groups.find({}, {"_id": 0}).sort("id", 1))
    return {"groups": groups}

# ===================== SUBGRUPOS =====================
@app.get("/api/subgroups")
async def get_all_subgroups():
    """
    Devuelve todos los subgrupos.
    """
    subs = list(col_subgroups.find({}, {"_id": 0}).sort("id", 1))
    return {"subgroups": subs}

@app.get("/api/subgroups/bygroup/{group_id}")
async def get_subgroups_by_group(group_id: int):
    """
    Devuelve subgrupos que pertenecen al grupo indicado.

    IMPORTANTE:
    En tu JSON, el campo se llama "group", NO "group_id".
    """
    subs = list(col_subgroups.find({"group": group_id}, {"_id": 0}).sort("id", 1))

    if not subs:
        return {"subgroups": []}  # evitar 404 para permitir render seguro

    return {"subgroups": subs}

# ===================== ESTADÍSTICAS =====================
@app.get("/api/stats")
async def get_stats():
    total = db.vulnerabilities.count_documents({})
    critical = db.vulnerabilities.count_documents({"cvss_v4": {"$gte": 9.0}})
    high = db.vulnerabilities.count_documents({"cvss_v4": {"$gte": 7.0, "$lt": 9.0}})

    top_group = list(db.vulnerabilities.aggregate([
        {"$group": {"_id": "$group_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 1}
    ]))

    top_name = "Desconocido"
    if top_group:
        g = col_groups.find_one({"id": top_group[0]["_id"]})
        if g:
            top_name = g["description"]  # tus grupos NO tienen "name"

    return {
        "total_vulnerabilidades": total,
        "criticas": critical,
        "altas": high,
        "grupo_mas_afectado": top_name,
        "grupo_cantidad": top_group[0]["count"] if top_group else 0
    }

# ===================== SHUTDOWN =====================
@app.on_event("shutdown")
def shutdown_event():
    client.close()
    print("Conexión a MongoDB cerrada.")
