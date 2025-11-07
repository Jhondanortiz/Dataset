# api/crud.py
from .database import collection
from .models import Vulnerability
from typing import List
import json

async def get_vulnerabilities(skip: int = 0, limit: int = 100) -> List[Vulnerability]:
    cursor = collection.find().skip(skip).limit(limit)
    return [Vulnerability(**doc) async for doc in cursor]

async def get_vulnerability_by_id(vuln_id: int) -> Vulnerability:
    doc = await collection.find_one({"id": vuln_id})
    return Vulnerability(**doc) if doc else None

async def create_vulnerability(vuln: Vulnerability) -> Vulnerability:
    result = await collection.insert_one(vuln.dict(by_alias=True))
    return await get_vulnerability_by_id(vuln.id)

async def load_json_data(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data["vulnerabilities"]:
        # Normalizar
        vuln = {
            "id": item["id"],
            "vulnerability_name": item["vulnerability_name"],
            "cve": item["cve"],
            "cvss_v4": item["cvss_v4"],
            "description": item["description"],
            "group": item["group"],
            "subgroup": item["subgroup"],
            "pdf_sources": item["pdf_sources"],
            "related_cves": item.get("related_vulnerabilities", [])
        }
        # Evitar duplicados
        exists = await collection.find_one({"id": vuln["id"]})
        if not exists:
            await collection.insert_one(vuln)
    print("¡Datos cargados en MongoDB!")