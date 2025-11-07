# api/routers/vulnerabilities.py
from fastapi import APIRouter, HTTPException
from typing import List
from .. import crud, models

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])

@router.get("/", response_model=List[models.Vulnerability])
async def read_vulnerabilities(skip: int = 0, limit: int = 100):
    return await crud.get_vulnerabilities(skip, limit)

@router.get("/{vuln_id}", response_model=models.Vulnerability)
async def read_vulnerability(vuln_id: int):
    vuln = await crud.get_vulnerability_by_id(vuln_id)
    if not vuln:
        raise HTTPException(404, "Vulnerabilidad no encontrada")
    return vuln

@router.post("/", response_model=models.Vulnerability)
async def create_vulnerability(vuln: models.Vulnerability):
    return await crud.create_vulnerability(vuln)