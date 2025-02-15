from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import get_db
from sqlalchemy import text
from app.models.pdf_file import PDFFile
from app.services.pdf_processor import PDFProcessor
from datetime import datetime
import os
from fastapi import HTTPException
from app.core.config import settings
from app.services.pdf_organizer_service import PDFOrganizerService

router = APIRouter()

@router.get('/test')
async def test():
    return {"message": "API test successful"}

@router.get("/test-db")
async def test_db(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1")).scalar()
    return {"db_test": result}


@router.post("/save-metadata")
async def save_metadata(file_path: str, db: Session = Depends(get_db)):
    # Check if file exists on the file system
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Extract metadata using PDFProcessor
    processor = PDFProcessor()
    metadata = processor.extract_metadata(file_path)
    if not metadata:
        raise HTTPException(status_code=400, detail="Failed to extract metadata")

    # Gather additional file info
    stat_info = os.stat(file_path)

    # Check if the PDFFile record already exists
    existing_file = db.query(PDFFile).filter(PDFFile.file_path == file_path).first()
    if existing_file:
        # Option 1: Update the existing record with new information
        existing_file.file_size = stat_info.st_size
        existing_file.created_date = datetime.fromtimestamp(stat_info.st_ctime)
        existing_file.pdf_metadata = metadata
        db.commit()
        db.refresh(existing_file)
        return {
            "message": "File already exists. Record updated.",
            "pdf_file": {
                "file_path": existing_file.file_path,
                "file_name": existing_file.file_name,
                "file_size": existing_file.file_size,
                "created_date": existing_file.created_date,
                "pdf_metadata": existing_file.pdf_metadata,
                "rule_id": existing_file.rule_id,
            }
        }
    else:
        # Option 2: Insert a new record
        new_file = PDFFile(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_size=stat_info.st_size,
            created_date=datetime.fromtimestamp(stat_info.st_ctime),
            pdf_metadata=metadata,
            rule_id=None
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        return {
            "message": "Metadata saved successfully",
            "pdf_file": {
                "file_path": new_file.file_path,
                "file_name": new_file.file_name,
                "file_size": new_file.file_size,
                "created_date": new_file.created_date,
                "pdf_metadata": new_file.pdf_metadata,
                "rule_id": new_file.rule_id,
            }
        }


@router.post("/scan-folder")
async def scan_folder_for_pdfs(db: Session = Depends(get_db)):
    """
    Automatically scans the configured folder for PDF files,
    extracts metadata, and saves (or updates) each PDF record.
    """
    folder_path = settings.TARGET_FOLDER
    if not os.path.isdir(folder_path):
        raise HTTPException(status_code=404, detail="Configured folder not found")

    processor = PDFProcessor()
    processed_files = []
    errors = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            try:
                # Get file stats
                stat_info = os.stat(file_path)
                # Extract metadata using PDFProcessor
                metadata = processor.extract_metadata(file_path)
                if not metadata:
                    errors.append(f"Failed to extract metadata from {file_path}")
                    continue

                # Check if the file record already exists
                existing_file = db.query(PDFFile).filter(PDFFile.file_path == file_path).first()
                if existing_file:
                    # Update existing record
                    existing_file.file_size = stat_info.st_size
                    existing_file.created_date = datetime.fromtimestamp(stat_info.st_ctime)
                    existing_file.pdf_metadata = metadata
                    db.commit()
                    db.refresh(existing_file)
                    processed_files.append({"file": file_path, "status": "updated"})
                else:
                    # Create a new record
                    new_file = PDFFile(
                        file_path=file_path,
                        file_name=filename,
                        file_size=stat_info.st_size,
                        created_date=datetime.fromtimestamp(stat_info.st_ctime),
                        pdf_metadata=metadata,
                        rule_id=None
                    )
                    db.add(new_file)
                    db.commit()
                    db.refresh(new_file)
                    processed_files.append({"file": file_path, "status": "created"})
            except Exception as e:
                errors.append(f"Error processing {file_path}: {str(e)}")
    return {"processed_files": processed_files, "errors": errors}

@router.post("/organize")
def organize_pdfs_endpoint(db: Session = Depends(get_db)):
    """
    Endpoint to group PDF files by their created_date (year and month).
    This will copy each PDF into a subfolder structure under settings.ORGANIZED_FOLDER.
    """
    try:
        organizer = PDFOrganizerService(db)
        result = organizer.organize_pdfs_by_downloaded_date()  # Synchronous call
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/organize-mod-date")
def organize_by_mod_date(db: Session = Depends(get_db)):
    """
    Organizes PDFs based on the /ModDate from pdf_metadata.
    Files are copied into subfolders based on the year and month derived from /ModDate.
    """
    try:
        organizer = PDFOrganizerService(db)
        result = organizer.organize_pdfs_by_mod_date()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))