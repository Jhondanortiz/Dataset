from pydantic import BaseModel
from typing import List, Optional

class SourceBase(BaseModel):
    filename: str
    title: Optional[str] = None
    publication_date: Optional[str] = None
    organization: Optional[str] = None
    url: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class Source(SourceBase):
    source_id: int
    class Config:
        from_attributes = True

class VulnerabilityBase(BaseModel):
    id: int
    vulnerability_name: Optional[str] = None
    cve: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_v4: Optional[float] = None
    description: Optional[str] = None
    group_id: int
    subgroup_id: Optional[int] = None

class VulnerabilityCreate(VulnerabilityBase):
    source_filenames: List[str] = []
    related_cves: List[str] = []

class Vulnerability(VulnerabilityBase):
    vuln_id: int
    sources: List[Source] = []
    class Config:
        from_attributes = True