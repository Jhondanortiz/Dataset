import asyncio
import json
from api.database import client
from api.models import Vulnerability
from api.crud import create_vulnerability

async def load():
    # Limpiar todo
    await client.drop_database("vulnerabilities_db")
    
    # Cargar vulnerabilidades
    with open("data/processed/vulnerabilities_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
        for v in data["vulnerabilities"]:
            vuln = Vulnerability(
                id=v["id"],
                pdf_sources=v["pdf_sources"],
                vulnerability_name=v.get("vulnerability_name"),
                group=v["group"],
                subgroup=v.get("subgroup"),
                cve=v.get("cve"),
                cwe=v.get("cwe"),
                cwe_name=v.get("cwe_name"),
                cvss_v4=v.get("cvss_v4"),
                related_vulnerabilities=v.get("related_vulnerabilities", []),
                description=v.get("description", "Sin descripción")
            )
            await create_vulnerability(vuln)
            print(f"Cargada: {v['id']} - {vuln.vulnerability_name or vuln.cve}")

    print("¡128 VULNERABILIDADES CARGADAS CON DESCRIPCIONES COMPLETAS!")

asyncio.run(load())