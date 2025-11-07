# api/models.py
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class Vulnerability(BaseModel):
    id: int
    vulnerability_name: Optional[str] = None
    cve: Optional[str] = None
    cwe_id: Optional[str] = None
    cvss_v4: Optional[float] = None
    description: Optional[str] = None
    group: str
    subgroup: Optional[str] = None
    pdf_sources: List[str] = Field(default_factory=list)
    related_vulnerabilities: List[str] = Field(default_factory=list, alias="related_cves")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}