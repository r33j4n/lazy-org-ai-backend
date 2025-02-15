from PyPDF2 import PdfReader
from typing import Dict

class PDFProcessor:
    def extract_metadata(self, pdf_path: str) -> Dict:
        pdf_meta_data= {}
        try:
            with open(pdf_path,"rb") as file:
                reader = PdfReader(file)
                if reader.metadata:
                    pdf_meta_data = dict(reader.metadata)
        except Exception as e:
            print(f"Error reading metadata from {pdf_path}: {e}")
        return pdf_meta_data

