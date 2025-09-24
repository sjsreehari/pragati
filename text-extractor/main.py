"""
DPR Text Extractor (Multilingual)
Main script to extract text from DPR documents in any language, especially Indian Northeast languages.
"""
from utils import load_file, extract_text, create_txt_file, save_text
import os
import sys

INPUT_DIR = "input"
OUTPUT_DIR = "output"

# Instructions for future enhancements:
# - Integrate with DPR evaluation system
# - Add support for more file formats
# - Improve language detection and OCR accuracy

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <filename>")
        sys.exit(1)
    filename = sys.argv[1]
    input_path = os.path.join(INPUT_DIR, filename)
    try:
        file = load_file(input_path)
        text = extract_text(file)
        txt_filename = create_txt_file(filename)
        save_text(text, txt_filename)
        print(f"Extraction complete. Output saved to {txt_filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
