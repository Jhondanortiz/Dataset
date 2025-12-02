# scripts/load_data.py

import json
import os
from pymongo import MongoClient
from bson import ObjectId

# =================== CONFIGURACIÓN ===================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")

FILES = {
    "vulnerabilities": "vulnerabilities_dataset.json",
    "groups": "vulnerabilities_dataset_groups.json",
    "subgroups": "vulnerabilities_dataset_subgroups.json"
}

client = MongoClient("mongodb://localhost:27017/")
db = client["vulnerabilities_db"]

col_vulns = db["vulnerabilities"]
col_groups = db["groups"]
col_subgroups = db["subgroups"]

print("🧹 Limpiando colecciones anteriores...")
col_vulns.drop()
col_groups.drop()
col_subgroups.drop()
print("✔ Base de datos reiniciada.\n")


# =================== UTILIDADES ===================

def load_json(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        raise Exception(f"Archivo no encontrado: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_list(data):
    """Extrae una lista desde varios posibles formatos JSON."""
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["groups", "subgroups", "vulnerabilities", "items", "data", "records"]:
            if key in data and isinstance(data[key], list):
                return data[key]

    raise Exception("El archivo NO contiene una lista válida.")


# =================== CARGA DE GRUPOS ===================

print("📥 Cargando grupos...")
groups_raw = load_json(FILES["groups"])
groups_list = extract_list(groups_raw)

groups_to_insert = []
for g in groups_list:
    groups_to_insert.append({
        "_id": ObjectId(),
        "id": int(g["id"]),
        "name": g["name"]   # CORRECTO SEGÚN TU JSON
    })

col_groups.insert_many(groups_to_insert)
print(f"✔ {len(groups_to_insert)} grupos cargados.\n")


# =================== CARGA DE SUBGRUPOS ===================

print("📥 Cargando subgrupos...")
subgroups_raw = load_json(FILES["subgroups"])
subgroups_list = extract_list(subgroups_raw)

subgroups_to_insert = []
for s in subgroups_list:
    subgroups_to_insert.append({
        "_id": ObjectId(),
        "id": int(s["id"]),
        "group_id": int(s["group_id"]),  # CORRECTO SEGÚN TU JSON
        "name": s["description"]         # CORRECTO SEGÚN TU JSON
    })

col_subgroups.insert_many(subgroups_to_insert)
print(f"✔ {len(subgroups_to_insert)} subgrupos cargados.\n")


# =================== CARGA DE VULNERABILIDADES ===================

print("📥 Cargando vulnerabilidades...")
vuln_raw = load_json(FILES["vulnerabilities"])
vuln_list = extract_list(vuln_raw)

vulns_to_insert = []
for v in vuln_list:
    group_val = v.get("group") or v.get("group_id")
    sub_val = v.get("subgroup") or v.get("subgroup_id")

    vulns_to_insert.append({
        "_id": ObjectId(),
        **v,
        "group_id": int(group_val) if group_val not in [None, ""] else 0,
        "subgroup_id": int(sub_val) if sub_val not in [None, ""] else 0
    })


col_vulns.insert_many(vulns_to_insert)
print(f"✔ {len(vulns_to_insert)} vulnerabilidades cargadas.\n")


# =================== FINAL ===================

print("=" * 60)
print("📌 CARGA COMPLETA SIN ERRORES")
print(f"• {col_groups.count_documents({})} grupos")
print(f"• {col_subgroups.count_documents({})} subgrupos")
print(f"• {col_vulns.count_documents({})} vulnerabilidades")
print("=" * 60)
print("Ejecuta ahora:")
print("   uvicorn api.main:app --reload")
print("=" * 60)

client.close()
