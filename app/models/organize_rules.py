from sqlalchemy import Column, Integer, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrganizeRules(Base):
    __tablename__ = "organize_rules"

    rule_id = Column(Integer, primary_key=True, index=True)
    group_by = Column(JSON)  # e.g., ["date", "content"]
    custom_rules = Column(JSON)

    # Relationships: link to PDFFile and OrganizationReport models
    pdf_files = relationship("PDFFile", back_populates="organize_rules")
    organization_reports = relationship("OrganizationReport", back_populates="organize_rules")