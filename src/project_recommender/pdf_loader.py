# Date: 28/10/2025 
#--------------------------------------------------------#
# Description: This module takes a PDF and returns raw text
# Functionality: PDF (filepath) --> raw text (string); optionally a .txt file
# _clean_extracted_text: removes weird artifacts from reading PDFs like line breaks and broken characters
# pdf_load: takes a PDF filepath and runs it through above to return string and optionally .txt file
#--------------------------------------------------------#

from pdfminer.high_level import extract_text
from pathlib import Path
import re
from typing import Tuple

def _clean_extracted_text(text: str) -> str:
    """
    Clean text extracted from PDFs:
    - normalize newlines
    - remove form feeds
    - fix word hyphenation (e.g. "exam-\nple" -> "example")
    - join lines inside paragraphs
    - collapse excessive blank lines
    """
    if not text:
        return ""

    # Normalize and remove form feeds
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\x0c', '\n')

    # Fix hyphenation: connect words broken by line breaks
    text = re.sub(r'([A-Za-z0-9])-\n([A-Za-z0-9])', r'\1\2', text)

    # Split into paragraphs by blank lines
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]

    cleaned = []
    for p in paragraphs:
        # Replace remaining newlines with spaces within paragraph
        p = re.sub(r'\n+', ' ', p)
        p = re.sub(r'[ \t]+', ' ', p)
        cleaned.append(p.strip())

    return "\n\n".join(cleaned) + "\n"

def pdf_load(input_pdf: str, write_txt: bool = True) -> Tuple[str, str]:
    """
    Extract and clean text from a PDF. Optionally writes a .txt file.

    Args:
        input_pdf: path to PDF
        write_txt: whether to save the cleaned text alongside the PDF

    Returns:
        (cleaned_text, txt_path)
    """
    raw_text = extract_text(input_pdf)
    cleaned_text = _clean_extracted_text(raw_text)

    txt_path = ""
    if write_txt:
        txt_path = str(Path(input_pdf).with_suffix(".txt"))
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

    return cleaned_text, txt_path
