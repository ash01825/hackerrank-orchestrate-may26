import os
from enum import Enum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

INPUT_COLUMNS = ["issue", "subject", "company"]
OUTPUT_COLUMNS = ["issue", "subject", "company", "response", "product_area", "status", "request_type", "justification"]

class Status(str, Enum):
    REPLIED = "replied"
    ESCALATED = "escalated"

class RequestType(str, Enum):
    PRODUCT_ISSUE = "product_issue"
    FEATURE_REQUEST = "feature_request"
    BUG = "bug"
    INVALID = "invalid"

class Ecosystem(str, Enum):
    HACKERRANK = "HackerRank"
    CLAUDE = "Claude"
    VISA = "Visa"
    UNKNOWN = "unknown"

RISK_KEYWORDS = [
    "fraud", "unauthorized", "charged twice",
    "account hacked", "payment failed",
    "legal", "gdpr", "compromise"
]
