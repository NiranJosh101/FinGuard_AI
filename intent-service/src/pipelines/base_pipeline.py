import re
from abc import ABC, abstractmethod

class BasePipeline(ABC):
    def __init__(self, max_characters: int = 500):
        self.max_characters = max_characters
        # Common prompt injection patterns (e.g., "ignore previous instructions")
        self.injection_patterns = [
            re.compile(r"ignore\s+(?:previous|above)\s+instructions", re.IGNORECASE),
            re.compile(r"system\s+override", re.IGNORECASE),
            re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
            re.compile(r"delete\s+all\s+rules", re.IGNORECASE)
        ]

    @abstractmethod
    async def process(self, payload) -> str:
        """
        Ingests the incoming protocol buffer payload, processes its specific 
        media type, and returns a clean, sanitized text string.
        """
        pass

    def sanitize_text(self, text: str) -> str:
        """
        Hard Guardrail: Strips out dangerous injection vectors, normalizes spacing, 
        and enforces maximum character constraints to shield the downstream LLM.
        """
        if not text:
            return ""

        # 1. Enforce length boundary
        sanitized = text.strip()
        if len(sanitized) > self.max_characters:
            sanitized = sanitized[:self.max_characters]

        # 2. Check for explicit prompt injection patterns
        for pattern in self.injection_patterns:
            if pattern.search(sanitized):
                # Hard Guardrail action: Neutralize the string immediately
                raise ValueError("Security Violation: Malicious input pattern detected.")

        # 3. Clean up whitespace/control characters
        sanitized = re.sub(r"\s+", " ", sanitized)
        
        return sanitized