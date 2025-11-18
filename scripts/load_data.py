# scripts/load_data.py
import asyncio
import json
from pathlib import Path
import sys

# Añadimos la carpeta raíz del proyecto al path (para que encuentre 'api')
sys.path.append(str(Path(__file__).parent.parent))

from api.database import client
from api.models import Vulnerability
from api.crud import create_vulnerability


async def load():
    # Limpiamos la base de datos anterior
    await client.drop_database("vulnerabilities_db")
    print("Base de datos 'vulnerabilities_db' eliminada (limpieza completa)\n")

    file_path = Path("data/processed/vulnerabilities_dataset.json")

    # Verificamos que el archivo exista
    if not file_path.exists():
        print(f"ERROR: No se encontró el archivo:\n   {file_path.resolve()}")
        print("   Asegúrate de tener 'vulnerabilities_dataset.json' en la carpeta data/processed/")
        return

    print(f"Leyendo archivo: {file_path}\n")

    try:
        raw = file_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: El archivo JSON está mal formado → {e}")
        print("Primeros 300 caracteres del archivo:")
        print(repr(raw[:300]))
        return
    except Exception as e:
        print(f"Error inesperado al leer el archivo: {e}")
        return

    # Extraemos la lista de vulnerabilidades (con o sin metadata)
    if "vulnerabilities" in data:
        vulnerabilities = data["vulnerabilities"]
    elif isinstance(data, list):
        vulnerabilities = data
    else:
        print("ERROR: No se encontró la clave 'vulnerabilities' ni una lista válida.")
        print("Claves encontradas en el JSON:", list(data.keys()))
        return

    total = len(vulnerabilities)
    if total == 0:
        print("ADVERTENCIA: El archivo JSON está vacío o no tiene vulnerabilidades.")
        return

    print(f"Encontradas {total} vulnerabilidades. Iniciando carga en MongoDB...\n")

    for idx, v in enumerate(vulnerabilities, start=1):
        try:
            # Aseguramos que id y group sean enteros
            vuln_id = int(v["id"])
            group_id = int(v["group"])

            vuln = Vulnerability(
                id=vuln_id,
                pdf_sources=v.get("pdf_sources", []),
                vulnerability_name=v.get("vulnerability_name"),
                group=group_id,
                subgroup=v.get("subgroup"),  # puede ser None o int
                cve=v.get("cve"),
                cwe=v.get("cwe"),
                cwe_name=v.get("cwe_name"),
                cvss_v4=v.get("cvss_v4"),
                related_vulnerabilities=v.get("related_vulnerabilities", []),
                description=v.get("description", "Sin descripción disponible").strip()
            )

            await create_vulnerability(vuln)

            nombre = vuln.vulnerability_name or vuln.cve or "Sin nombre"
            print(f"  {idx:3d}/128  →  ID {vuln_id:3d}  |  {nombre[:55]:55}")

        except Exception as e:
            print(f"  ERROR en posición {idx} (ID {v.get('id', '??')}): {e}")

    print("\nTODAS LAS VULNERABILIDADES HAN SIDO CARGADAS CORRECTAMENTE!")
    print("API lista para usar:")
    print("   uvicorn api.main:app --reload")
    print("   Abrir en el navegador: http://127.0.0.1:8000/docs")
    print("\n¡Tu proyecto ya está 100% funcional!")


# Ejecutar solo si se llama directamente
if __name__ == "__main__":
    asyncio.run(load())