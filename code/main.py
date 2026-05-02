import pandas as pd
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from config.enums import INPUT_COLUMNS, OUTPUT_COLUMNS, Status
from retrieval import hybrid
from classification import risk_classifier, intent_classifier
from validation.evidence_validator import validate_and_compose, compose_response
from decision import decision_engine
from utils.schema_validator import OutputRow

COMPANY_TO_ECOSYSTEM = {
    "HackerRank": "HackerRank",
    "Claude": "Claude",
    "Visa": "Visa",
}

PLEASANTRY_WORDS = {"thank you", "thanks", "great", "awesome"}

def _deflect(issue, subject, company, friendly=False):
    if friendly:
        response = "Happy to help! Let me know if you need anything else."
    else:
        response = "Thank you for reaching out. Your question doesn't appear to be related to our support topics. If you have a product-related question, please provide more details and we'll be happy to help."
    return {
        "issue": issue, "subject": subject, "company": company,
        "response": response, "product_area": "general",
        "status": "replied", "request_type": "invalid",
        "justification": "No matching evidence. Replied with generic deflection.",
    }

def _escalate(issue, subject, company, request_type, reason, response=None):
    return {
        "issue": issue, "subject": subject, "company": company,
        "response": response or "I am sorry, this is out of scope from my capabilities.",
        "product_area": "general", "status": "escalated",
        "request_type": request_type, "justification": reason,
    }

def process_ticket(retriever, issue, subject, company):
    full_text = f"{subject}\n{issue}".strip()

    has_risk, _ = risk_classifier.hard_risk_scan(full_text)

    intent = intent_classifier.classify_ticket(full_text)
    req_type = intent.get("request_type", "product_issue")
    is_emergency = intent.get("is_emergency", False)
    search_query = intent.get("search_query", full_text)

    if is_emergency:
        return _escalate(issue, subject, company, req_type,
                         "LLM detected emergency/outage condition.",
                         "This appears to be a critical system issue. Escalating to human support immediately.")

    ecosystem = COMPANY_TO_ECOSYSTEM.get(company, "unknown")
    combined_query = f"{full_text}\n{search_query}"
    chunks = retriever.retrieve(combined_query, ecosystem, top_k=5)

    if not chunks:
        if not has_risk:
            text_lower = issue.lower()
            is_pleasantry = len(text_lower.split()) < 10 and any(p in text_lower for p in PLEASANTRY_WORDS)
            return _deflect(issue, subject, company, friendly=is_pleasantry)

    prod_area = chunks[0].get("section_path", "general") if chunks else "general"
    top_score = chunks[0].get("hybrid_score", 0.0) if chunks else 0.0

    validation = validate_and_compose(full_text, chunks)
    status, justification = decision_engine.decide_status(has_risk, validation, top_score)

    if status == Status.REPLIED.value:
        response = (validation.get("response") or "").strip()
        if not response and chunks:
            response = compose_response(full_text, chunks)
        if not response:
            response = "Thank you for reaching out. Please contact our support team for further assistance."
    else:
        response = "I am sorry, this is out of scope from my capabilities."

    try:
        row = OutputRow(
            issue=issue, subject=subject, company=company,
            response=response, product_area=prod_area,
            status=status, request_type=req_type, justification=justification,
        )
        return row.model_dump()
    except Exception as e:
        return _escalate(issue, subject, company, "product_issue", f"Schema error: {e}")


def run_pipeline(input_csv, output_csv, use_sample=False):
    print("Loading data and building index...")
    retriever = hybrid.get_retriever()
    print("Index ready.\n")

    df = pd.read_csv(input_csv)
    df = df.rename(columns={c: c.lower() for c in df.columns})
    total = len(df)
    print(f"Loaded {total} tickets.\n")

    results = []
    for i, row in df.iterrows():
        issue = "" if pd.isna(row.get("issue")) else str(row["issue"]).strip()
        subject = "" if pd.isna(row.get("subject")) else str(row["subject"]).strip()
        company = "" if pd.isna(row.get("company")) else str(row["company"]).strip()

        print(f"[{i+1}/{total}] {subject[:60]!r}")
        result = process_ticket(retriever, issue, subject, company)
        results.append(result)
        print(f"  → status={result['status']} | area={result['product_area']}\n")

    out_df = pd.DataFrame(results, columns=OUTPUT_COLUMNS)
    out_df.to_csv(output_csv, index=False)
    print(f"Done. Output → {output_csv}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tickets_csv = os.path.join(base, "support_tickets", "support_tickets.csv")
    sample_csv = os.path.join(base, "support_tickets", "sample_support_tickets.csv")
    output_csv = os.path.join(base, "support_tickets", "output.csv")

    use_sample = "test" in sys.argv
    input_csv = sample_csv if use_sample else tickets_csv
    run_pipeline(input_csv, output_csv)
