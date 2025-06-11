import pytesseract
import fitz  
from PIL import Image
import os

def extract_text_from_file(file):
    """Extract text from uploaded PDF or image file"""
    filename = file.name.lower()
    
    if filename.endswith(".pdf"):
        return ocr_pdf_with_pymupdf(file)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        return extract_text_from_image(file)
    else:
        return "Unsupported file type."

def ocr_pdf_with_pymupdf(file):
    """Extract text from a PDF using OCR (pytesseract + PyMuPDF)"""
    text = ""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += pytesseract.image_to_string(img)
    return text

def extract_text_from_image(file):
    """Extract text from an image using pytesseract"""
    image = Image.open(file)
    return pytesseract.image_to_string(image)
