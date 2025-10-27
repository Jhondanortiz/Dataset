from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"])

@router.get("/", response_model=List[schemas.Vulnerability])
def read_vulnerabilities(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_vulnerabilities(db, skip, limit)

@router.get("/{vuln_id}", response_model=schemas.Vulnerability)
def read_vulnerability(vuln_id: int, db: Session = Depends(database.get_db)):
    vuln = crud.get_vulnerability(db, vuln_id)
    if not vuln:
        raise HTTPException(404, "Vulnerabilidad no encontrada")
    return vuln

@router.post("/", response_model=schemas.Vulnerability)
def create_vulnerability(vuln: schemas.VulnerabilityCreate, db: Session = Depends(database.get_db)):
    return crud.create_vulnerability(db, vuln)