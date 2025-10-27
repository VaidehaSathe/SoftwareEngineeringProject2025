from pdfminer.high_level import extract_text

def pdf_load(input_pdf):
    text=extract_text(input_pdf)
    output_txt=input_pdf.rsplit('.', 1)[0] + '.txt'
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(text)
    return text