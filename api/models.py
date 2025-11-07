from pydantic import BaseModel, Field
from typing import List, Optional

class Vulnerability(BaseModel):
    id: int
    pdf_sources: List[str]
    vulnerability_name: Optional[str] = None
    group: int
    subgroup: Optional[int] = None
    cve: Optional[str] = None
    cwe: Optional[str] = None
    cwe_name: Optional[str] = None
    cvss_v4: Optional[float] = None
    related_vulnerabilities: List[str] = Field(default_factory=list)
    description: str