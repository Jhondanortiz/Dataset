# api/routers/vulnerabilities.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from ..models import Vulnerability
from ..crud import get_vulnerabilities, get_vulnerability

router = APIRouter()

@router.get("/", response_model=List[Dict[str, Any]])
async def read_all(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    q: Optional[str] = Query(None, description="Búsqueda por texto"),
    min_cvss: Optional[float] = Query(None, ge=0, le=10, description="CVSS mínimo"),
    max_cvss: Optional[float] = Query(None, ge=0, le=10, description="CVSS máximo")
):
    """
    Obtiene todas las vulnerabilidades con filtros opcionales
    """
    vulns = await get_vulnerabilities(skip, limit)
    
    print(f"🔍 DEBUG router: Recibidas {len(vulns)} vulnerabilidades de crud.py")
    
    # Filtrado por texto
    if q:
        q_lower = q.lower()
        vulns = [v for v in vulns if 
                 q_lower in str(v.get("cve", "")).lower() or
                 q_lower in str(v.get("vulnerability_name", "")).lower() or
                 q_lower in str(v.get("description", "")).lower() or
                 q_lower in str(v.get("cwe_name", "")).lower() or
                 q_lower in str(v.get("group", "")).lower()]
    
    # Filtrado por CVSS
    if min_cvss is not None:
        vulns = [v for v in vulns if v.get("cvss_v4") and float(v["cvss_v4"]) >= min_cvss]
    
    if max_cvss is not None:
        vulns = [v for v in vulns if v.get("cvss_v4") and float(v["cvss_v4"]) <= max_cvss]
    
    print(f"✅ DEBUG router: Devolviendo {len(vulns)} vulnerabilidades después de filtros")
    return vulns

@router.get("/{id}")
async def read_one(id: int):
    """
    Obtiene una vulnerabilidad específica por ID
    """
    vuln = await get_vulnerability(id)
    if not vuln:
        raise HTTPException(status_code=404, detail="No encontrada")
    return vuln