from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Vulnerability
from ..crud import create_vulnerability, get_vulnerabilities, get_vulnerability

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])

@router.get("/", response_model=List[Vulnerability])
async def read_all(skip: int = 0, limit: int = 100):
    return await get_vulnerabilities(skip, limit)

@router.get("/{id}", response_model=Vulnerability)
async def read_one(id: int):
    vuln = await get_vulnerability(id)
    if not vuln:
        raise HTTPException(404, "No encontrada")
    return vuln