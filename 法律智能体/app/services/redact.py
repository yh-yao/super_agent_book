import re

PII_PATTERNS = [
    re.compile(r"[\w\.-]+@[\w\.-]+"),             # emails
    re.compile(r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b"), # US SSN-like
    re.compile(r"\b\+?\d{1,3}[- ]?\d{3}[- ]?\d{3}[- ]?\d{4}\b") # phones
]

def redact(text: str) -> str:
    masked = text
    for pat in PII_PATTERNS:
        masked = pat.sub("[REDACTED]", masked)
    return masked
