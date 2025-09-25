#!/usr/bin/env python3
"""
MDONER/NEC DPR Compliance Checker - Standalone Script
AI-powered document compliance validation for government DPR documents
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Import our modules
from compliance_checker import DPRComplianceChecker
from utils import load_file, extract_text, clean_text, extract_document_index


def load_json_document(file_path: str) -> tuple[str, list]:
    """Load document from existing JSON output"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract text and index from JSON
        text_content = data.get('content', '')
        if not text_content and 'text' in data:
            text_content = data['text']
        
        document_index = data.get('index', [])
        
        return text_content, document_index
    
    except Exception as e:
        print(f"Error loading JSON document: {e}")
        return "", []


def extract_document_content(file_path: str) -> tuple[str, list]:
    """Extract content from various document formats"""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.json':
        # Load from existing JSON output
        return load_json_document(str(file_path))
    
    # Extract from original document
    try:
        # Load and extract text
        file_content = load_file(str(file_path))
        raw_text = extract_text(file_content, str(file_path))
        clean_text_content = clean_text(raw_text)
        
        # Extract document index
        document_index = extract_document_index(clean_text_content)
        
        return clean_text_content, document_index
    
    except Exception as e:
        print(f"Error extracting document content: {e}")
        return "", []


def save_compliance_results(results: Dict[str, Any], output_path: str) -> None:
    """Save compliance results to JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Compliance results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results: {e}")


def print_compliance_summary(results: Dict[str, Any]) -> None:
    """Print a concise compliance summary to console"""
    print("\n" + "="*60)
    print("MDONER/NEC DPR COMPLIANCE SUMMARY")
    print("="*60)
    
    print(f"Overall Score: {results['overall_score']}%")
    print(f"Compliance Level: {results['compliance_level'].replace('_', ' ').title()}")
    print(f"Status: {results.get('compliance_description', 'N/A')}")
    
    print(f"\nDocument Statistics:")
    stats = results['document_stats']
    print(f"  • Total Characters: {stats['total_characters']:,}")
    print(f"  • Total Words: {stats['total_words']:,}")
    print(f"  • Has Index: {'Yes' if stats['has_index'] else 'No'}")
    
    print(f"\nSection Analysis:")
    found_sections = 0
    total_required = 0
    
    for section_id, section_data in results['section_analysis'].items():
        status = "✓" if section_data['found'] else "✗"
        score = section_data['score']
        
        print(f"  {status} {section_data['title']}: {score:.1f}%")
        
        if section_data['found']:
            found_sections += 1
        if section_data['required']:
            total_required += 1
    
    print(f"\nSections Found: {found_sections} / {len(results['section_analysis'])} total")
    print(f"Required Sections: {total_required}")
    
    # Quality checks summary
    print(f"\nQuality Checks:")
    qc = results['quality_checks']
    
    fin_status = "✓" if qc['financial_analysis']['has_financial_data'] else "✗"
    tech_status = "✓" if qc['technical_specifications']['has_technical_specs'] else "✗"
    length_status = "✓" if qc['document_length']['meets_minimum'] else "✗"
    
    print(f"  {fin_status} Financial Analysis: {qc['financial_analysis']['financial_mentions']} mentions")
    print(f"  {tech_status} Technical Specifications: Score {qc['technical_specifications']['technical_score']}")
    print(f"  {length_status} Document Length: {qc['document_length']['actual_length']:,} chars")
    
    # Special requirements
    sr = results['special_requirements']
    ne_status = "✓" if sr['northeast_focus']['has_ne_focus'] else "✗"
    print(f"  {ne_status} Northeast Focus: {sr['northeast_focus']['ne_mentions']} mentions")
    
    # Recommendations
    if results['recommendations']:
        print(f"\nKey Recommendations:")
        for i, rec in enumerate(results['recommendations'][:5], 1):
            print(f"  {i}. {rec}")
        
        if len(results['recommendations']) > 5:
            print(f"  ... and {len(results['recommendations']) - 5} more recommendations")
    
    print("="*60)


def main():
    """Main function for standalone compliance checking"""
    parser = argparse.ArgumentParser(
        description="MDONER/NEC DPR Compliance Checker - Validate document compliance with government guidelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python check_compliance.py document.pdf
  python check_compliance.py document.json --output results.json
  python check_compliance.py document.docx --html-report --summary
        """
    )
    
    parser.add_argument(
        "input_file",
        help="Input document file (PDF, DOCX, or JSON from previous extraction)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file for detailed results (default: auto-generated)"
    )
    
    parser.add_argument(
        "--html-report",
        action="store_true",
        help="Generate HTML compliance report"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        default=True,
        help="Print compliance summary to console (default: enabled)"
    )
    
    parser.add_argument(
        "--guidelines",
        default="mdoner_guidelines.json",
        help="Path to guidelines JSON file (default: mdoner_guidelines.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not Path(args.input_file).exists():
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Validate guidelines file
    if not Path(args.guidelines).exists():
        print(f"Error: Guidelines file not found: {args.guidelines}")
        print("Please ensure mdoner_guidelines.json is in the current directory")
        sys.exit(1)
    
    print("Starting MDONER/NEC DPR compliance check...")
    print(f"Input document: {args.input_file}")
    
    try:
        # Initialize compliance checker
        checker = DPRComplianceChecker(args.guidelines)
        
        # Extract document content
        print("Extracting document content...")
        document_text, document_index = extract_document_content(args.input_file)
        
        if not document_text:
            print("Error: No text content extracted from document")
            sys.exit(1)
        
        print(f"Extracted {len(document_text):,} characters, {len(document_index)} index entries")
        
        # Run compliance check
        print("Running compliance analysis...")
        compliance_results = checker.check_compliance(document_text, document_index)
        
        # Generate output filename if not specified
        input_path = Path(args.input_file)
        if args.output:
            output_json = args.output
        else:
            output_json = f"{input_path.stem}_compliance_results.json"
        
        # Save JSON results
        save_compliance_results(compliance_results, output_json)
        
        # Generate HTML report if requested
        if args.html_report:
            html_output = f"{input_path.stem}_compliance_report.html"
            checker.generate_report_html(compliance_results, html_output)
            print(f"HTML report saved to: {html_output}")
        
        # Print summary
        if args.summary:
            print_compliance_summary(compliance_results)
        
        # Exit with appropriate code
        score = compliance_results['overall_score']
        if score >= 70:
            print(f"\n✓ Document meets basic compliance standards ({score}%)")
            sys.exit(0)
        else:
            print(f"\n✗ Document does not meet compliance standards ({score}%)")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"Error during compliance check: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()