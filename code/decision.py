import config

def decide_status(has_hard_risk, top_chunks):
    if has_hard_risk:
        return config.Status.ESCALATED.value, "Escalated due to sensitive/risk keywords."
        
    if not top_chunks:
        return config.Status.ESCALATED.value, "No relevant evidence found in the corpus."
        
    top_score = top_chunks[0].get("bm25_score", 0.0)
    
    # We require at least some match score to consider it relevant
    if top_score < 0.1:
        return config.Status.ESCALATED.value, "Retrieval confidence too low."
        
    return config.Status.REPLIED.value, "High confidence match in corpus."
