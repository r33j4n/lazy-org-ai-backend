import json
from datetime import datetime
import os
import shutil
from app.core.config import settings
from app.models.pdf_file import PDFFile

class PDFOrganizerService:
    def __init__(self, db_session):
        self.db = db_session

    def organize_pdfs_by_downloaded_date(self):
        """
        Groups PDFs by their created_date into folders based on year and month.
        Copies each file into the corresponding folder under settings.ORGANIZED_FOLDER.
        Returns a dictionary with details of processed files and any errors encountered.
        """
        # Retrieve all PDF records from the database (synchronously)
        pdf_files = self.db.query(PDFFile).all()
        processed_files = []
        errors = []

        for pdf in pdf_files:
            try:
                if pdf.created_date is None:
                    raise Exception("Missing created_date for file.")

                # Determine target folders from the creation date
                year = pdf.created_date.strftime("%Y")
                month = pdf.created_date.strftime("%m")
                target_dir = os.path.join(settings.ORGANIZED_FOLDER,"By Downloaded Date", year, month)
                os.makedirs(target_dir, exist_ok=True)

                # Determine the target file path
                target_path = os.path.join(target_dir, os.path.basename(pdf.file_path))
                # Copy the file (using copy2 to preserve metadata)
                shutil.copy2(pdf.file_path, target_path)
                processed_files.append({"source": pdf.file_path, "destination": target_path, "status": "copied"})
            except Exception as e:
                errors.append({"file": pdf.file_path, "error": str(e)})

        return {"processed_files": processed_files, "errors": errors}

    def organize_pdfs_by_mod_date(self):
        """
        Groups PDFs based on the /ModDate found in pdf_metadata.
        The /ModDate is expected to be in the format:
          "D:YYYYMMDDHHMMSS+00'00'"
        (or similar). The method extracts the date part, converts it into a datetime,
        then groups files by year and month from that date.
        """
        pdf_files = self.db.query(PDFFile).all()
        processed_files = []
        errors = []

        for pdf in pdf_files:
            try:
                # Get the metadata; ensure it's a dict
                metadata = pdf.pdf_metadata
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)

                mod_date_str = metadata.get("/ModDate")
                if not mod_date_str:
                    raise Exception("Missing /ModDate in metadata.")

                # Remove the "D:" prefix if present and take the first 14 characters (YYYYMMDDHHMMSS)
                if mod_date_str.startswith("D:"):
                    mod_date_str = mod_date_str[2:]
                date_part = mod_date_str[:14]
                mod_date = datetime.strptime(date_part, "%Y%m%d%H%M%S")

                year = mod_date.strftime("%Y")
                month = mod_date.strftime("%m")
                target_dir = os.path.join(settings.ORGANIZED_FOLDER,"By Modified Date", year, month)
                os.makedirs(target_dir, exist_ok=True)
                target_path = os.path.join(target_dir, os.path.basename(pdf.file_path))
                shutil.copy2(pdf.file_path, target_path)
                processed_files.append({
                    "source": pdf.file_path,
                    "destination": target_path,
                    "status": "copied (mod_date)"
                })
            except Exception as e:
                errors.append({"file": pdf.file_path, "error": str(e)})

        return {"processed_files": processed_files, "errors": errors}