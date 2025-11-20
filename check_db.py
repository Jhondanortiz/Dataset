import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def check():
    # Usa la misma URI que tienes en database.py
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["vulnerabilities_db"]  # Cambia por tu nombre de BD
    
    count = await db.vulnerabilities.count_documents({})
    print(f"📊 Total de documentos en MongoDB: {count}")
    
    if count > 0:
        cursor = db.vulnerabilities.find().limit(3)
        print("\n📄 Primeros 3 documentos:")
        async for doc in cursor:
            print(f"  - ID: {doc.get('id')}, CVE: {doc.get('cve')}, Nombre: {doc.get('vulnerability_name')}")
    else:
        print("⚠️ La colección está vacía. Necesitas cargar datos primero.")

asyncio.run(check())