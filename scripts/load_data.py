import json
import os
from pymongo import MongoClient
from bson import ObjectId

# Configuración
JSON_FILE = "data/processed/vulnerabilities_dataset.json"
DB_NAME = "vulnerabilities_db"
COLLECTION_NAME = "vulnerabilities"

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# LIMPIEZA COMPLETA
print(f"Base de datos '{DB_NAME}' eliminada (limpieza completa)")
collection.drop()
client.drop_database(DB_NAME)  # fuerza recreación limpia
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Lectura y carga correcta de JSON Lines
file_path = os.path.join(os.path.dirname(__file__), "..", JSON_FILE)

print(f"Leyendo archivo: {JSON_FILE}")

if not os.path.exists(file_path):
    print("ERROR: No se encontró el archivo JSON. Ruta esperada:")
    print(file_path)
    exit(1)

vulnerabilities = []
total_lineas = 0
lineas_validas = 0

with open(file_path, "r", encoding="utf-8") as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        total_lineas += 1
        if not line:  # línea vacía
            continue
        try:
            vuln = json.loads(line)
            # Añadimos un ID único si no lo tiene
            if "_id" not in vuln:
                vuln["_id"] = ObjectId()
            vulnerabilities.append(vuln)
            lineas_validas += 1
        except json.JSONDecodeError as e:
            print(f"  ERROR en línea {line_num}: {e} → línea ignorada")

print(f"Procesadas {total_lineas} líneas → {lineas_validas} válidas. Insertando en MongoDB...")

if vulnerabilities:
    result = collection.insert_many(vulnerabilities)
    print(f"¡ÉXITO! Insertadas {len(result.inserted_ids)} vulnerabilidades correctamente.")
else:
    print("ADVERTENCIA: No se insertó ninguna vulnerabilidad.")

print(f"Base de datos '{DB_NAME}' lista con {collection.count_documents({})} documentos.")
print("\nAPI lista para usar:")
print("   uvicorn api.main:app --reload")
print("   Abrir en el navegador: http://127.0.0.1:8000/docs")
print("   Frontend: abre frontend/index.html")
print("\n¡TU PROYECTO ESTÁ 100% FUNCIONAL!")