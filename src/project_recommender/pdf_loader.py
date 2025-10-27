from pdfminer.high_level import extract_text

def pdf_load(input_pdf):
    text=extract_text(input_pdf)
    return text