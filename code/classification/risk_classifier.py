import re
from config.enums import RISK_KEYWORDS

PLEASANTRIES = {"thank you", "thanks", "great", "awesome", "helpful", "appreciate"}

def hard_risk_scan(ticket_text):
    text = ticket_text.lower().strip()
    if len(text.split()) < 10 and any(p in text for p in PLEASANTRIES):
        return False, None
    for kw in RISK_KEYWORDS:
        if kw in text:
            return True, kw
    return False, None
