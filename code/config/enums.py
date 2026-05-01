import os
from enum import Enum

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
TICKETS_CSV = os.path.join(BASE_DIR, "support_tickets", "support_tickets.csv")
SAMPLE_TICKETS_CSV = os.path.join(BASE_DIR, "support_tickets", "sample_support_tickets.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "support_tickets", "output.csv")
LOG_FILE = os.path.join(BASE_DIR, "pipeline_debug.log")

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
    NONE = "None"
    UNKNOWN = "unknown"

RISK_KEYWORDS = [
    "fraud", "unauthorized", "charged twice",
    "account hacked", "payment failed",
    "legal", "gdpr", "compromise"
]

BUG_KEYWORDS = ["not working", "error", "broken", "fail", "bug", "issue"]
FEATURE_KEYWORDS = ["feature request", "can you add", "it would be nice", "please add"]
