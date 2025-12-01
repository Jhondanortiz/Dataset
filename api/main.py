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

# ===================== CORS (para que el frontend funcione desde cualquier lado) =====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],              # En producción cambia a tu dominio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== CONEXIÓN DIRECTA A MONGODB (para endpoints de grupos/subgrupos) =====================
client = MongoClient("mongodb://localhost:27017/")
db = client["vulnerabilities_db"]
col_groups = db["groups"]
col_subgroups = db["subgroups"]

# ===================== INCLUSIÓN DE ROUTERS =====================
app.include_router(vulnerabilities.router, prefix="/api/vulnerabilities", tags=["Vulnerabilidades"])

# ===================== EVENTO DE INICIO =====================
@app.on_event("startup")
async def startup_event():
    await create_indexes()
    print("Índices creados correctamente")
    print("API VulneraDB iniciada - ¡Listo para dominar el proyecto!")

# ===================== ENDPOINTS PRINCIPALES =====================
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
            "/api/subgroups/{group_id}"
        ]
    }

# ===================== ENDPOINTS DE GRUPOS Y SUBGRUPOS (¡LOS QUE TE FALTABAN!) =====================
@app.get("/api/groups")
async def get_groups():
    """Devuelve todos los grupos (para el select principal del frontend)"""
    groups = list(col_groups.find({}, {"_id": 0}).sort("id", 1))
    return {"groups": groups}


@app.get("/api/subgroups")
async def get_all_subgroups():
    """Devuelve todos los subgrupos (útil para estadísticas o carga inicial)"""
    subgroups = list(col_subgroups.find({}, {"_id": 0}).sort("id", 1))
    return {"subgroups": subgroups}


@app.get("/api/subgroups/{group_id}")
async def get_subgroups_by_group(group_id: int):
    """Devuelve solo los subgrupos de un grupo seleccionado (filtros en cascada)"""
    subgroups = list(col_subgroups.find({"group_id": group_id}, {"_id": 0}).sort("id", 1))
    if not subgroups:
        raise HTTPException(status_code=404, detail="No se encontraron subgrupos para este grupo")
    return {"subgroups": subgroups}


# ===================== ESTADÍSTICAS RÁPIDAS (bonus para el frontend) =====================
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
        group_doc = col_groups.find_one({"id": top_group[0]["_id"]})
        top_name = group_doc["name"] if group_doc else "Otro"

    return {
        "total_vulnerabilidades": total,
        "criticas": critical,
        "altas": high,
        "grupo_mas_afectado": top_name,
        "grupo_cantidad": top_group[0]["count"] if top_group else 0
    }

# ===================== CIERRE DE CONEXIÓN (opcional, FastAPI lo maneja bien) =====================
@app.on_event("shutdown")
def shutdown_event():
    client.close()
    print("Conexión a MongoDB cerrada.")