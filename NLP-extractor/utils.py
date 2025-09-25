import os
import json
import re
import mimetypes
from datetime import datetime
from typing import Any, Dict, List

try:
    import docx
    from pdfminer.high_level import extract_text as pdf_extract_text
except ImportError:
    docx = None
    pdf_extract_text = None

try:
    import pytesseract
    from PIL import Image
    import pdf2image
except ImportError:
    pytesseract = None
    Image = None
    pdf2image = None

def load_file(input_path: str) -> Any:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")
    mime_type, _ = mimetypes.guess_type(input_path)
    if mime_type == "application/pdf":
        return input_path
    elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        return docx.Document(input_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and Word files are supported.")

def extract_text(file: Any, file_path: str = None) -> str:
    if isinstance(file, str) and file.lower().endswith(".pdf"):
        if pdf_extract_text:
            text = pdf_extract_text(file)
            if text.strip():
                return text
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
    elif docx and hasattr(file, "paragraphs"):
        return "\n".join([para.text for para in file.paragraphs])
    else:
        raise ValueError("Unsupported file type for extraction.")

def create_txt_file(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    txt_path = os.path.join("output", f"{base}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        pass
    return txt_path

def save_text(text: str, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    text = re.sub(r'\r\n|\r', '\n', text)
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    lines = [line.rstrip() for line in text.split('\n')]
    
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    cleaned_text = '\n'.join(lines)
    cleaned_text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', cleaned_text)
    cleaned_text = re.sub(r'(?<=[a-z])\s+(?=[A-Z][a-z])', ' ', cleaned_text)
    
    return cleaned_text.strip()

def create_json_file(filename: str) -> str:
    base = os.path.splitext(filename)[0]
    json_path = os.path.join("output", f"{base}.json")
    return json_path

def save_text_as_json(text: str, filename: str, original_filename: str, extraction_method: str = "text") -> Dict:
    cleaned_text = clean_text(text)
    index_structure = extract_document_index(text)
    
    json_data = {
        "metadata": {
            "original_filename": original_filename,
            "extraction_timestamp": datetime.now().isoformat(),
            "extraction_method": extraction_method,
            "raw_text_length": len(text),
            "cleaned_text_length": len(cleaned_text),
            "output_format": "json",
            "has_index": len(index_structure) > 0
        },
        "content": {
            "full_text": cleaned_text,
            "raw_text": text
        },
        "index": index_structure,
        "statistics": {
            "total_index_items": len(index_structure),
            "total_characters": len(cleaned_text),
            "total_words": len(cleaned_text.split()) if cleaned_text else 0,
            "total_lines": len(cleaned_text.split('\n')) if cleaned_text else 0,
            "paragraphs": len([p for p in cleaned_text.split('\n\n') if p.strip()]) if cleaned_text else 0
        }
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return json_data

def extract_document_index(text: str) -> List[Dict]:
    index_items = []
    lines = text.split('\n')
    
    # Look for table of contents section
    in_toc_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Find table of contents start
        if re.search(r'table\s+of\s+contents', line, re.IGNORECASE):
            in_toc_section = True
            continue
        
        if not in_toc_section:
            continue
        
        # Skip empty lines and headers
        if not line or re.search(r'^(sr\s*no|page\s*no|content)$', line, re.IGNORECASE):
            continue
        
        # Look for pattern: number followed by content title
        # Example: "1" followed by "INTRODUCTION ABOUT THE PROJECT"
        if re.match(r'^[1-8]$', line):
            # Look for the title in subsequent lines
            for j in range(i+1, min(len(lines), i+5)):
                next_line = lines[j].strip()
                
                # Skip empty lines and other numbers
                if not next_line or re.match(r'^[1-8]$', next_line):
                    continue
                
                # Found a title
                if len(next_line) > 5 and not next_line.isdigit():
                    # Look for page number in the next few lines
                    page_num = "N/A"
                    for k in range(j+1, min(len(lines), j+3)):
                        page_line = lines[k].strip()
                        if re.match(r'^\d+$', page_line):
                            page_num = page_line
                            break
                    
                    index_items.append({
                        "item_number": line,
                        "title": next_line,
                        "page_number": page_num
                    })
                    break
        
        # Alternative pattern: "1. TITLE" format
        match = re.match(r'^(\d+)\.\s*(.+)$', line)
        if match:
            num = match.group(1)
            title = match.group(2).strip()
            
            # Look for page number
            page_num = "N/A"
            for j in range(i+1, min(len(lines), i+3)):
                page_line = lines[j].strip()
                if re.match(r'^\d+$', page_line):
                    page_num = page_line
                    break
            
            index_items.append({
                "item_number": num,
                "title": title,
                "page_number": page_num
            })
        
        # Stop if we reach the first chapter/section
        if re.search(r'^1\.\s*introduction', line, re.IGNORECASE):
            break
    
    return index_items
    
    return index_items

def extract_headings_from_content(text: str) -> List[Dict]:
    headings = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for numbered sections like "1. Title", "2. Title", etc.
        match = re.match(r'^(\d+)\.\s+([A-Z][A-Za-z\s&()]+)', line)
        if match:
            section_num = match.group(1)
            title = match.group(2).strip()
            
            # Try to find page number in surrounding lines
            page_num = "N/A"
            for j in range(max(0, i-5), min(len(lines), i+6)):
                page_match = re.search(r'page\s+(\d+)', lines[j], re.IGNORECASE)
                if page_match:
                    page_num = page_match.group(1)
                    break
            
            # Clean up title
            title = re.sub(r'\s+', ' ', title)
            if title.isupper():
                title = title.title()
            
            if len(title) > 3:
                headings.append({
                    "item_number": len(headings) + 1,
                    "title": title,
                    "page_number": page_num
                })
    
    return headings