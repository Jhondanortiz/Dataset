from .database import vulnerabilities, groups, subgroups
from .models import Vulnerability
import json
from pathlib import Path
import os

DESC_PATH = Path("data/processed/vulnerabilities_descriptions.json")

async def save_description(ref: str, text: str):
    """Guarda descripción en el archivo JSON central"""
    try:
        # Crear directorio si no existe
        DESC_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Inicializar archivo si no existe
        if not DESC_PATH.exists():
            with open(DESC_PATH, "w", encoding="utf-8") as f:
                json.dump({"descriptions": {}}, f, indent=2, ensure_ascii=False)
        
        # Leer, actualizar y guardar
        with open(DESC_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {"descriptions": {}}
        
        # Asegurar que existe la clave "descriptions"
        if "descriptions" not in data:
            data["descriptions"] = {}
        
        data["descriptions"][ref] = text
        
        with open(DESC_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    
    except Exception as e:
        print(f"❌ Error guardando descripción {ref}: {e}")
        return False

async def load_description(ref: str) -> str:
    """Carga descripción desde el archivo JSON central"""
    try:
        # Verificar que el archivo existe
        if not DESC_PATH.exists():
            print(f"⚠️  Archivo de descripciones no existe: {DESC_PATH}")
            return "Sin descripción disponible"
        
        # Verificar que el archivo no está vacío
        if DESC_PATH.stat().st_size == 0:
            print(f"⚠️  Archivo de descripciones está vacío: {DESC_PATH}")
            return "Sin descripción disponible"
        
        # Leer el archivo
        with open(DESC_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Verificar estructura del JSON
        if not isinstance(data, dict):
            print(f"⚠️  Formato inválido en {DESC_PATH}")
            return "Sin descripción disponible"
        
        if "descriptions" not in data:
            print(f"⚠️  Falta clave 'descriptions' en {DESC_PATH}")
            return "Sin descripción disponible"
        
        # Retornar descripción o valor por defecto
        return data["descriptions"].get(ref, "Sin descripción")
    
    except json.JSONDecodeError as e:
        print(f"❌ Error JSON en {DESC_PATH}: {e}")
        return "Error: formato JSON inválido"
    
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {DESC_PATH}")
        return "Sin descripción disponible"
    
    except Exception as e:
        print(f"❌ Error cargando descripción {ref}: {e}")
        return f"Error al cargar descripción"

async def create_vulnerability(vuln: Vulnerability):
    """Crea o actualiza una vulnerabilidad"""
    try:
        ref = f"desc_{vuln.id}"
        
        # Guardar descripción
        await save_description(ref, vuln.description)
        
        # Preparar documento para MongoDB
        vuln_dict = vuln.dict()
        vuln_dict["description_ref"] = ref
        del vuln_dict["description"]
        
        # Insertar o actualizar en MongoDB
        result = await vulnerabilities.update_one(
            {"id": vuln.id}, 
            {"$set": vuln_dict}, 
            upsert=True
        )
        
        return result
    
    except Exception as e:
        print(f"❌ Error creando vulnerabilidad {vuln.id}: {e}")
        raise

async def get_vulnerabilities(skip: int = 0, limit: int = 100):
    """Obtiene lista de vulnerabilidades con paginación"""
    try:
        cursor = vulnerabilities.find().skip(skip).limit(limit).sort("id")
        result = []
        
        async for doc in cursor:
            # Eliminar _id de MongoDB
            doc.pop("_id", None)
            
            # Cargar descripción de forma segura
            description_ref = doc.get("description_ref", f"desc_{doc.get('id', 0)}")
            doc["description"] = await load_description(description_ref)
            
            result.append(doc)
        
        print(f"✅ crud.py: Retornando {len(result)} vulnerabilidades")
        return result
    
    except Exception as e:
        print(f"❌ Error obteniendo vulnerabilidades: {e}")
        return []

async def get_vulnerability(id: int):
    """Obtiene una vulnerabilidad específica por ID"""
    try:
        doc = await vulnerabilities.find_one({"id": id})
        
        if doc:
            doc.pop("_id", None)
            description_ref = doc.get("description_ref", f"desc_{id}")
            doc["description"] = await load_description(description_ref)
            return doc
        
        return None
    
    except Exception as e:
        print(f"❌ Error obteniendo vulnerabilidad {id}: {e}")
        return None

async def get_groups():
    """Obtiene todos los grupos"""
    try:
        cursor = groups.find()
        result = []
        async for doc in cursor:
            doc.pop("_id", None)
            result.append(doc)
        return result
    except Exception as e:
        print(f"❌ Error obteniendo grupos: {e}")
        return []

async def get_subgroups():
    """Obtiene todos los subgrupos"""
    try:
        cursor = subgroups.find()
        result = []
        async for doc in cursor:
            doc.pop("_id", None)
            result.append(doc)
        return result
    except Exception as e:
        print(f"❌ Error obteniendo subgrupos: {e}")
        return []