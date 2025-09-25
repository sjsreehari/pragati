"""
DPR Text Extractor (Multilingual)
Main script to extract text from DPR documents in any language, especially Indian Northeast languages.
Supports both TXT and JSON output formats with text cleaning capabilities.
"""
from utils import load_file, extract_text, create_txt_file, save_text, create_json_file, save_text_as_json
import os
import sys
import argparse

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    parser = argparse.ArgumentParser(description="Extract text from DPR documents with support for multiple output formats")
    parser.add_argument("filename", help="Input filename (relative to input/ directory)")
    parser.add_argument("--format", "-f", choices=["txt", "json", "both"], default="json", 
                       help="Output format: txt, json, or both (default: json)")
    
    # Handle legacy usage (backward compatibility)
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        filename = sys.argv[1]
        output_format = "json"
    else:
        args = parser.parse_args()
        filename = args.filename
        output_format = args.format
    
    input_path = os.path.join(INPUT_DIR, filename)
    
    try:
        file = load_file(input_path)
        text = extract_text(file)
        
        extraction_method = "pdf_extraction" if input_path.lower().endswith('.pdf') and text.strip() else "ocr" if input_path.lower().endswith('.pdf') else "docx_extraction"
        
        outputs = []
        
        if output_format in ["txt", "both"]:
            txt_filename = create_txt_file(filename)
            save_text(text, txt_filename)
            outputs.append(txt_filename)
            print(f"TXT output saved to: {txt_filename}")
        
        if output_format in ["json", "both"]:
            json_filename = create_json_file(filename)
            json_data = save_text_as_json(text, json_filename, filename, extraction_method)
            outputs.append(json_filename)
            print(f"JSON output saved to: {json_filename}")
            
            stats = json_data["statistics"]
            print(f"\nExtraction Summary:")
            print(f"  - Index entries: {stats['total_index_items']}")
            print(f"  - Total words: {stats['total_words']}")
            print(f"  - Extraction method: {extraction_method}")
        
        print(f"\nExtraction complete! Output files: {', '.join(outputs)}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
