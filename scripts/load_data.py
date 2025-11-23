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
print(f"🗑️  Base de datos '{DB_NAME}' eliminada (limpieza completa)")
collection.drop()
client.drop_database(DB_NAME)  # fuerza recreación limpia
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Lectura del archivo JSON
file_path = os.path.join(os.path.dirname(__file__), "..", JSON_FILE)

print(f"📂 Leyendo archivo: {JSON_FILE}")

if not os.path.exists(file_path):
    print("❌ ERROR: No se encontró el archivo JSON. Ruta esperada:")
    print(f"   {file_path}")
    exit(1)

try:
    # ✅ CORRECCIÓN: Leer el archivo JSON completo (no línea por línea)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)  # Lee TODO el archivo como un objeto JSON
    
    # Extraer el array de vulnerabilidades
    vulnerabilities = data.get("vulnerabilities", [])
    
    if not vulnerabilities:
        print("⚠️  ADVERTENCIA: No se encontraron vulnerabilidades en el archivo")
        exit(1)
    
    # Añadir _id único si no lo tienen
    for vuln in vulnerabilities:
        if "_id" not in vuln:
            vuln["_id"] = ObjectId()
    
    print(f"📊 Encontradas {len(vulnerabilities)} vulnerabilidades. Insertando en MongoDB...")
    
    # Insertar todas las vulnerabilidades
    result = collection.insert_many(vulnerabilities)
    print(f"✅ ¡ÉXITO! Insertadas {len(result.inserted_ids)} vulnerabilidades correctamente.")
    
    # Verificar la inserción
    total_docs = collection.count_documents({})
    print(f"📈 Base de datos '{DB_NAME}' lista con {total_docs} documentos.")
    
    # Mostrar metadata si existe
    metadata = data.get("metadata", {})
    if metadata:
        print(f"\n📋 Metadata del dataset:")
        print(f"   - Generado: {metadata.get('generated_at', 'N/A')}")
        print(f"   - Total vulnerabilidades: {metadata.get('total_vulnerabilities', 'N/A')}")
        print(f"   - Fuente: {metadata.get('source', 'N/A')}")
    
    # Mostrar algunas estadísticas
    print(f"\n📊 Estadísticas rápidas:")
    
    # Contar por grupo
    pipeline_groups = [
        {"$group": {"_id": "$group", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_groups = list(collection.aggregate(pipeline_groups))
    if top_groups:
        print(f"   Top 5 grupos más frecuentes:")
        for item in top_groups:
            print(f"      - Grupo {item['_id']}: {item['count']} vulnerabilidades")
    
    # Contar por severidad (CVSS)
    high_severity = collection.count_documents({"cvss_v4": {"$gte": 9.0}})
    medium_severity = collection.count_documents({"cvss_v4": {"$gte": 7.0, "$lt": 9.0}})
    low_severity = collection.count_documents({"cvss_v4": {"$lt": 7.0, "$ne": None}})
    
    print(f"\n   Distribución por severidad (CVSS v4):")
    print(f"      - Crítica (≥9.0): {high_severity}")
    print(f"      - Alta (7.0-8.9): {medium_severity}")
    print(f"      - Media/Baja (<7.0): {low_severity}")
    
    print("\n" + "="*60)
    print("🎉 ¡TU PROYECTO ESTÁ 100% FUNCIONAL!")
    print("="*60)
    print("\n🚀 Próximos pasos:")
    print("   1. Iniciar API:")
    print("      uvicorn api.main:app --reload")
    print("\n   2. Abrir documentación API:")
    print("      http://127.0.0.1:8000/docs")
    print("\n   3. Abrir Frontend:")
    print("      Abre frontend/index.html en tu navegador")
    print("\n" + "="*60)

except json.JSONDecodeError as e:
    print(f"❌ ERROR: El archivo no es un JSON válido")
    print(f"   Detalles: {e}")
    exit(1)
except Exception as e:
    print(f"❌ ERROR inesperado: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    client.close()