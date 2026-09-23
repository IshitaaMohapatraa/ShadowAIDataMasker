import pytest
from src.sanitizer import TextSanitizer

def test_api_key_redaction():
    raw = "My OpenAI key is sk-1234567890abcdef1234567890abcdef"
    sanitized, vault = TextSanitizer.sanitize(raw)
    assert "sk-1234567890abcdef1234567890abcdef" not in sanitized
    assert "[REDACTED_OPENAI_API_KEY_" in sanitized
    assert len(vault) == 1

def test_indian_pii_redaction():
    raw = "PAN is ABCDE1234F and Aadhaar is 2345 6789 0123"
    sanitized, vault = TextSanitizer.sanitize(raw)
    assert "ABCDE1234F" not in sanitized
    assert "2345 6789 0123" not in sanitized
    assert "[REDACTED_PAN_CARD_" in sanitized
    assert "[REDACTED_AADHAAR_NUMBER_" in sanitized

def test_high_entropy_detection():
    raw = "Secret token is zX9kL2pQ8vR4mW7nT1yU3iO5aS6dF0gH"
    sanitized, vault = TextSanitizer.sanitize(raw)
    assert "zX9kL2pQ8vR4mW7nT1yU3iO5aS6dF0gH" not in sanitized
    assert "[REDACTED_HIGH_ENTROPY_SECRET_" in sanitized