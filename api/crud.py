from sqlalchemy.orm import Session
from . import models, schemas

def get_vulnerability(db: Session, vuln_id: int):
    return db.query(models.Vulnerability).filter(models.Vulnerability.vuln_id == vuln_id).first()

def get_vulnerabilities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Vulnerability).offset(skip).limit(limit).all()

def create_vulnerability(db: Session, vuln: schemas.VulnerabilityCreate):
    db_vuln = models.Vulnerability(**vuln.dict(exclude={"source_filenames", "related_cves"}))
    db.add(db_vuln)
    db.commit()
    db.refresh(db_vuln)

    # Fuentes
    for filename in vuln.source_filenames:
        source = db.query(models.Source).filter(models.Source.filename == filename).first()
        if not source:
            source = models.Source(filename=filename)
            db.add(source)
            db.commit()
            db.refresh(source)
        db_vuln.sources.append(source)

    # Relacionadas
    for cve in vuln.related_cves:
        related = db.query(models.Vulnerability).filter(models.Vulnerability.cve == cve).first()
        if related:
            stmt = models.related_vulnerabilities.insert().values(vuln_id=db_vuln.vuln_id, related_cve=cve)
            db.execute(stmt)

    db.commit()
    return db_vuln