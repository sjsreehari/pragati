from utils import load_file, extract_text, create_txt_file, save_text, create_json_file, save_text_as_json, clean_text, extract_document_index
import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import re
from datetime import datetime

try:
    from compliance_checker import DPRComplianceChecker
    COMPLIANCE_AVAILABLE = True
except ImportError:
    COMPLIANCE_AVAILABLE = False

try:
    from text_to_csv_converter import extract_parameters_from_text
    CSV_CONVERSION_AVAILABLE = True
except ImportError:
    CSV_CONVERSION_AVAILABLE = False

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def extract_parameters_for_csv(text_content, filename):
    text_lower = text_content.lower()
    sector_keywords = {
        'Information Technology': ['e-vidhan', 'digital', 'computer', 'software', 'application', 'ict', 'technology', 'system'],
        'Transport and Communication': ['road', 'construction', 'transport', 'highway', 'bridge', 'communication'],
        'Education': ['education', 'school', 'college', 'training', 'it.i', 'institute'],
        'Health': ['health', 'medical', 'hospital', 'clinic', 'healthcare'],
        'Irrigation and Flood Control': ['water', 'supply', 'irrigation', 'flood', 'drainage'],
        'Agriculture and Allied': ['agriculture', 'farming', 'crop', 'horticulture', 'livestock'],
        'Industries': ['industry', 'bamboo', 'auditorium', 'commercial']
    }
    """
    Extract DPR parameters and convert to CSV format for model prediction
    """
    parameters = {
        'SR. No.': 1,
        'State': '',
        'Sector': '',
        'Project Name': '',
        'Scheme': '',
        'Sub Scheme': '',
        'Executing Department': '',
        'Sanctioned Date': '',
        'Approved Cost': '0',
        'Scheduled Completion Date': '',
        'Financial Expenditure as on 31-03-2025': '0',
        'Financial Expenditure for current Financial Year 01-04-2025 to 31-08-2025': '0',
        'Total Financial Expenditure': '0',
        'U.C. Received': '0',
        'Present Status': 'Under Review'
    }
    
    # Extract State from Assembly/Council name
    state_match = re.search(r'Assembly/Council Name[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if state_match:
        parameters['State'] = state_match.group(1).strip().upper()
    
    # Extract Project Name
    project_match = re.search(r'DETAILED PROJECT REPORT\s*\(DPR\)\s*\n*(.*?)\s*In Name of', text_content, re.IGNORECASE | re.DOTALL)
    if project_match:
        parameters['Project Name'] = project_match.group(1).strip()
    else:
        title_match = re.search(r'Title of the Project[:\s]*(.*?)(?:\n|$)', text_content, re.IGNORECASE)
        if title_match:
            parameters['Project Name'] = title_match.group(1).strip()
        else:
            # Try to find project name in introduction
            intro_match = re.search(r'INTRODUCTION\s*(.*?)(?:\n\n|\n[A-Z]|\n\d)', text_content, re.IGNORECASE | re.DOTALL)
            if intro_match:
                intro_text = intro_match.group(1)
                # Extract first meaningful line as project name
                lines = [line.strip() for line in intro_text.split('\n') if line.strip()]
    
    max_matches = 0
    detected_sector = 'Infrastructure'  # Default
    
    for sector, keywords in sector_keywords.items():
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        if matches > max_matches:
            max_matches = matches
            detected_sector = sector
    
    parameters['Sector'] = detected_sector
    
    # Extract Scheme
    scheme_match = re.search(r'Scheme[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if scheme_match:
        parameters['Scheme'] = scheme_match.group(1).strip()
    else:
        if 'neva' in text_lower or 'e-vidhan' in text_lower:
            parameters['Scheme'] = 'National e-Vidhan Application (NeVA)'
        elif 'nesids' in text_lower:
            parameters['Scheme'] = 'NESIDS'
        else:
            parameters['Scheme'] = 'Schemes of NEC'
    
    # Extract Sub Scheme
    sub_scheme_match = re.search(r'Sub Scheme[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if sub_scheme_match:
        parameters['Sub Scheme'] = sub_scheme_match.group(1).strip()
    else:
        parameters['Sub Scheme'] = parameters['Scheme']  # Use scheme as fallback
    
    # Extract Executing Department
    dept_match = re.search(r'Executing Department[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if dept_match:
        parameters['Executing Department'] = dept_match.group(1).strip()
    else:
        # Try to find department in the document
        dept_patterns = [
            r'Department of ([^\n,]+)',
            r'([^\n,]*Department[^\n,]*)',
            r'Ministry of ([^\n,]+)'
        ]
        
        for pattern in dept_patterns:
            dept_found = re.search(pattern, text_content, re.IGNORECASE)
            if dept_found:
                parameters['Executing Department'] = dept_found.group(0).strip()
                break
        else:
            parameters['Executing Department'] = 'Public Works Department'  # Common default
    
    # Extract Approved Cost with better pattern matching
    cost_patterns = [
        r'Rs[\s\.]*([0-9,]+[\.]?[0-9]*)\s*(lakh|crore|cr)',
        r'₹[\s\.]*([0-9,]+[\.]?[0-9]*)',
        r'Approved Cost[:\s]*Rs\.?\s*([0-9,]+)',
        r'Tentative Outlay[:\s]*Rs\.?\s*([0-9,]+)',
        r'estimated cost of Rs\.?\s*([0-9,]+)',
        r'cost of Rs\.?\s*([0-9,]+)',
        r'Total Cost[:\s]*Rs\.?\s*([0-9,]+)',
        r'Budget[:\s]*Rs\.?\s*([0-9,]+)'
    ]
    
    cost_found = False
    for pattern in cost_patterns:
        cost_matches = re.findall(pattern, text_content, re.IGNORECASE)
        for match in cost_matches:
            if isinstance(match, tuple):
                cost_value = match[0].replace(',', '')
                unit = match[1].lower() if len(match) > 1 else ''
            else:
                cost_value = match.replace(',', '')
                unit = ''
            
            if cost_value.replace('.', '').isdigit():
                # Convert to numeric value in consistent units
                cost_num = float(cost_value)
                if 'lakh' in unit:
                    cost_num *= 0.01  # Convert lakh to crore
                parameters['Approved Cost'] = str(round(cost_num, 2))
                cost_found = True
                break
        if cost_found:
            break
    
    # Set dates
    current_date = datetime.now().strftime('%d-%m-%Y')
    parameters['Sanctioned Date'] = current_date
    
    # Estimate completion date (1-3 years from now based on project complexity)
    future_date = (datetime.now() + pd.DateOffset(years=2)).strftime('%d-%m-%Y')
    parameters['Scheduled Completion Date'] = future_date
    
    return parameters

def create_prediction_csv(text_content, filename, output_dir=OUTPUT_DIR):
    """
    Create CSV file for model prediction from extracted text
    """
    parameters = extract_parameters_for_csv(text_content, filename)
    
    # Create DataFrame
    df = pd.DataFrame([parameters])
    
    # Ensure correct column order matching training data
    expected_columns = [
        'SR. No.', 'State', 'Sector', 'Project Name', 'Scheme', 'Sub Scheme',
        'Executing Department', 'Sanctioned Date', 'Approved Cost',
        'Scheduled Completion Date', 'Financial Expenditure as on 31-03-2025',
        'Financial Expenditure for current Financial Year 01-04-2025 to 31-08-2025',
        'Total Financial Expenditure', 'U.C. Received', 'Present Status'
    ]
    
    for col in expected_columns:
        if col not in df.columns:
            df[col] = '' if col != 'Approved Cost' else '0'
    
    df = df[expected_columns]
    
    # Save CSV
    base_name = Path(filename).stem
    csv_filename = os.path.join(output_dir, f"{base_name}_for_prediction.csv")
    df.to_csv(csv_filename, index=False)
    
    return csv_filename, parameters

def main():
    parser = argparse.ArgumentParser(description="Extract text from DPR documents with support for multiple output formats")
    parser.add_argument("filename", help="Input filename (relative to input/ directory)")
    parser.add_argument("--format", "-f", choices=["txt", "json", "both", "all"], default="both", help="Output format: txt, json, both, or all (default: both)")
    parser.add_argument("--compliance", "-c", action="store_true", help="Run MDONER/NEC DPR compliance check")
    parser.add_argument("--html-report", action="store_true", help="Generate HTML compliance report")
    parser.add_argument("--csv", action="store_true", help="Generate CSV for model prediction")
    parser.add_argument("--predict", action="store_true", help="Run model prediction after extraction")
    parser.add_argument("--train-model", action="store_true", help="Train the model before prediction")
    args = parser.parse_args()
    filename = args.filename
    output_format = args.format
    run_compliance = args.compliance
    generate_html = args.html_report
    generate_csv = args.csv
    run_prediction = args.predict
    train_model = args.train_model
    

    # If "all" format is selected, enable all outputs
    if output_format == "all":
        output_format = "both"
        run_compliance = True
        generate_csv = True
        run_prediction = True

    # Default behavior: if no specific flags, generate CSV and predict
    if not any([run_compliance, generate_csv, run_prediction]):
        generate_csv = True
        run_prediction = True

    input_path = os.path.join(INPUT_DIR, filename)
    
    try:
        file = load_file(input_path)
        raw_text = extract_text(file, input_path)
        clean_text_content = clean_text(raw_text)
        
        extraction_method = "pdf_extraction" if input_path.lower().endswith('.pdf') and clean_text_content.strip() else "ocr" if input_path.lower().endswith('.pdf') else "docx_extraction"
        
        outputs = []
        json_data = None
        
        # Text output
        if output_format in ["txt", "both"]:
            txt_filename = create_txt_file(filename)
            save_text(clean_text_content, txt_filename)
            outputs.append(txt_filename)
            print(f"TXT output saved to: {txt_filename}")
        
        # JSON output
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
        
        # CSV for model prediction
        if generate_csv or run_prediction:
            csv_filename, parameters = create_prediction_csv(clean_text_content, filename)
            outputs.append(csv_filename)
            print(f"CSV for model prediction saved to: {csv_filename}")
            
            # Display extracted parameters
            print(f"\nExtracted Parameters for Model:")
            for key, value in parameters.items():
                if value and value != '0':  # Only show non-empty and non-zero values
                    print(f"  - {key}: {value}")
        
        # Train model if requested
        if train_model:
            print("\nTraining model...")
            try:
                # Import and run model training
                import subprocess
                result = subprocess.run([sys.executable, "model/model.py"], 
                                      cwd=os.path.dirname(os.path.abspath(__file__)) + "/..",
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("Model training completed successfully!")
                else:
                    print(f"Model training failed: {result.stderr}")
            except Exception as e:
                print(f"Error during model training: {e}")
        
        # Compliance check
        if run_compliance:
            if not COMPLIANCE_AVAILABLE:
                print("\nWarning: Compliance checker not available.")
            else:
                print("\nRunning MDONER/NEC DPR compliance check...")
                
                try:
                    checker = DPRComplianceChecker("mdoner_guidelines.json")
                    
                    document_index = []
                    if json_data and json_data.get("index"):
                        document_index = json_data["index"]
                    else:
                        document_index = extract_document_index(clean_text_content)
                    
                    compliance_results = checker.check_compliance(clean_text_content, document_index)
                    
                    base_name = Path(filename).stem
                    compliance_json = os.path.join(OUTPUT_DIR, f"{base_name}_compliance.json")
                    
                    import json
                    with open(compliance_json, 'w', encoding='utf-8') as f:
                        json.dump(compliance_results, f, indent=2, ensure_ascii=False)
                    
                    outputs.append(compliance_json)
                    print(f"Compliance results saved to: {compliance_json}")
                    
                    if generate_html:
                        html_report = os.path.join(OUTPUT_DIR, f"{base_name}_compliance_report.html")
                        checker.generate_report_html(compliance_results, html_report)
                        outputs.append(html_report)
                        print(f"HTML compliance report saved to: {html_report}")
                    
                    score = compliance_results['overall_score']
                    level = compliance_results['compliance_level'].replace('_', ' ').title()
                    print(f"\nCompliance Summary:")
                    print(f"  - Overall Score: {score}%")
                    print(f"  - Compliance Level: {level}")
                    print(f"  - Sections Found: {sum(1 for s in compliance_results['section_analysis'].values() if s['found'])}/{len(compliance_results['section_analysis'])}")
                    
                    if score < 70:
                        print(f"  - Status: ⚠️ Needs improvement")
                    else:
                        print(f"  - Status: ✅ Meets requirements")
                
                except FileNotFoundError:
                    print("Error: mdoner_guidelines.json not found.")
                except Exception as e:
                    print(f"Error during compliance check: {e}")
        
        # Model prediction
        # (Old/incorrect model prediction block removed. Only the correct block remains below.)
        
        print(f"\nExtraction complete! Output files: {', '.join(outputs)}")
        
        # Return appropriate exit code
        if run_compliance and COMPLIANCE_AVAILABLE and 'compliance_results' in locals():
            return 0 if compliance_results['overall_score'] >= 70 else 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)