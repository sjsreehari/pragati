import os
import pandas as pd
from utils import load_file, extract_text, clean_text
import spacy
from transformers import pipeline
import torch

# Try to use GPU for spaCy and transformers if available
spacy_model = "en_core_web_sm"
try:
    import spacy.cli
    spacy.prefer_gpu()
    nlp = spacy.load(spacy_model)
except OSError:
    spacy.cli.download(spacy_model)
    nlp = spacy.load(spacy_model)

# Use GPU for transformers if available
device = 0 if torch.cuda.is_available() else -1
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=device)

def pdf_to_simple_csv(pdf_path, output_csv_path):
    # Extract text from PDF
    file = load_file(pdf_path)
    text = extract_text(file, pdf_path)
    text = clean_text(text)

    import re

    # 1. Project description: Use summarization on the first 1500 words
    text_for_summary = " ".join(text.split()[:1500])
    try:
        summary_result = summarizer(text_for_summary, max_length=60, min_length=20, do_sample=False)
        description = summary_result[0]['summary_text'].replace('\n', ' ').strip()
    except Exception:
        # fallback to regex if summarizer fails
        desc_regex = r'([A-Z][^.\n]*?(construction|development|improvement|rehabilitation|project|scheme|application|upgrade|expansion)[^.\n]*[.])'
        desc_match = re.search(desc_regex, text, re.IGNORECASE)
        description = desc_match.group(0).replace('\n', ' ').strip() if desc_match else ''

    # 2. Budget: Use NER to find MONEY entities, fallback to regex
    # Limit NER to first 2000 words to avoid memory errors
    ner_text = " ".join(text.split()[:2000])
    doc = nlp(ner_text)
    money_ents = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]
    # Try to find the largest budget
    budget = ""
    def parse_money(m):
        # Remove currency symbols and commas
        m_clean = re.sub(r'[^\d.,]', '', m)
        # Prefer numbers with commas as thousands separators
        nums = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+|\d+', m_clean)
        # Filter out numbers that are too short (e.g., '4.12.8' or '4')
        nums = [n for n in nums if len(n.replace(',', '')) > 4]
        try:
            return float(nums[0].replace(',', '')) if nums else 0
        except Exception:
            return 0

    # Broaden budget extraction: match crore/lakh, numbers with spaces, and numbers near budget/cost/amount
    budget = ""
    budget_patterns = [
        r'(?:Rs|₹)[^\d]*(\d[\d,\.]+)',  # Rs/₹ followed by number
        r'(\d+[\d, ]+)(?:\s*crore|\s*lakhs?)',  # number + crore/lakh
        r'(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?)(?:\s*INR)?',  # Indian-style comma numbers
        r'(\d+[\d, ]+)',  # large numbers with spaces/commas
    ]
    budget_values = []
    for pat in budget_patterns:
        for m in re.findall(pat, text, re.IGNORECASE):
            # Normalize crore/lakh
            if isinstance(m, tuple):
                m = m[0]
            m_clean = m.replace(',', '').replace(' ', '')
            # Convert crore/lakh to number
            if re.search(r'crore', text[text.find(m):text.find(m)+30], re.IGNORECASE):
                try:
                    val = float(m_clean) * 1e7
                    if val >= 1e5:
                        budget_values.append(val)
                except:
                    pass
            elif re.search(r'lakh', text[text.find(m):text.find(m)+30], re.IGNORECASE):
                try:
                    val = float(m_clean) * 1e5
                    if val >= 1e5:
                        budget_values.append(val)
                except:
                    pass
            else:
                try:
                    val = float(m_clean)
                    if val >= 1e5:
                        budget_values.append(val)
                except:
                    pass
    # Also look for numbers near budget/cost/amount keywords
    keyword_budget = []
    for match in re.finditer(r'(budget|cost|amount)[^\d]{0,20}(\d[\d,\. ]+)', text, re.IGNORECASE):
        m = match.group(2).replace(',', '').replace(' ', '')
        try:
            val = float(m)
            if val >= 1e5:
                keyword_budget.append(val)
        except:
            pass
    budget_values += keyword_budget
    if budget_values:
        max_budget = max(budget_values)
        budget = f"Budget Rs {max_budget:,.2f}"
    # If regex fails, fallback to spaCy NER
    if not budget:
        money_ents_valid = [m for m in money_ents if parse_money(m) > 0]
        if money_ents_valid:
            money_ents_sorted = sorted(money_ents_valid, key=parse_money, reverse=True)
            # Clean up the entity for CSV output
            best = money_ents_sorted[0]
            best_clean = re.sub(r'[^\d.,]', '', best)
            nums = re.findall(r'\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+|\d+', best_clean)
            if nums:
                budget = f"Budget Rs {nums[0]}"
            else:
                budget = f"Budget {best}"
        else:
            budget = "Budget details not found"
    if not budget:
        budget = "Budget details not found"

    # 3. Timeline: Use NER to find DATE/DURATION, fallback to regex
    timeline = ""
    timeline_ents = [ent.text for ent in doc.ents if ent.label_ in ["DATE", "TIME", "DURATION"] and re.search(r'(month|year)', ent.text, re.IGNORECASE)]
    if timeline_ents:
        timeline = f"Timeline {timeline_ents[0]}"
    else:
        # fallback: regex
        timeline_match = re.search(r'(timeline|duration|completion)[^\d]*(\d+\s*(?:year|month)s?)', text, re.IGNORECASE)
        if timeline_match:
            timeline = f"Timeline {timeline_match.group(2)}"
        else:
            fallback = re.search(r'(within|in|for)[^\d]*(\d+\s*(?:year|month)s?)', text, re.IGNORECASE)
            if fallback:
                timeline = f"Timeline {fallback.group(2)}"
            else:
                fallback2 = re.search(r'(\d+\s*(?:year|month)s?)', text[:1000], re.IGNORECASE)
                timeline = f"Timeline {fallback2.group(1)}" if fallback2 else "Timeline not found"

    # Compose the summary, avoid repeating budget/timeline if already in description
    summary = description.strip()
    if budget and budget not in summary:
        summary = f"{summary} {budget}." if summary else f"{budget}."
    if timeline and timeline not in summary:
        summary = f"{summary} {timeline}." if summary else f"{timeline}."
    summary = summary.replace('..', '.').replace(' .', '.').strip()
    if not description:
        summary = f"Project details not found. {budget}. {timeline}."

    data = [{
        'id': 1,
        'text': summary,
        'label': 'pending',
        'issues': 'budget,timeline'
    }]
    df = pd.DataFrame(data)
    df.to_csv(output_csv_path, index=False)
    print(f"CSV created: {output_csv_path}")

if __name__ == "__main__":
    # Example usage for Model_DPR_Final 2.0.pdf
    pdf_path = os.path.join('text-extractor', 'input', 'Model_DPR_Final 2.0.pdf')
    output_csv_path = os.path.join('text-extractor', 'output', 'Model_DPR_Final 2.0_for_prediction.csv')
    pdf_to_simple_csv(pdf_path, output_csv_path)
