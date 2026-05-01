import pandas as pd
import os
import sys

import config
import indexer
import router
import retriever
import classifier
import decision
import responder
import validator

def run_pipeline(input_csv, output_csv):
    print("Loading data and building index...")
    idx = indexer.get_indexer()
    print("Data loaded.")
    
    # Check if we need to map column names. Sample CSV has capital letters.
    df = pd.read_csv(input_csv)
    
    # Map column names if they are capitalized
    col_map = {c: c.lower() for c in df.columns}
    df = df.rename(columns=col_map)
    
    output_rows = []
    
    with open(config.LOG_FILE, "a") as log:
        for i, row in df.iterrows():
            ticket_id = i
            issue = str(row.get("issue", ""))
            subject = str(row.get("subject", ""))
            company = str(row.get("company", ""))
            
            full_text = f"{subject}\n{issue}"
            
            # 1. Router (Hard risks)
            has_risk, kw = router.hard_risk_scan(full_text)
            
            # 2. Classifier
            req_type = classifier.classify_request_type(full_text)
            
            # 3. Retriever
            eco_map = {
                "HackerRank": config.Ecosystem.HACKERRANK.value,
                "Claude": config.Ecosystem.CLAUDE.value,
                "Visa": config.Ecosystem.VISA.value
            }
            ecosystem = eco_map.get(company, config.Ecosystem.UNKNOWN.value)
            
            top_chunks = retriever.retrieve(full_text, ecosystem)
            top_chunk = top_chunks[0] if top_chunks else None
            
            prod_area = classifier.classify_product_area(top_chunk)
            
            # 4. Decision
            status, just = decision.decide_status(has_risk, top_chunks)
            
            # 5. Responder
            if status == config.Status.REPLIED.value:
                resp = responder.generate_response(top_chunk)
            else:
                resp = "I am sorry, this is out of scope from my capabilities."
                
            # 6. Validate
            out_row = {
                "status": status,
                "product_area": prod_area,
                "response": resp,
                "justification": just,
                "request_type": req_type
            }
            validated_row = validator.validate_row(out_row)
            
            output_rows.append(validated_row)
            
            log.write(f"--- Ticket {ticket_id} ---\n")
            log.write(f"Ecosystem: {ecosystem}\n")
            log.write(f"Risk: {has_risk} ({kw})\n")
            log.write(f"Status: {status}\n")
            log.write(f"Req Type: {req_type}\n")
            log.write(f"Justification: {just}\n\n")

    out_df = pd.DataFrame(output_rows)
    out_df.to_csv(output_csv, index=False)
    print(f"Pipeline finished. Output written to {output_csv}")

if __name__ == "__main__":
    # Use sample tickets for testing if passed "test"
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_pipeline(config.SAMPLE_TICKETS_CSV, config.OUTPUT_CSV)
    else:
        run_pipeline(config.TICKETS_CSV, config.OUTPUT_CSV)
