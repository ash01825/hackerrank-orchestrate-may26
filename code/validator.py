import config

def validate_row(row):
    # Enforce enums
    if row["status"] not in [e.value for e in config.Status]:
        row["status"] = config.Status.ESCALATED.value
        
    if row["request_type"] not in [e.value for e in config.RequestType]:
        row["request_type"] = config.RequestType.PRODUCT_ISSUE.value
        
    # Ensure no empty fields
    for col in config.OUTPUT_COLUMNS:
        if col not in row or not row[col]:
            row[col] = "N/A"
            
    return {col: row[col] for col in config.OUTPUT_COLUMNS}
