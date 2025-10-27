from pdfminer.high_level import extract_text
text=extract_text('######.pdf')
with open('######.txt', 'w', encoding='utf-8') as f:
    f.write(text)
