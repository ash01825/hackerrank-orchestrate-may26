from utils.llm_client import call_llm

def classify_ticket(ticket_text):
    messages = [
        {"role": "system", "content": "You are a support classification engine. Extract the request_type (bug, product_issue, feature_request, invalid). Also determine 'is_emergency' (boolean) - true ONLY if the ticket describes a severe system-wide outage, crash, or site inaccessibility requiring immediate human escalation. Output strict JSON with keys 'request_type' and 'is_emergency'."},
        {"role": "user", "content": f"Ticket:\n{ticket_text}\n\nOutput JSON with keys 'request_type' and 'is_emergency'."}
    ]
    
    result = call_llm(messages, response_format=True)
    if isinstance(result, dict):
        return result
    return {"request_type": "product_issue", "is_emergency": False}
