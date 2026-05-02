import argparse
import os
import re
import sys
from collections import Counter, defaultdict

import pandas as pd


REQUIRED_COLUMNS = [
    "issue",
    "subject",
    "company",
    "response",
    "product_area",
    "status",
    "request_type",
    "justification",
]

ALLOWED_STATUS = {"replied", "escalated"}
ALLOWED_REQUEST_TYPES = {"product_issue", "feature_request", "bug", "invalid"}

RISK_PATTERNS = {
    "fraud_identity": [
        r"\bfraud\b",
        r"\bstolen\b",
        r"\bidentity theft\b",
        r"\bunauthorized\b",
        r"\bcard.*blocked\b",
        r"\bblocked.*card\b",
    ],
    "billing_payment": [
        r"\brefund\b",
        r"\bpayment\b",
        r"\bcharged?\b",
        r"\bchargeback\b",
        r"\bdispute\b",
        r"\border id\b",
    ],
    "account_access": [
        r"\badmin\b",
        r"\bowner\b",
        r"\bseat\b",
        r"\brestore.*access\b",
        r"\blost access\b",
        r"\bremove (a )?user\b",
    ],
    "legal_privacy": [
        r"\bgdpr\b",
        r"\blegal\b",
        r"\bprivate info\b",
        r"\bpersonal data\b",
        r"\bdelete my data\b",
    ],
    "outage": [
        r"\bsite is down\b",
        r"\bwebsite.*down\b",
        r"\ball requests.*fail",
        r"\bnone of .* accessible\b",
        r"\bsubmissions across any challenges\b",
    ],
    "prompt_injection": [
        r"\binternal rules\b",
        r"\bdocuments retrieved\b",
        r"\blogic exact\b",
        r"\bsystem prompt\b",
        r"\bignore (the )?(previous|above) instructions\b",
    ],
}

GENERIC_RESPONSE_PATTERNS = [
    r"doesn't appear to be related to our support topics",
    r"please provide more details",
    r"contact our support team for further assistance",
    r"out of scope from my capabilities",
]


def _text(value):
    if pd.isna(value):
        return ""
    return str(value)


def _matches(patterns, text):
    return [pattern for pattern in patterns if re.search(pattern, text, re.IGNORECASE)]


def load_csv(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        print(f"ERROR: missing file: {path}")
        sys.exit(2)


def audit(input_csv, output_csv):
    tickets = load_csv(input_csv)
    output = load_csv(output_csv)

    errors = []
    warnings = []
    risk_hits = defaultdict(list)

    missing_columns = [c for c in REQUIRED_COLUMNS if c not in output.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")

    if len(tickets) != len(output):
        errors.append(f"Row count mismatch: input={len(tickets)} output={len(output)}")

    if not missing_columns:
        bad_status = sorted(set(output["status"].dropna()) - ALLOWED_STATUS)
        if bad_status:
            errors.append(f"Invalid status values: {bad_status}")

        bad_request_types = sorted(set(output["request_type"].dropna()) - ALLOWED_REQUEST_TYPES)
        if bad_request_types:
            errors.append(f"Invalid request_type values: {bad_request_types}")

        for column in ["response", "product_area", "status", "request_type", "justification"]:
            blank_count = output[column].isna().sum() + (output[column].astype(str).str.strip() == "").sum()
            if blank_count:
                errors.append(f"Blank values in {column}: {blank_count}")

        for i, row in output.iterrows():
            issue_text = " ".join([_text(row.get("subject")), _text(row.get("issue"))]).strip()
            response_text = _text(row.get("response"))

            for label, patterns in RISK_PATTERNS.items():
                if _matches(patterns, issue_text):
                    risk_hits[label].append(i + 1)

            generic_hits = _matches(GENERIC_RESPONSE_PATTERNS, response_text)
            if generic_hits and row.get("request_type") != "invalid":
                warnings.append(
                    f"Row {i + 1}: generic response on non-invalid request_type={row.get('request_type')}"
                )

            if row.get("status") == "replied":
                for label in ["fraud_identity", "prompt_injection", "outage"]:
                    if _matches(RISK_PATTERNS[label], issue_text):
                        warnings.append(f"Row {i + 1}: replied despite {label} signal")

    print("Submission audit")
    print("================")
    print(f"Input rows:  {len(tickets)}")
    print(f"Output rows: {len(output)}")

    if not missing_columns:
        print("\nStatus distribution:")
        for key, value in Counter(output["status"]).items():
            print(f"  {key}: {value}")

        print("\nRequest type distribution:")
        for key, value in Counter(output["request_type"]).items():
            print(f"  {key}: {value}")

        if risk_hits:
            print("\nRisk signals by category:")
            for label, rows in sorted(risk_hits.items()):
                preview = ", ".join(map(str, rows[:8]))
                suffix = "" if len(rows) <= 8 else f" (+{len(rows) - 8} more)"
                print(f"  {label}: rows {preview}{suffix}")

    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("\nAudit result: PASS")
    return 0


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    parser = argparse.ArgumentParser(description="Audit Orchestrate submission CSV.")
    parser.add_argument(
        "--input",
        default=os.path.join(repo_root, "support_tickets", "support_tickets.csv"),
        help="Path to support_tickets.csv",
    )
    parser.add_argument(
        "--output",
        default=os.path.join(repo_root, "support_tickets", "output.csv"),
        help="Path to output.csv",
    )
    args = parser.parse_args()
    raise SystemExit(audit(args.input, args.output))


if __name__ == "__main__":
    main()
