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
    with open(DESC_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["descriptions"].get(ref, "Sin descripción")

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
        doc["description"] = await load_description(doc["description_ref"])
        result.append(Vulnerability(**doc))
    return result

async def get_vulnerability(id: int):
    doc = await vulnerabilities.find_one({"id": id})
    if doc:
        doc["description"] = await load_description(doc["description_ref"])
        return Vulnerability(**doc)
    return None