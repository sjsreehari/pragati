import pandas as pd
import re
import json
from datetime import datetime
import os

def extract_parameters_from_text(text_content, filename):
    """
    Convert extracted DPR text to CSV format matching training data structure
    """
    # Initialize parameters dictionary matching your training CSV columns
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
            parameters['Project Name'] = os.path.splitext(filename)[0].replace('_', ' ').title()
    
    # Determine Sector based on content
    text_lower = text_content.lower()
    if any(keyword in text_lower for keyword in ['e-vidhan', 'digital', 'computer', 'software', 'application', 'ict']):
        parameters['Sector'] = 'Information Technology'
    elif any(keyword in text_lower for keyword in ['road', 'construction', 'transport', 'highway', 'bridge']):
        parameters['Sector'] = 'Transport and Communication'
    elif any(keyword in text_lower for keyword in ['education', 'school', 'college', 'training', 'it.i']):
        parameters['Sector'] = 'Education'
    elif any(keyword in text_lower for keyword in ['health', 'medical', 'hospital', 'clinic']):
        parameters['Sector'] = 'Health'
    elif any(keyword in text_lower for keyword in ['water', 'supply', 'irrigation', 'flood']):
        parameters['Sector'] = 'Irrigation and Flood Control'
    elif any(keyword in text_lower for keyword in ['agriculture', 'farming', 'crop', 'horticulture']):
        parameters['Sector'] = 'Agriculture and Allied'
    else:
        parameters['Sector'] = 'Infrastructure'
    
    # Extract Scheme
    scheme_match = re.search(r'Scheme[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if scheme_match:
        parameters['Scheme'] = scheme_match.group(1).strip()
    else:
        parameters['Scheme'] = 'National e-Vidhan Application (NeVA)'
    
    # Extract Sub Scheme
    sub_scheme_match = re.search(r'Sub Scheme[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if sub_scheme_match:
        parameters['Sub Scheme'] = sub_scheme_match.group(1).strip()
    else:
        parameters['Sub Scheme'] = parameters['Scheme']
    
    # Extract Executing Department
    dept_match = re.search(r'Executing Department[:\s]*([^\n,]+)', text_content, re.IGNORECASE)
    if dept_match:
        parameters['Executing Department'] = dept_match.group(1).strip()
    else:
        parameters['Executing Department'] = 'Legislative Assembly Secretariat'
    
    # Extract Approved Cost
    cost_patterns = [
        r'Rs[\s\.]*([0-9,]+[\.]?[0-9]*)\s*(lakh|crore|cr)',
        r'₹[\s\.]*([0-9,]+[\.]?[0-9]*)',
        r'Approved Cost[:\s]*Rs\.?\s*([0-9,]+)',
        r'Tentative Outlay[:\s]*Rs\.?\s*([0-9,]+)',
        r'estimated cost of Rs\.?\s*([0-9,]+)',
        r'cost of Rs\.?\s*([0-9,]+)'
    ]
    
    cost_found = False
    for pattern in cost_patterns:
        cost_match = re.search(pattern, text_content, re.IGNORECASE)
        if cost_match:
            if isinstance(cost_match.groups(), tuple) and len(cost_match.groups()) > 1:
                cost_value = cost_match.group(1).replace(',', '')
                unit = cost_match.group(2).lower() if cost_match.group(2) else ''
            else:
                cost_value = cost_match.group(1).replace(',', '') if cost_match.group(1) else cost_match.group(0)
                unit = ''
            
            if cost_value.replace('.', '').isdigit():
                cost_num = float(cost_value)
                if 'lakh' in unit:
                    cost_num *= 0.01  # Convert lakh to crore
                parameters['Approved Cost'] = str(round(cost_num, 2))
                cost_found = True
                break
    
    # Set dates
    current_date = datetime.now().strftime('%d-%m-%Y')
    parameters['Sanctioned Date'] = current_date
    
    future_date = (datetime.now() + pd.DateOffset(years=2)).strftime('%d-%m-%Y')
    parameters['Scheduled Completion Date'] = future_date
    
    return parameters

def convert_text_to_csv(text_file_path, output_csv_path=None):
    """
    Main function to convert text file to CSV for prediction
    """
    # Read the extracted text
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text_content = file.read()
    
    # Extract parameters
    filename = os.path.basename(text_file_path)
    parameters = extract_parameters_from_text(text_content, filename)
    
    # Create DataFrame
    df = pd.DataFrame([parameters])
    
    # Ensure correct column order
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
    
    # Set output path if not provided
    if output_csv_path is None:
        base_name = os.path.splitext(filename)[0]
        output_csv_path = f"output/{base_name}_for_prediction.csv"
    
    # Save CSV
    df.to_csv(output_csv_path, index=False)
    print(f"CSV file created successfully: {output_csv_path}")
    print(f"Extracted {len(df)} DPR record(s)")
    
    return df, output_csv_path

def main():
    # File paths based on your project structure
    text_file_path = "output/Model_DPR_Final 2.0.txt"
    output_csv_path = "output/extracted_dpr_for_prediction.csv"
    
    try:
        df, csv_path = convert_text_to_csv(text_file_path, output_csv_path)
        print("\nExtracted Data:")
        print(df.to_string(index=False))
        
    except FileNotFoundError:
        print(f"Error: Text file '{text_file_path}' not found.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()