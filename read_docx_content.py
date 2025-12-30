
from docx import Document
import sys

def read_docx(file_path):
    try:
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = "d:/Year 4 semster 1/GRAD PROJECT/medtwin/NTRA-GP_Competition_template-2025_Ongoing-Academic-year-2025-2026 - UPDATED MEDTWIN.docx"
    print(read_docx(file_path))
