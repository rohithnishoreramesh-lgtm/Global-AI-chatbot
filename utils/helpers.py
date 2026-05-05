from pypdf import PdfReader

def read_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def read_text_file(uploaded_file):
    return uploaded_file.read().decode("utf-8", errors="ignore")