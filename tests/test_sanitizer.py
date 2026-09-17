import pytest
from src.sanitizer import TextSanitizer

@pytest.fixture
def sanitizer():
    return TextSanitizer()

def test_single_secret_masking(sanitizer):
    text = "Deploying with key sk-abcdef1234567890abcdef1234567890 to production."
    clean, logs = sanitizer.sanitize(text)
    assert "sk-abcdef" not in clean
    assert "[REDACTED_OPENAI_API_KEY]" in clean
    assert len(logs) == 1

def test_multiple_pii_masking(sanitizer):
    text = "Reach out to user@test.com or call 555-123-4567."
    clean, logs = sanitizer.sanitize(text)
    assert "user@test.com" not in clean
    assert "555-123-4567" not in clean
    assert "[REDACTED_EMAIL]" in clean
    assert "[REDACTED_PHONE_NUMBER]" in clean
    assert len(logs) == 2

def test_invalid_input_raises_error(sanitizer):
    with pytest.raises(TypeError):
        sanitizer.sanitize(12345)