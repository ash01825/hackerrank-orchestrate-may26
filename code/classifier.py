import config

def classify_request_type(ticket_text):
    text_lower = ticket_text.lower()
    for kw in config.FEATURE_KEYWORDS:
        if kw in text_lower:
            return config.RequestType.FEATURE_REQUEST.value
    for kw in config.BUG_KEYWORDS:
        if kw in text_lower:
            return config.RequestType.BUG.value
            
    if len(ticket_text.strip()) < 10:
        return config.RequestType.INVALID.value
        
    return config.RequestType.PRODUCT_ISSUE.value

def classify_product_area(top_chunk):
    if top_chunk and "section_path" in top_chunk:
        return top_chunk["section_path"].replace("/", "_").replace("-", "_")
    return "general_support"
