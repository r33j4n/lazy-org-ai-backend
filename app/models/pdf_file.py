from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, false
from sqlalchemy.orm import relationship
from app.core.database import Base

class PDFFile(Base):
    __tablename__ = "pdf_file"
    file_path = Column(String(512), primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    created_date = Column(DateTime)
    pdf_metadata = Column(JSON)

    rule_id = Column(Integer, ForeignKey("organize_rules.rule_id"), nullable=True)
    organize_rules = relationship("OrganizeRules", back_populates="pdf_files")
