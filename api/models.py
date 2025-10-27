from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Tablas de relación
vulnerability_sources = Table(
    'vulnerability_sources', Base.metadata,
    Column('vuln_id', Integer, ForeignKey('vulnerabilities.vuln_id'), primary_key=True),
    Column('source_id', Integer, ForeignKey('sources.source_id'), primary_key=True)
)

related_vulnerabilities = Table(
    'related_vulnerabilities', Base.metadata,
    Column('vuln_id', Integer, ForeignKey('vulnerabilities.vuln_id'), primary_key=True),
    Column('related_cve', String(50), ForeignKey('vulnerabilities.cve'), primary_key=True)
)

class Source(Base):
    __tablename__ = "sources"
    source_id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), unique=True, nullable=False)
    title = Column(String(500))
    publication_date = Column(String(10))  # DATE como str
    organization = Column(String(200))
    url = Column(Text)

    vulnerabilities = relationship("Vulnerability", secondary=vulnerability_sources, back_populates="sources")

class Group(Base):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(200), unique=True, nullable=False)

    subgroups = relationship("Subgroup", back_populates="group")
    vulnerabilities = relationship("Vulnerability", back_populates="group")

class Subgroup(Base):
    __tablename__ = "subgroups"
    subgroup_id = Column(Integer, primary_key=True, index=True)
    subgroup_name = Column(String(200), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable=False)

    group = relationship("Group", back_populates="subgroups")
    vulnerabilities = relationship("Vulnerability", back_populates="subgroup")

class CWE(Base):
    __tablename__ = "cwe"
    cwe_id = Column(String(20), primary_key=True)
    cwe_name = Column(String(300), nullable=False)

    vulnerabilities = relationship("Vulnerability", back_populates="cwe")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    vuln_id = Column(Integer, primary_key=True, index=True)
    id = Column(Integer, unique=True, nullable=False)
    vulnerability_name = Column(String(300))
    cve = Column(String(50), unique=True)
    cwe_id = Column(String(20), ForeignKey("cwe.cwe_id"))
    cvss_v4 = Column(Float)
    description = Column(Text)
    group_id = Column(Integer, ForeignKey("groups.group_id"), nullable=False)
    subgroup_id = Column(Integer, ForeignKey("subgroups.subgroup_id"))

    group = relationship("Group", back_populates="vulnerabilities")
    subgroup = relationship("Subgroup", back_populates="vulnerabilities")
    cwe = relationship("CWE", back_populates="vulnerabilities")
    sources = relationship("Source", secondary=vulnerability_sources, back_populates="vulnerabilities")
    related = relationship("Vulnerability", secondary=related_vulnerabilities,
                           primaryjoin=(vuln_id == related_vulnerabilities.c.vuln_id),
                           secondaryjoin=(cve == related_vulnerabilities.c.related_cve))