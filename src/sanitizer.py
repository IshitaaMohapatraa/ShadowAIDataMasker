import os
import re
import hashlib
from src.rules import PATTERNS, find_high_entropy_tokens

# Cryptographic salt generated once per server instance lifecycle
SESSION_SALT = os.urandom(16)

class TextSanitizer:
    @staticmethod
    def generate_vault_key(secret_type: str, raw_value: str) -> str:
        """Generates a cryptographically salted, unique placeholder token."""
        salted_bytes = SESSION_SALT + raw_value.encode('utf-8')
        short_hash = hashlib.sha256(salted_bytes).hexdigest()[:8]
        return f"[REDACTED_{secret_type}_{short_hash}]"

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, dict[str, str]]:
        """
        Sanitizes prompt text by masking sensitive patterns.
        Returns a tuple of (sanitized_prompt, vault_mapping).
        """
        sanitized_prompt = text
        vault = {}

        # 1. Deterministic Regex Masking
        for secret_type, pattern in PATTERNS.items():
            matches = set(re.findall(pattern, sanitized_prompt))
            for match in matches:
                # Handle tuple matches from complex regex capture groups
                raw_match = match[0] if isinstance(match, tuple) else match
                placeholder = cls.generate_vault_key(secret_type, raw_match)

                sanitized_prompt = sanitized_prompt.replace(raw_match, placeholder)
                vault[placeholder] = raw_match

        # 2. Heuristic High-Entropy Scanning on Remaining Text
        high_entropy_tokens = find_high_entropy_tokens(sanitized_prompt)
        for token in set(high_entropy_tokens):
            # Avoid re-masking existing redacted placeholders
            if token.startswith("[REDACTED_"):
                continue

            placeholder = cls.generate_vault_key("HIGH_ENTROPY_SECRET", token)
            sanitized_prompt = sanitized_prompt.replace(token, placeholder)
            vault[placeholder] = token

        return sanitized_prompt, vault