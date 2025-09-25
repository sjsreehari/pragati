from utils import load_file, extract_text, create_txt_file, save_text, create_json_file, save_text_as_json, clean_text, extract_document_index
import os
import sys
import argparse
from pathlib import Path

# Import compliance checker (optional - will work without it)
try:
    from compliance_checker import DPRComplianceChecker
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def main():
    parser = argparse.ArgumentParser(description="Extract text from DPR documents with support for multiple output formats")
    parser.add_argument("filename", help="Input filename (relative to input/ directory)")
    parser.add_argument("--format", "-f", choices=["txt", "json", "both"], default="json", 
                       help="Output format: txt, json, or both (default: json)")
    parser.add_argument("--compliance", "-c", action="store_true",
                       help="Run MDONER/NEC DPR compliance check (requires compliance_checker.py)")
    parser.add_argument("--html-report", action="store_true",
                       help="Generate HTML compliance report (use with --compliance)")
    
    # Handle legacy usage (backward compatibility)
    if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
        filename = sys.argv[1]
        output_format = "json"
        run_compliance = False
        generate_html = False
    else:
        args = parser.parse_args()
        filename = args.filename
        output_format = args.format
        run_compliance = args.compliance
        generate_html = args.html_report
    
    input_path = os.path.join(INPUT_DIR, filename)
    
    try:
        file = load_file(input_path)
        raw_text = extract_text(file, input_path)
        clean_text_content = clean_text(raw_text)
        
        extraction_method = "pdf_extraction" if input_path.lower().endswith('.pdf') and clean_text_content.strip() else "ocr" if input_path.lower().endswith('.pdf') else "docx_extraction"
        
        outputs = []
        json_data = None
        
        if output_format in ["txt", "both"]:
            txt_filename = create_txt_file(filename)
            save_text(clean_text_content, txt_filename)
            outputs.append(txt_filename)
            print(f"TXT output saved to: {txt_filename}")
        
        if output_format in ["json", "both"]:
            json_filename = create_json_file(filename)
            json_data = save_text_as_json(clean_text_content, json_filename, filename, extraction_method)
            outputs.append(json_filename)
            print(f"JSON output saved to: {json_filename}")
            
            stats = json_data["statistics"]
            print(f"\nExtraction Summary:")
            print(f"  - Index entries: {stats['total_index_items']}")
            print(f"  - Total words: {stats['total_words']}")
            print(f"  - Extraction method: {extraction_method}")
        
        # Run compliance check if requested
        if run_compliance:
            if not COMPLIANCE_AVAILABLE:
                print("\nWarning: Compliance checker not available. Please ensure compliance_checker.py and mdoner_guidelines.json are present.")
            else:
                print("\nRunning MDONER/NEC DPR compliance check...")
                
                try:
                    # Initialize compliance checker
                    checker = DPRComplianceChecker("mdoner_guidelines.json")
                    
                    # Get document index if JSON was created
                    document_index = []
                    if json_data and json_data.get("index"):
                        document_index = json_data["index"]
                    else:
                        document_index = extract_document_index(clean_text_content)
                    
                    # Run compliance analysis
                    compliance_results = checker.check_compliance(clean_text_content, document_index)
                    
                    # Save compliance results
                    base_name = Path(filename).stem
                    compliance_json = os.path.join(OUTPUT_DIR, f"{base_name}_compliance.json")
                    
                    import json
                    with open(compliance_json, 'w', encoding='utf-8') as f:
                        json.dump(compliance_results, f, indent=2, ensure_ascii=False)
                    
                    outputs.append(compliance_json)
                    print(f"Compliance results saved to: {compliance_json}")
                    
                    # Generate HTML report if requested
                    if generate_html:
                        html_report = os.path.join(OUTPUT_DIR, f"{base_name}_compliance_report.html")
                        checker.generate_report_html(compliance_results, html_report)
                        outputs.append(html_report)
                        print(f"HTML compliance report saved to: {html_report}")
                    
                    # Print compliance summary
                    score = compliance_results['overall_score']
                    level = compliance_results['compliance_level'].replace('_', ' ').title()
                    print(f"\nCompliance Summary:")
                    print(f"  - Overall Score: {score}%")
                    print(f"  - Compliance Level: {level}")
                    print(f"  - Sections Found: {sum(1 for s in compliance_results['section_analysis'].values() if s['found'])}/{len(compliance_results['section_analysis'])}")
                    
                    if score < 70:
                        print(f"  - Status: ⚠️ Needs improvement to meet MDONER/NEC standards")
                    else:
                        print(f"  - Status: ✅ Meets basic compliance requirements")
                
                except FileNotFoundError:
                    print("Error: mdoner_guidelines.json not found. Please ensure the guidelines file is present.")
                except Exception as e:
                    print(f"Error during compliance check: {e}")
        
        print(f"\nExtraction complete! Output files: {', '.join(outputs)}")
        
        # Return appropriate exit code based on compliance if checked
        if run_compliance and COMPLIANCE_AVAILABLE and 'compliance_results' in locals():
            return 0 if compliance_results['overall_score'] >= 70 else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
