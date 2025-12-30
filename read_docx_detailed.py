
from docx import Document
import sys

def read_docx_detailed(file_path):
    try:
        doc = Document(file_path)
        content = []
        
        # Helper to extract text from valid elements
        def iter_block_items(parent):
            if isinstance(parent, Document):
                parent_elm = parent.element.body
            else:
                parent_elm = parent._element
            for child in parent_elm.iterchildren():
                if child.tag.endswith('p'):
                    yield 'P', child
                elif child.tag.endswith('tbl'):
                    yield 'T', child

        for block_type, block in iter_block_items(doc):
            if block_type == 'P':
                # It's a paragraph, we need to wrap it to read text
                from docx.text.paragraph import Paragraph
                para = Paragraph(block, doc)
                if para.text.strip():
                    content.append(f"[PARA] {para.text}")
            elif block_type == 'T':
                # It's a table
                from docx.table import Table
                table = Table(block, doc)
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_data.append(cell.text.strip())
                    if row_data:
                        content.append(f"[TABLE ROW] {' | '.join(row_data)}")

        return '\n'.join(content)
    except Exception as e:
        import traceback
        return f"Error: {str(e)}\n{traceback.format_exc()}"

if __name__ == "__main__":
    file_path = "d:/Year 4 semster 1/GRAD PROJECT/medtwin/NTRA-GP_Competition_template-2025_Ongoing-Academic-year-2025-2026 - UPDATED MEDTWIN.docx"
    print(read_docx_detailed(file_path))
