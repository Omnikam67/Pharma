"""
Language detection helpers for English, Marathi, and Hindi user messages.
"""

from __future__ import annotations

import re
from typing import Tuple


class LanguageDetector:
    """Detect the most likely language from a short user message."""

    DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")

    ENGLISH_INDICATORS = {
        "order",
        "medicine",
        "product",
        "symptom",
        "pain",
        "drug",
        "price",
        "headache",
        "fever",
        "cold",
        "cough",
        "hello",
        "hi",
        "how",
        "help",
        "paracetamol",
        "ibuprofen",
        "aspirin",
        "thank",
        "thanks",
    }

    MARATHI_INDICATORS = {
        "\u092e\u0932\u093e",
        "\u092e\u0940",
        "\u0924\u0941\u092e\u094d\u0939\u0940",
        "\u0906\u0939\u0947",
        "\u0906\u0939\u0947\u0924",
        "\u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940",
        "\u0938\u0930\u0926\u0930\u094d\u0926",
        "\u092a\u094b\u091f\u0926\u0941\u0916\u0940",
        "\u0924\u093e\u092a",
        "\u0916\u094b\u0915\u0932\u093e",
        "\u0914\u0937\u0927",
        "\u0926\u0941\u0916\u0924",
        "\u0906\u0939\u0947\u092f",
        "\u0915\u093e\u092f",
        "\u0915\u0938\u0947",
        "\u0926\u094d\u092f\u093e",
        "\u0918\u094d\u092f\u093e",
    }

    HINDI_INDICATORS = {
        "\u092e\u0941\u091d\u0947",
        "\u092e\u0948\u0902",
        "\u0906\u092a",
        "\u0939\u0948",
        "\u0939\u0948\u0902",
        "\u0938\u093f\u0930\u0926\u0930\u094d\u0926",
        "\u0938\u0930\u0926\u0930\u094d\u0926",
        "\u092a\u0947\u091f",
        "\u092c\u0941\u0916\u093e\u0930",
        "\u0916\u093e\u0902\u0938\u0940",
        "\u0926\u0935\u093e",
        "\u0926\u0930\u094d\u0926",
        "\u0915\u094d\u092f\u093e",
        "\u0915\u0948\u0938\u0947",
        "\u0926\u0940\u091c\u093f\u090f",
        "\u091a\u093e\u0939\u093f\u090f",
    }

    @classmethod
    def detect_language(cls, text: str) -> Tuple[str, float]:
        if not text or not isinstance(text, str):
            return "en", 0.5

        lowered = text.lower().strip()
        if not lowered:
            return "en", 0.5

        if cls.DEVANAGARI_PATTERN.search(lowered):
            marathi_score = sum(1 for word in cls.MARATHI_INDICATORS if word in lowered)
            hindi_score = sum(1 for word in cls.HINDI_INDICATORS if word in lowered)

            marathi_suffixes = (
                "\u0906\u0939\u0947",
                "\u0906\u0939\u0947\u0924",
                "\u0924\u094b\u092f",
                "\u0924\u0947\u092f",
                "\u0915\u093e",
            )
            if any(suffix in lowered for suffix in marathi_suffixes):
                marathi_score += 1

            if marathi_score > hindi_score:
                return "mr", min(0.99, 0.65 + (marathi_score * 0.08))

            return "hi", min(0.99, 0.65 + (hindi_score * 0.08))

        english_score = sum(1 for word in cls.ENGLISH_INDICATORS if word in lowered)
        return "en", min(0.99, 0.5 + (english_score * 0.08))

    @classmethod
    def get_available_languages(cls) -> list[str]:
        return ["en", "mr", "hi"]

    @classmethod
    def is_supported_language(cls, lang_code: str) -> bool:
        return lang_code in cls.get_available_languages()
