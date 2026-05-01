import re
from config import enums as config

# Short pleasantry messages should never be escalated
PLEASANTRIES = ["thank you", "thanks", "great", "awesome", "helpful", "appreciate"]

def hard_risk_scan(ticket_text):
    """
    Scans the ticket text for any hard-risk keywords.
    Returns (True, matching_keyword) if found, else (False, None).
    """
    text_lower = ticket_text.lower().strip()

    if len(text_lower.split()) < 10 and any(p in text_lower for p in PLEASANTRIES):
        return False, None
        
    for kw in config.RISK_KEYWORDS:
        if kw in text_lower:
            return True, kw
    return False, None
