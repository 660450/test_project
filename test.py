import pdfplumber

PDF_FILE = "CC329-R00-Model-Color-NewIC.pdf"

with pdfplumber.open(PDF_FILE) as pdf:
    page = pdf.pages[0]
    text = page.extract_text()
    print(text)
