from .database import vulnerabilities, groups, subgroups
from .models import Vulnerability
import json
from pathlib import Path

DESC_PATH = Path("data/processed/vulnerabilities_descriptions.json")

async def save_description(ref: str, text: str):
    with open(DESC_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["descriptions"][ref] = text
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

async def load_description(ref: str) -> str:
    try:
        with open(DESC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["descriptions"].get(ref, "Sin descripción")
    except FileNotFoundError:
        return "Sin descripción"

async def create_vulnerability(vuln: Vulnerability):
    ref = f"desc_{vuln.id}"
    await save_description(ref, vuln.description)
    vuln_dict = vuln.dict()
    vuln_dict["description_ref"] = ref
    del vuln_dict["description"]
    await vulnerabilities.update_one({"id": vuln.id}, {"$set": vuln_dict}, upsert=True)

async def get_vulnerabilities(skip: int = 0, limit: int = 100):
    cursor = vulnerabilities.find().skip(skip).limit(limit).sort("id")
    result = []
    async for doc in cursor:
        # Eliminar _id de MongoDB que causa problemas
        doc.pop("_id", None)
        
        # Cargar descripción
        description_ref = doc.get("description_ref", f"desc_{doc.get('id')}")
        doc["description"] = await load_description(description_ref)
        
        # Agregar como diccionario directamente
        result.append(doc)
    
    print(f"🔍 DEBUG crud.py: Se encontraron {len(result)} vulnerabilidades")
    return result

async def get_vulnerability(id: int):
    doc = await vulnerabilities.find_one({"id": id})
    if doc:
        doc.pop("_id", None)
        description_ref = doc.get("description_ref", f"desc_{id}")
        doc["description"] = await load_description(description_ref)
        return doc
    return None