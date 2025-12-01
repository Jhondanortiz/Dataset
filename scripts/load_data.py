# scripts/load_data.py
import json
import os
from pymongo import MongoClient
from bson import ObjectId

# ===================== CONFIGURACIÓN =====================
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

print("Limpieza completa de la base de datos anterior...")
col_vulns.drop()
col_groups.drop()
col_subgroups.drop()
print("Base de datos limpiada.\n")

def load_json(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(path):
        print(f"ERROR: Archivo no encontrado → {path}")
        exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_data_list(data, data_type="items"):
    """Extrae una lista de datos desde diferentes estructuras JSON"""
    if isinstance(data, list):
        return data
    
    if isinstance(data, dict):
        # Intentar diferentes nombres de claves comunes
        possible_keys = [
            data_type,  # nombre específico (ej: "groups", "subgroups")
            "data",
            "items",
            "records",
            "results"
        ]
        
        for key in possible_keys:
            if key in data:
                if isinstance(data[key], list):
                    return data[key]
        
        # Si no encuentra ninguna clave conocida, devolver los valores del dict
        # Esto maneja casos donde el dict es un mapeo de id -> objeto
        values = list(data.values())
        if values and isinstance(values[0], dict):
            return values
    
    return []

# ===================== CARGA DE GRUPOS =====================
print("Cargando grupos...")
groups_raw = load_json(FILES["groups"])
groups_list = extract_data_list(groups_raw, "groups")

if not groups_list:
    print(f"ERROR: No se pudieron extraer grupos del archivo.")
    print(f"Estructura del archivo: {type(groups_raw)}")
    if isinstance(groups_raw, dict):
        print(f"Claves disponibles: {list(groups_raw.keys())}")
    exit(1)

groups_to_insert = []
for item in groups_list:
    if isinstance(item, dict):
        new_item = {"_id": ObjectId(), **item}
        groups_to_insert.append(new_item)
    else:
        print(f"ADVERTENCIA: Elemento no es un dict: {item}")

if groups_to_insert:
    col_groups.insert_many(groups_to_insert)
    print(f"{len(groups_to_insert)} grupos cargados.")
else:
    print("No se encontraron grupos válidos para cargar.")
    exit(1)

# ===================== CARGA DE SUBGRUPOS =====================
print("Cargando subgrupos...")
subgroups_raw = load_json(FILES["subgroups"])
subgroups_list = extract_data_list(subgroups_raw, "subgroups")

if not subgroups_list:
    print(f"ERROR: No se pudieron extraer subgrupos del archivo.")
    print(f"Estructura del archivo: {type(subgroups_raw)}")
    if isinstance(subgroups_raw, dict):
        print(f"Claves disponibles: {list(subgroups_raw.keys())}")
    exit(1)

subgroups_to_insert = []
for item in subgroups_list:
    if isinstance(item, dict):
        new_item = {"_id": ObjectId(), **item}
        subgroups_to_insert.append(new_item)
    else:
        print(f"ADVERTENCIA: Elemento no es un dict: {item}")

if subgroups_to_insert:
    col_subgroups.insert_many(subgroups_to_insert)
    print(f"{len(subgroups_to_insert)} subgrupos cargados.")
else:
    print("No se encontraron subgrupos válidos para cargar.")
    exit(1)

# ===================== CARGA DE VULNERABILIDADES =====================
print("Cargando vulnerabilidades...")
main_data = load_json(FILES["vulnerabilities"])
vulnerabilities = extract_data_list(main_data, "vulnerabilities")

if not vulnerabilities:
    print("ERROR: No se encontraron vulnerabilidades para cargar.")
    print(f"Estructura del archivo: {type(main_data)}")
    if isinstance(main_data, dict):
        print(f"Claves disponibles: {list(main_data.keys())}")
    exit(1)

for vuln in vulnerabilities:
    if isinstance(vuln, dict):
        vuln["_id"] = ObjectId()
        vuln["group_id"] = int(vuln.get("group_id", 8))
        vuln["subgroup_id"] = int(vuln.get("subgroup_id", 28))

result = col_vulns.insert_many(vulnerabilities)
print(f"{len(result.inserted_ids)} vulnerabilidades cargadas correctamente!")

# ===================== FINAL =====================
total = col_vulns.count_documents({})
print("\n" + "="*60)
print("¡TODO CARGADO PERFECTO! (Sin errores)")
print(f"   • {col_groups.count_documents({})} grupos")
print(f"   • {col_subgroups.count_documents({})} subgrupos")
print(f"   • {total} vulnerabilidades")
print("="*60)
print("Ya puedes iniciar la API:")
print("   uvicorn api.main:app --reload")
print("="*60)

client.close()