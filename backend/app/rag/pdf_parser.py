import fitz
import os
import re

def parse_pdf(file_path: str):
    """
    Parses a PDF file and extracts text page by page.
    Returns a list of dictionaries containing page_number and text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    doc = fitz.open(file_path)
    pages = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        # Clean up text by removing extra newlines and spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        if text:  # Only add non-empty pages
            pages.append({
                "page_number": page_num + 1,
                "text": text
            })
        
    return pages
