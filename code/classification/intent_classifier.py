from utils.llm_client import call_llm

def classify_ticket(ticket_text):
    messages = [
        {"role": "system", "content": "You are a support classification engine. Extract the request_type (bug, product_issue, feature_request, invalid). Also determine 'is_emergency' (boolean) - true ONLY if the ticket describes a severe PLATFORM-WIDE outage (e.g. the main website/app is down for all users, all submissions across all tests failing, the entire service is inaccessible). is_emergency=false if the failure is isolated to: a user's own application, a personal project, a third-party API integration (e.g. AWS Bedrock, Slack), a single feature, or a single user's account. Finally, extract a clean, concise 'search_query' (3-6 words) representing the core technical intent to be used for documentation retrieval (ignore pleasantries and conversational filler). If the ticket reports a specific feature as down or unavailable, orient the search_query toward availability or access status (e.g. 'resume builder access availability') rather than general usage. Output strict JSON with keys 'request_type', 'is_emergency', and 'search_query'."},
        {"role": "user", "content": f"Ticket:\n{ticket_text}\n\nOutput JSON with keys 'request_type', 'is_emergency', and 'search_query'."}
    ]

    result = call_llm(messages, response_format=True)
    if isinstance(result, dict):
        return result
    return {"request_type": "product_issue", "is_emergency": False, "search_query": ticket_text}
