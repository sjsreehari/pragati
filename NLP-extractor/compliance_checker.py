import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DPRComplianceChecker:
    
    def __init__(self, guidelines_path: str = "mdoner_guidelines.json"):
        self.guidelines_path = Path(guidelines_path)
        self.guidelines = self._load_guidelines()
        self.required_sections = self.guidelines["mdoner_dpr_guidelines"]["required_sections"]
        self.quality_checks = self.guidelines["mdoner_dpr_guidelines"]["quality_checks"]
        self.compliance_levels = self.guidelines["mdoner_dpr_guidelines"]["compliance_levels"]
        self.special_requirements = self.guidelines["mdoner_dpr_guidelines"]["special_requirements"]
    
    def _load_guidelines(self) -> Dict:
        try:
            with open(self.guidelines_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Guidelines file not found: {self.guidelines_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in guidelines file: {e}")
            raise
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _find_section_in_text(self, text: str, section_keywords: List[str]) -> Dict:
        text_lower = text.lower()
        lines = text.split('\n')
        
        best_match = {"found": False, "content": "", "line_number": -1, "confidence": 0.0}
        
        for i, line in enumerate(lines):
            line_clean = re.sub(r'[^\w\s]', ' ', line.lower()).strip()
            
            for keyword_phrase in section_keywords:
                # Calculate similarity
                similarity = self._similarity_score(line_clean, keyword_phrase.lower())
                
                keyword_words = keyword_phrase.lower().split()
                words_found = sum(1 for word in keyword_words if word in line_clean)
                keyword_coverage = words_found / len(keyword_words) if keyword_words else 0
                
                confidence = (similarity * 0.6) + (keyword_coverage * 0.4)
                
                if confidence > best_match["confidence"] and confidence > 0.4:
                    start_idx = max(0, i - 2)
                    end_idx = min(len(lines), i + 20)
                    content = '\n'.join(lines[start_idx:end_idx])
                    
                    best_match = {
                        "found": True,
                        "content": content,
                        "line_number": i,
                        "confidence": confidence,
                        "matched_keyword": keyword_phrase
                    }
        
        return best_match
    
    def _check_financial_details(self, text: str) -> Dict:
        financial_patterns = [
            r'(?:rs\.?|rupees?|₹|inr)\s*\d+(?:,\d+)*(?:\.\d+)?(?:\s*(?:crore|lakh|thousand))?',
            r'\d+(?:,\d+)*(?:\.\d+)?\s*(?:crore|lakh|thousand)',
            r'budget\s*:\s*[\d,]+',
            r'cost\s*estimate',
            r'total\s*cost',
            r'expenditure'
        ]
        
        financial_matches = []
        for pattern in financial_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            financial_matches.extend(matches)
        
        return {
            "has_financial_data": len(financial_matches) > 0,
            "financial_mentions": len(financial_matches),
            "examples": financial_matches[:5]
        }
    
    def _check_technical_specifications(self, text: str) -> Dict:
        technical_patterns = [
            r'specification[s]?',
            r'technical\s+detail[s]?',
            r'implementation',
            r'methodology',
            r'design\s+parameter[s]?',
            r'system\s+requirement[s]?',
            r'infrastructure',
            r'equipment',
            r'technology'
        ]
        
        technical_score = 0
        found_patterns = []
        
        for pattern in technical_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                technical_score += min(matches, 3)  # Cap at 3 per pattern
                found_patterns.append(pattern)
        
        return {
            "has_technical_specs": technical_score > 5,
            "technical_score": technical_score,
            "found_patterns": found_patterns
        }
    
    def _check_northeast_focus(self, text: str) -> Dict:
        """Check if document has Northeast India focus"""
        ne_keywords = self.special_requirements["northeast_focus"]["keywords"]
        
        matches = 0
        found_keywords = []
        
        for keyword in ne_keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            keyword_matches = len(re.findall(pattern, text, re.IGNORECASE))
            if keyword_matches > 0:
                matches += keyword_matches
                found_keywords.append(keyword)
        
        return {
            "has_ne_focus": matches > 0,
            "ne_mentions": matches,
            "found_keywords": found_keywords
        }
    
    def check_compliance(self, document_text: str, document_index: List[Dict] = None) -> Dict:
        """Main compliance checking function"""
        logger.info("Starting compliance check...")
        
        compliance_report = {
            "timestamp": datetime.now().isoformat(),
            "document_stats": {
                "total_characters": len(document_text),
                "total_words": len(document_text.split()),
                "has_index": document_index is not None and len(document_index) > 0
            },
            "section_analysis": {},
            "quality_checks": {},
            "special_requirements": {},
            "overall_score": 0,
            "compliance_level": "",
            "recommendations": []
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        for section_id, section_info in self.required_sections.items():
            logger.info(f"Checking section: {section_info['title']}")
            
            section_match = self._find_section_in_text(
                document_text, 
                section_info["keywords"]
            )
            
            section_score = 0
            if section_match["found"]:
                section_score = section_match["confidence"] * 100
                
                content_words = len(section_match["content"].split())
                if content_words > 100:
                    section_score = min(section_score + 10, 100)
                elif content_words > 50:
                    section_score = min(section_score + 5, 100)
            
            compliance_report["section_analysis"][section_id] = {
                "title": section_info["title"],
                "required": section_info["required"],
                "weight": section_info["weight"],
                "found": section_match["found"],
                "score": section_score,
                "confidence": section_match.get("confidence", 0),
                "matched_keyword": section_match.get("matched_keyword", ""),
                "content_preview": section_match["content"][:200] + "..." if section_match["content"] else ""
            }
            
            if section_info["required"]:
                weighted_score = (section_score * section_info["weight"]) / 100
                total_weighted_score += weighted_score
                total_weight += section_info["weight"]
        
        # Quality checks
        compliance_report["quality_checks"]["financial_analysis"] = self._check_financial_details(document_text)
        compliance_report["quality_checks"]["technical_specifications"] = self._check_technical_specifications(document_text)
        compliance_report["quality_checks"]["document_length"] = {
            "meets_minimum": len(document_text) >= self.quality_checks["document_length_minimum"],
            "actual_length": len(document_text),
            "required_minimum": self.quality_checks["document_length_minimum"]
        }
        
        # Special requirements
        compliance_report["special_requirements"]["northeast_focus"] = self._check_northeast_focus(document_text)
        
        # Calculate overall score
        if total_weight > 0:
            compliance_report["overall_score"] = round(total_weighted_score / total_weight * 100, 1)
        else:
            compliance_report["overall_score"] = 0
        
        # Determine compliance level
        score = compliance_report["overall_score"]
        for level, info in self.compliance_levels.items():
            if info["score_range"][0] <= score <= info["score_range"][1]:
                compliance_report["compliance_level"] = level
                compliance_report["compliance_description"] = info["description"]
                break
        
        # Generate recommendations
        compliance_report["recommendations"] = self._generate_recommendations(compliance_report)
        
        logger.info(f"Compliance check complete. Overall score: {score}")
        return compliance_report
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations based on compliance analysis"""
        recommendations = []
        
        # Section-specific recommendations
        for section_id, section_data in report["section_analysis"].items():
            if section_data["required"] and not section_data["found"]:
                recommendations.append(f"Add missing required section: '{section_data['title']}'")
            elif section_data["found"] and section_data["score"] < 60:
                recommendations.append(f"Improve content quality in '{section_data['title']}' section")
        
        # Quality check recommendations
        if not report["quality_checks"]["financial_analysis"]["has_financial_data"]:
            recommendations.append("Include detailed financial analysis with budget breakdown and cost estimates")
        
        if not report["quality_checks"]["technical_specifications"]["has_technical_specs"]:
            recommendations.append("Add comprehensive technical specifications and implementation methodology")
        
        if not report["quality_checks"]["document_length"]["meets_minimum"]:
            recommendations.append("Expand document content to meet minimum length requirements")
        
        # Special requirement recommendations
        if not report["special_requirements"]["northeast_focus"]["has_ne_focus"]:
            recommendations.append("Emphasize Northeast India relevance and regional development impact")
        
        # Overall score recommendations
        if report["overall_score"] < 70:
            recommendations.append("Overall document needs significant improvement to meet MDONER/NEC standards")
        elif report["overall_score"] < 85:
            recommendations.append("Document is good but could benefit from minor enhancements")
        
        return recommendations
    
    def generate_report_html(self, compliance_data: Dict, output_path: str = None) -> str:
        """Generate HTML compliance report"""
        if output_path is None:
            output_path = f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        # Get compliance level info
        level_info = self.compliance_levels.get(compliance_data["compliance_level"], {})
        level_color = level_info.get("color", "gray")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MDONER/NEC DPR Compliance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .score-badge {{ display: inline-block; padding: 10px 20px; border-radius: 20px; color: white; font-weight: bold; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #f8f9fa; }}
                .found {{ border-left-color: #27ae60; }}
                .not-found {{ border-left-color: #e74c3c; }}
                .recommendations {{ background: #fff3cd; padding: 15px; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #ecf0f1; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MDONER/NEC DPR Compliance Report</h1>
                <p>Generated on: {compliance_data['timestamp']}</p>
            </div>
            
            <h2>Overall Compliance Score</h2>
            <div class="score-badge" style="background-color: {level_color};">
                {compliance_data['overall_score']}% - {compliance_data['compliance_level'].replace('_', ' ').title()}
            </div>
            <p><strong>Status:</strong> {compliance_data.get('compliance_description', 'N/A')}</p>
            
            <h2>Document Statistics</h2>
            <div class="metric">Characters: {compliance_data['document_stats']['total_characters']:,}</div>
            <div class="metric">Words: {compliance_data['document_stats']['total_words']:,}</div>
            <div class="metric">Has Index: {'Yes' if compliance_data['document_stats']['has_index'] else 'No'}</div>
            
            <h2>Section Analysis</h2>
            <table>
                <tr>
                    <th>Section</th>
                    <th>Required</th>
                    <th>Found</th>
                    <th>Score</th>
                    <th>Weight</th>
                </tr>"""
        
        for section_id, section_data in compliance_data["section_analysis"].items():
            found_status = "✓" if section_data["found"] else "✗"
            found_class = "found" if section_data["found"] else "not-found"
            html_content += f"""
                <tr class="{found_class}">
                    <td>{section_data['title']}</td>
                    <td>{'Yes' if section_data['required'] else 'No'}</td>
                    <td>{found_status}</td>
                    <td>{section_data['score']:.1f}%</td>
                    <td>{section_data['weight']}</td>
                </tr>"""
        
        html_content += """
            </table>
            
            <h2>Quality Checks</h2>"""
        
        # Financial Analysis
        fin_data = compliance_data["quality_checks"]["financial_analysis"]
        html_content += f"""
            <div class="section {'found' if fin_data['has_financial_data'] else 'not-found'}">
                <h3>Financial Analysis</h3>
                <p>Status: {'Present' if fin_data['has_financial_data'] else 'Missing'}</p>
                <p>Financial mentions: {fin_data['financial_mentions']}</p>
            </div>"""
        
        # Technical Specifications
        tech_data = compliance_data["quality_checks"]["technical_specifications"]
        html_content += f"""
            <div class="section {'found' if tech_data['has_technical_specs'] else 'not-found'}">
                <h3>Technical Specifications</h3>
                <p>Status: {'Present' if tech_data['has_technical_specs'] else 'Missing'}</p>
                <p>Technical score: {tech_data['technical_score']}</p>
            </div>"""
        
        # Northeast Focus
        ne_data = compliance_data["special_requirements"]["northeast_focus"]
        html_content += f"""
            <div class="section {'found' if ne_data['has_ne_focus'] else 'not-found'}">
                <h3>Northeast India Focus</h3>
                <p>Status: {'Present' if ne_data['has_ne_focus'] else 'Missing'}</p>
                <p>Northeast mentions: {ne_data['ne_mentions']}</p>
                <p>Found keywords: {', '.join(ne_data['found_keywords'][:5])}</p>
            </div>"""
        
        # Recommendations
        if compliance_data["recommendations"]:
            html_content += """
            <h2>Recommendations</h2>
            <div class="recommendations">
                <ul>"""
            for rec in compliance_data["recommendations"]:
                html_content += f"<li>{rec}</li>"
            html_content += """
                </ul>
            </div>"""
        
        html_content += """
        </body>
        </html>"""
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to: {output_path}")
        return output_path


def main():
    """Test the compliance checker"""
    checker = DPRComplianceChecker()
    
    # Example usage
    sample_text = """
    INTRODUCTION ABOUT THE PROJECT
    
    This project aims to develop infrastructure in Northeast India.
    The total cost is Rs. 50 crore.
    
    TECHNICAL SPECIFICATIONS
    
    The project will use modern technology and equipment.
    Implementation will follow standard methodology.
    """
    
    result = checker.check_compliance(sample_text)
    print(f"Compliance Score: {result['overall_score']}%")
    print(f"Level: {result['compliance_level']}")


if __name__ == "__main__":
    main()