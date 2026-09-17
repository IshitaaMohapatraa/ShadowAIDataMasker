import re

# Centralized compiled regex rules for structured PII & credential detection
RULES = {
    "AWS_ACCESS_KEY": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    "OPENAI_API_KEY": re.compile(r"\bsk-[a-zA-Z0-9]{32,}\b"),
    "GENERIC_API_KEY": re.compile(r"\b(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?([a-zA-Z0-9\-_]{16,})['\"]?\b", re.IGNORECASE),
    "CREDIT_CARD": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    "PHONE_NUMBER": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
}