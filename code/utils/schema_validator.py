from pydantic import BaseModel, Field
from typing import Literal

class OutputRow(BaseModel):
    issue: str
    subject: str
    company: str
    response: str
    product_area: str
    status: Literal["replied", "escalated"]
    request_type: Literal["product_issue", "feature_request", "bug", "invalid"]
    justification: str

class ClassificationResult(BaseModel):
    request_type: Literal["product_issue", "feature_request", "bug", "invalid"]
    product_area: str

class ValidationResult(BaseModel):
    answerable: Literal["yes", "no"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
