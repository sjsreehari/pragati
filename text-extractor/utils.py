"""
Utility functions for DPR Text Extractor (Multilingual)
Handles file loading, text extraction (including OCR), and saving output.
"""
import os
import mimetypes
from typing import Any

# PDF and Word extraction
try:
    import docx
    from pdfminer.high_level import extract_text as pdf_extract_text
except ImportError:
    docx = None
    pdf_extract_text = None

# OCR
try:
    import pytesseract
    from PIL import Image
    import pdf2image
except ImportError:
    pytesseract = None
    Image = None
    pdf2image = None

def load_file(input_path: str) -> Any:
    """
    Loads the input file and returns a file object or path.
    Supports PDF and Word formats. Raises error if file is missing or unsupported.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")
    mime_type, _ = mimetypes.guess_type(input_path)
    if mime_type == "application/pdf":
        return input_path
    elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return docx.Document(input_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and Word files are supported.")

def extract_text(file: Any) -> str:
    """
    Extracts text from the loaded file. Uses OCR for scanned PDFs.
    Handles multilingual text, especially Indian Northeast languages.
    """
    # PDF extraction
    if isinstance(file, str) and file.lower().endswith(".pdf"):
        if pdf_extract_text:
            text = pdf_extract_text(file)
            if text.strip():
                return text
        # If no text, try OCR
        if pytesseract and pdf2image:
            try:
                images = pdf2image.convert_from_path(file)
                text = ""
                for img in images:
                    text += pytesseract.image_to_string(img, lang="eng+asm+bod+ben+hin")
                return text
            except Exception as e:
                raise RuntimeError(f"OCR failed: {e}")
        else:
            raise RuntimeError("OCR libraries not installed.")
    # Word extraction
    elif docx and hasattr(file, "paragraphs"):
        return "\n".join([para.text for para in file.paragraphs])
    else:
        raise ValueError("Unsupported file type for extraction.")

def create_txt_file(filename: str) -> str:
    """
    Creates a blank .txt file in the output folder with the same name as the input file.
    Returns the path to the new .txt file.
    """
    base = os.path.splitext(filename)[0]
    txt_path = os.path.join("output", f"{base}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        pass
    return txt_path

def save_text(text: str, filename: str):
    """
    Saves the extracted text to the specified .txt file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)
