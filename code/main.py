import pandas as pd
import sys
import os
from dotenv import load_dotenv

load_dotenv()

from config import enums
from config.enums import INPUT_COLUMNS, OUTPUT_COLUMNS
from retrieval import hybrid
from classification import risk_classifier, intent_classifier
from validation import evidence_validator
from decision import decision_engine
from utils.schema_validator import OutputRow

def run_pipeline(input_csv, output_csv):
    print("Loading data and building index...")
    retriever = hybrid.get_retriever()
    print("Hybrid index ready.")
    
    df = pd.read_csv(input_csv)
    col_map = {c: c.lower() for c in df.columns}
    df = df.rename(columns=col_map)
    total = len(df)
    print(f"Loaded {total} tickets. Starting pipeline...\n")
    
    output_rows = []
    
    with open("pipeline_debug.log", "a") as log:
        for i, row in df.iterrows():
            issue = str(row.get("issue", ""))
            subject = str(row.get("subject", ""))
            company = str(row.get("company", ""))
            
            full_text = f"{subject}\n{issue}"
            print(f"[{i+1}/{total}] Ticket: {subject[:50]!r}")
            
            # 1. Hard Risks
            print(f"  [1/5] Risk scan...")
            has_risk, kw = risk_classifier.hard_risk_scan(full_text)
            
            # 2. LLM Classification
            print(f"  [2/5] LLM classifying intent...")
            req_type = intent_classifier.classify_ticket(full_text)
            
            # 3. Hybrid Retrieval
            print(f"  [3/5] Retrieving relevant docs...")
            eco_map = {
                "HackerRank": "HackerRank",
                "Claude": "Claude",
                "Visa": "Visa"
            }
            ecosystem = eco_map.get(company, "unknown")
            top_chunks = retriever.retrieve(full_text, ecosystem)
            
            # Set product_area from the top chunk's directory path to avoid LLM hallucination
            if top_chunks:
                prod_area = top_chunks[0].get("section_path", "general")
            else:
                prod_area = "general"
            
            # 4. LLM Evidence Validation & Drafting
            print(f"  [4/5] Validating evidence (LLM)...")
            validation_result = evidence_validator.validate_and_compose(full_text, top_chunks)
            
            # 5. Decision Engine
            print(f"  [5/5] Decision...")
            top_score = top_chunks[0].get("hybrid_score", 0.0) if top_chunks else 0.0
            status, just = decision_engine.decide_status(has_risk, validation_result, top_score)
            print(f"  ✅ Done → status={status} | product_area={prod_area} | request_type={req_type}\n")
            
            # 6. Responder
            if status == "replied":
                resp = validation_result.get("response", "")
                if not resp:
                    resp = "I am sorry, this is out of scope from my capabilities."
            else:
                resp = "I am sorry, this is out of scope from my capabilities."
                
            # 7. Validate
            try:
                out_row = OutputRow(
                    issue=issue,
                    subject=subject,
                    company=company,
                    response=resp,
                    product_area=prod_area,
                    status=status,
                    request_type=req_type,
                    justification=just
                )
                output_rows.append(out_row.model_dump())
            except Exception as e:
                # Fallback on strict enum fail
                output_rows.append({
                    "issue": issue, "subject": subject, "company": company,
                    "response": "I am sorry, this is out of scope from my capabilities.",
                    "product_area": "general", "status": "escalated",
                    "request_type": "product_issue", "justification": f"Schema error: {e}"
                })
            
            log.write(f"Ticket {i} -> Status: {status} | Score: {top_score:.2f} | Val: {validation_result.get('confidence', 0.0)}\n")

    out_df = pd.DataFrame(output_rows, columns=OUTPUT_COLUMNS)
    out_df.to_csv(output_csv, index=False)
    print(f"Pipeline finished. Output written to {output_csv}")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TICKETS_CSV = os.path.join(BASE_DIR, "support_tickets", "support_tickets.csv")
    SAMPLE_TICKETS_CSV = os.path.join(BASE_DIR, "support_tickets", "sample_support_tickets.csv")
    OUTPUT_CSV = os.path.join(BASE_DIR, "support_tickets", "output.csv")
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_pipeline(SAMPLE_TICKETS_CSV, OUTPUT_CSV)
    else:
        run_pipeline(TICKETS_CSV, OUTPUT_CSV)
