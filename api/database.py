# api/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from .config import settings

# Cliente asíncrono para FastAPI
client = AsyncIOMotorClient(settings.MONGODB_URL)
db = client[settings.DATABASE_NAME]

# Cliente síncrono para operaciones simples en main.py
sync_client = MongoClient(settings.MONGODB_URL)
sync_db = sync_client[settings.DATABASE_NAME]

# Colecciones
vulnerabilities = db.get_collection("vulnerabilities")
groups = db.get_collection("groups")
subgroups = db.get_collection("subgroups")

async def create_indexes():
    """Crea índices para mejorar el rendimiento"""
    try:
        # Índice para CVE (si existe)
        await vulnerabilities.create_index("cve", unique=True, sparse=True)
        
        # Índices para filtros
        await vulnerabilities.create_index("group_id")
        await vulnerabilities.create_index("subgroup_id")
        await vulnerabilities.create_index("cvss_v4")
        
        # Índice de texto para búsqueda
        await vulnerabilities.create_index([
            ("title", "text"),
            ("description", "text")
        ])
        
        print("✓ Índices creados exitosamente")
    except Exception as e:
        print(f"⚠ Advertencia al crear índices: {e}")