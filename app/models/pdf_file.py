from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, false
from sqlalchemy.orm import relationship
from app.core.database import Base

class PDFFile(Base):
    __tablename__ = "pdf_file"
    file_path = Column(String, primary_key=True)
    file_name = Column(String,nullable=false)
    file_size = Column(Integer,nullable=false)
    created_date=Column(DateTime)
    metadata = Column(JSON)

    rule_id = Column(Integer, ForeignKey("organize_rules.rule_id"), nullable=True)
    organize_rules = relationship("OrganizeRules", back_populates="pdf_files")
