"""
Tests for multilingual symptom mapping and language detection.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.language_detector import LanguageDetector
from app.services.symptom_mapping import SymptomMapper


class TestSymptomMapping:
    def test_exact_match_english_headache(self):
        result = SymptomMapper.find_matching_medicines("headache", "en")
        assert result["found"] is True
        assert any("Paracetamol" in str(m) for m in result["medicines"])
        assert result["language"] == "en"

    def test_marathi_headache_sentence_maps_correctly(self):
        result = SymptomMapper.find_matching_medicines("\u092e\u0932\u093e \u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940 \u0939\u094b\u0924 \u0906\u0939\u0947", "mr")
        assert result["found"] is True
        assert result["matched_key"] == "headache"
        assert any("Nurofen" in str(m) for m in result["medicines"])

    def test_hindi_headache_sentence_maps_correctly(self):
        result = SymptomMapper.find_matching_medicines("\u092e\u0941\u091d\u0947 \u0938\u093f\u0930\u0926\u0930\u094d\u0926 \u0939\u0948", "hi")
        assert result["found"] is True
        assert result["matched_key"] == "headache"

    def test_exact_match_marathi_stomach_pain(self):
        result = SymptomMapper.find_matching_medicines("\u092a\u094b\u091f\u0926\u0941\u0916\u0940", "mr")
        assert result["found"] is True
        assert len(result["medicines"]) > 0
        assert result["language"] == "mr"

    def test_exact_match_hindi_fever(self):
        result = SymptomMapper.find_matching_medicines("\u092c\u0941\u0916\u093e\u0930", "hi")
        assert result["found"] is True
        assert result["language"] == "hi"

    def test_alias_matching(self):
        result1 = SymptomMapper.find_matching_medicines("belly pain", "en")
        result2 = SymptomMapper.find_matching_medicines("stomach pain", "en")
        assert result1["found"] is True
        assert result2["found"] is True

    def test_not_available_symptom(self):
        result = SymptomMapper.find_matching_medicines("heart pain", "en")
        assert result["found"] is True
        assert result["not_available"] is True
        assert result["medicines"] == []

    def test_unsupported_symptom(self):
        result = SymptomMapper.find_matching_medicines("xyz_invalid_symptom_xyz", "en")
        assert result["found"] is False
        assert result["medicines"] == []

    def test_case_insensitive(self):
        result1 = SymptomMapper.find_matching_medicines("HEADACHE", "en")
        result2 = SymptomMapper.find_matching_medicines("HeAdAcHe", "en")
        result3 = SymptomMapper.find_matching_medicines("headache", "en")
        assert result1["found"] == result2["found"] == result3["found"] is True

    def test_leg_pain_alias_matching(self):
        result = SymptomMapper.find_matching_medicines("I feel leg pain", "en")
        assert result["found"] is True
        assert result["matched_key"] == "muscle pain"

    def test_recommendation_builder(self):
        sample = {
            "found": True,
            "symptom": "Headache",
            "matched_key": "headache",
            "language": "en",
            "medicines": [
                {"name": "Nurofen 200 mg", "price": 10, "stock": 5},
                {"name": "Paracetamol apodiscounter 500 mg", "price": 4, "stock": 20},
            ],
        }
        text = SymptomMapper.build_recommendation_response(sample, "headache", "en")
        assert "best" in text.lower()
        assert "Nurofen 200 mg" in text
        assert "How to use" in text


class TestLanguageDetection:
    def test_english_detection(self):
        lang, confidence = LanguageDetector.detect_language("I have a headache")
        assert lang == "en"
        assert confidence > 0.5

    def test_marathi_detection(self):
        lang, confidence = LanguageDetector.detect_language("\u092e\u0932\u093e \u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940 \u0906\u0939\u0947")
        assert lang == "mr"
        assert confidence > 0.5

    def test_hindi_detection(self):
        lang, confidence = LanguageDetector.detect_language("\u092e\u0941\u091d\u0947 \u0938\u093f\u0930\u0926\u0930\u094d\u0926 \u0939\u0948")
        assert lang == "hi"
        assert confidence > 0.5

    def test_mixed_language_keeps_devanagari_detection(self):
        lang, _ = LanguageDetector.detect_language("I feel \u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940")
        assert lang in {"mr", "hi"}

    def test_supported_languages(self):
        supported = LanguageDetector.get_available_languages()
        assert "en" in supported
        assert "mr" in supported
        assert "hi" in supported
