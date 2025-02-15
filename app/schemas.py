# app/schemas.py

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PDFFileBase(BaseModel):
    file_path: str
    file_name: str
    file_size: int
    created_date: datetime
    pdf_metadata: Dict[str, Any]

class PDFFileCreate(PDFFileBase):
    pass

class PDFFileResponse(PDFFileBase):
    rule_id: Optional[int] = None

    class Config:
        orm_mode = True


class OrganizeRulesBase(BaseModel):
    group_by: List[str]
    custom_rules: Dict[str, Any]

class OrganizeRulesCreate(OrganizeRulesBase):
    pass

class OrganizeRulesResponse(OrganizeRulesBase):
    rule_id: int
    # Optional: include associated PDF files if needed.
    pdf_files: Optional[List[PDFFileResponse]] = []

    class Config:
        orm_mode = True

# ---------------------------
# OrganizationReport Schemas
# ---------------------------
class OrganizationReportBase(BaseModel):
    moved_files: int
    new_folders: Dict[str, Any]  # E.g., {"2023": ["folder1", "folder2"]}
    errors: Dict[str, Any]       # E.g., {"error1": "description", ...}

class OrganizationReportCreate(OrganizationReportBase):
    rule_id: int  # Which OrganizeRules were applied

class OrganizationReportResponse(OrganizationReportBase):
    report_id: int
    rule_id: int

    class Config:
        orm_mode = True