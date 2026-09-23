import re
import math

# --- REGEX PATTERNS FOR KNOWN SECRETS & PII ---
PATTERNS = {
    # Cloud & API Secrets
    "OPENAI_API_KEY": r"sk-[a-zA-Z0-9]{32,}",
    "AWS_ACCESS_KEY_ID": r"(?:A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "AWS_SECRET_ACCESS_KEY": r"(?i)aws_secret_access_key\s*=\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
    "GITHUB_TOKEN": r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36}",
    "GOOGLE_API_KEY": r"AIzaSy[a-zA-Z0-9\-_]{33}",
    "SLACK_WEBHOOK": r"https://hooks\.slack\.com/services/T[a-zA-Z0-9_]+/B[a-zA-Z0-9_]+/[a-zA-Z0-9_]+",
    "JWT_TOKEN": r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+",
    
    # Financial & Identifiers (India & Global)
    "CREDIT_CARD": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b",
    "PAN_CARD": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "AADHAAR_NUMBER": r"\b[2-9]{1}[0-9]{3}\s[0-9]{4}\s[0-9]{4}\b",
    
    # Network & Contact PII
    "EMAIL_ADDRESS": r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",
    "IPV4_ADDRESS": r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b",
}

# --- SHANNON ENTROPY DETECTOR ---
def calculate_entropy(data: str) -> float:
    """Calculates the Shannon entropy of a given string."""
    if not data:
        return 0.0
    entropy = 0.0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy

def find_high_entropy_tokens(text: str, threshold: float = 4.5, min_length: int = 20) -> list[str]:
    """Finds unstructured, high-entropy tokens (e.g. random secret keys) that bypass regex."""
    tokens = re.findall(r"\b[A-Za-z0-9/+=_-]+\b", text)
    suspicious = []
    
    for token in tokens:
        if len(token) >= min_length:
            # Skip standard text/words with repetitive low complexity
            if calculate_entropy(token) >= threshold:
                suspicious.append(token)
                
    return suspicious