from typing import Dict, List, Tuple
from src.rules import RULES

class TextSanitizer:
    def __init__(self, rules_config: Dict = None):
        self.rules = rules_config or RULES

    def sanitize(self, text: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Scans input string against regex rules and replaces sensitive tokens.
        Returns a tuple of (sanitized_text, redacting_log).
        """
        if not isinstance(text, str):
            raise TypeError("Input payload must be a string.")

        sanitized_text = text
        detections = []

        for category, pattern in self.rules.items():
            matches = list(pattern.finditer(sanitized_text))
            
            # Process in reverse order to keep correct index offsets
            for match in reversed(matches):
                start, end = match.span()
                matched_val = match.group(0)
                placeholder = f"[REDACTED_{category}]"
                
                # Perform surgical string slice swap
                sanitized_text = sanitized_text[:start] + placeholder + sanitized_text[end:]
                
                detections.append({
                    "category": category,
                    "original_snippet": matched_val[:4] + "..." if len(matched_val) > 4 else "***",
                    "placeholder": placeholder
                })

        return sanitized_text, detections