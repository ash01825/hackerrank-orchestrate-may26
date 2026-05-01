import re
import config

def hard_risk_scan(ticket_text):
    """
    Scans the ticket text for any hard-risk keywords.
    Returns (True, matching_keyword) if found, else (False, None).
    """
    text_lower = ticket_text.lower()
    for kw in config.RISK_KEYWORDS:
        if kw in text_lower:
            return True, kw
    return False, None
