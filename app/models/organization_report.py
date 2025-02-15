# app/models/organization_report.py

from sqlalchemy import Column, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class OrganizationReport(Base):
    __tablename__ = "organization_report"

    report_id = Column(Integer, primary_key=True, index=True)
    moved_files = Column(Integer)
    new_folders = Column(JSON)
    errors = Column(JSON)

    # Foreign key: Link to the OrganizeRules used for this report
    rule_id = Column(Integer, ForeignKey("organize_rules.rule_id"))
    organize_rules = relationship("OrganizeRules", back_populates="organization_reports")