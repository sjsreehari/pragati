"""
Utility functions for DPR Text Extractor (Multilingual)
Handles file loading, text extraction (including OCR), and saving output.
"""
import os
import json
import re
import mimetypes
from datetime import datetime
from typing import Any, Dict, List

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


def clean_text(text: str) -> str:
    """
    Cleans the extracted text by removing extra whitespace, normalizing line breaks,
    and formatting paragraphs properly.
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\r\n|\r', '\n', text)  # Normalize line endings
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Remove excessive empty lines
    text = re.sub(r'[ \t]+', ' ', text)  # Replace multiple spaces/tabs with single space
    
    # Remove trailing whitespace from each line
    lines = [line.rstrip() for line in text.split('\n')]
    
    # Remove empty lines at the beginning and end
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    # Join lines back together
    cleaned_text = '\n'.join(lines)
    
    # Fix common OCR issues
    cleaned_text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', cleaned_text)  # Fix hyphenated words split across lines
    cleaned_text = re.sub(r'(?<=[a-z])\s+(?=[A-Z][a-z])', ' ', cleaned_text)  # Fix spacing issues
    
    return cleaned_text.strip()


def create_json_file(filename: str) -> str:
    """
    Creates a blank .json file in the output folder with the same name as the input file.
    Returns the path to the new .json file.
    """
    base = os.path.splitext(filename)[0]
    json_path = os.path.join("output", f"{base}.json")
    return json_path


def save_text_as_json(text: str, filename: str, original_filename: str, extraction_method: str = "text") -> Dict:
    """
    Saves the extracted text as JSON with metadata and cleaned text.
    Returns the JSON data structure.
    """
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Extract index/table of contents
    index_structure = extract_document_index(text)
    
    # Create JSON structure
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
        "index": index_structure,
        "statistics": {
            "total_index_items": len(index_structure),
            "total_characters": len(cleaned_text),
            "total_words": len(cleaned_text.split()) if cleaned_text else 0,
            "total_lines": len(cleaned_text.split('\n')) if cleaned_text else 0,
            "paragraphs": len([p for p in cleaned_text.split('\n\n') if p.strip()]) if cleaned_text else 0
        }
    }
    
    # Save to JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    return json_data


def extract_document_index(text: str) -> List[Dict]:
    """
    Extracts the table of contents/index from the document text.
    Returns a structured list of index items with titles and page numbers.
    """
    index_items = []
    
    # Look for common table of contents patterns
    toc_patterns = [
        r'Table of Contents',
        r'TABLE OF CONTENTS',
        r'Contents',
        r'CONTENTS',
        r'Index',
        r'INDEX'
    ]
    
    lines = text.split('\n')
    in_toc_section = False
    current_index = 1
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Check if we're entering a TOC section
        if not in_toc_section:
            for pattern in toc_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    in_toc_section = True
                    break
            continue
        
        # Skip empty lines in TOC
        if not line:
            continue
            
        # Stop if we encounter certain patterns that indicate end of TOC
        end_patterns = [
            r'^\d+\.\s+Introduction',
            r'^\d+\s+Introduction',
            r'^INTRODUCTION',
            r'^1\s+Introduction',
            r'^1\.\s+Introduction'
        ]
        
        for pattern in end_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Add this line as first index item if it matches introduction pattern
                title_match = re.search(r'(?:\d+\.?\s+)?(.+?)(?:\s+\d+)?$', line)
                if title_match:
                    title = title_match.group(1).strip()
                    page_match = re.search(r'\d+$', line)
                    page_num = page_match.group() if page_match else "N/A"
                    
                    index_items.append({
                        "index": current_index,
                        "title": title,
                        "page_number": page_num
                    })
                    current_index += 1
                in_toc_section = False
                break
        
        if not in_toc_section:
            continue
            
        # Pattern matching for index items with various formats
        patterns = [
            # Format: "1 TITLE 5" or "1. TITLE 5"
            r'^(\d+)\.?\s+([A-Z][A-Z\s&]+(?:[a-z][a-z\s]*)?)\s+(\d+)$',
            # Format: "Sr No Content" header - skip this
            r'^Sr\s+No\s+Content',
            # Format: "Page No" header - skip this  
            r'^Page\s+No',
            # Format: number only
            r'^\d+$'
        ]
        
        # Skip header lines
        if re.search(r'^Sr\s+No\s+Content|^Page\s+No', line, re.IGNORECASE):
            continue
            
        # Skip lines that are just numbers
        if re.match(r'^\d+$', line):
            continue
            
        # Try to match index item patterns
        for pattern in patterns:
            match = re.search(pattern, line)
            if match and len(match.groups()) == 3:  # Has number, title, and page
                item_num = match.group(1)
                title = match.group(2).strip()
                page_num = match.group(3)
                
                # Clean up the title
                title = re.sub(r'\s+', ' ', title)  # Remove extra spaces
                title = title.title() if title.isupper() else title  # Convert from ALL CAPS
                
                index_items.append({
                    "index": current_index,
                    "title": title,
                    "page_number": page_num
                })
                current_index += 1
                break
        
        # Alternative: Look for chapter/section headings in the main text
        chapter_patterns = [
            r'^(\d+)\.\s+([A-Z][A-Za-z\s&]+)',  # "1. Introduction About The Project"
            r'^(\d+)\s+([A-Z][A-Z\s]+)',        # "1 INTRODUCTION"
        ]
        
        for pattern in chapter_patterns:
            match = re.search(pattern, line)
            if match:
                chapter_num = match.group(1)
                title = match.group(2).strip()
                
                # Try to find page number in nearby lines
                page_num = "N/A"
                for j in range(max(0, i-3), min(len(lines), i+4)):
                    page_match = re.search(r'Page\s+(\d+)', lines[j])
                    if page_match:
                        page_num = page_match.group(1)
                        break
                
                # Clean up title
                title = re.sub(r'\s+', ' ', title)
                title = title.title() if title.isupper() else title
                
                # Avoid duplicates
                if not any(item['title'].lower() == title.lower() for item in index_items):
                    index_items.append({
                        "index": current_index,
                        "title": title,
                        "page_number": page_num
                    })
                    current_index += 1
                break
    
    # If no TOC found, try to extract major headings from document structure
    if not index_items:
        index_items = extract_headings_from_content(text)
    
    return index_items


def extract_headings_from_content(text: str) -> List[Dict]:
    """
    Extracts major headings from document content when no formal TOC is found.
    """
    headings = []
    lines = text.split('\n')
    current_index = 1
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for numbered sections like "1. Title", "2. Title", etc.
        heading_patterns = [
            r'^(\d+)\.\s+([A-Z][A-Za-z\s&()]+)',  # "1. Introduction About The Project"
            r'^(\d+)\s+([A-Z][A-Z\s&()]+)',       # "1 BACKGROUND OF PROJECT"
        ]
        
        for pattern in heading_patterns:
            match = re.search(pattern, line)
            if match:
                section_num = match.group(1)
                title = match.group(2).strip()
                
                # Clean up title
                title = re.sub(r'\s+', ' ', title)
                title = title.title() if title.isupper() else title
                
                # Try to find page number
                page_num = "N/A"
                for j in range(max(0, i-5), min(len(lines), i+6)):
                    page_match = re.search(r'Page\s+(\d+)', lines[j])
                    if page_match:
                        page_num = page_match.group(1)
                        break
                
                # Avoid duplicates and very short titles
                if len(title) > 3 and not any(item['title'].lower() == title.lower() for item in headings):
                    headings.append({
                        "index": current_index,
                        "title": title,
                        "page_number": page_num
                    })
                    current_index += 1
                break
    
    return headings
