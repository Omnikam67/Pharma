"""
Exact symptom-to-medicine mapping with multilingual normalization.
"""

from __future__ import annotations

import re


SYMPTOM_MEDICINE_MAP = {
    "headache": {
        "en": {"symptom": "Headache", "medicines": ["Paracetamol apodiscounter 500 mg", "Nurofen 200 mg"]},
        "mr": {"symptom": "\u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940", "medicines": ["Paracetamol apodiscounter 500 mg", "Nurofen 200 mg"]},
        "hi": {"symptom": "\u0938\u093f\u0930\u0926\u0930\u094d\u0926", "medicines": ["Paracetamol apodiscounter 500 mg", "Nurofen 200 mg"]},
    },
    "stomach pain": {
        "en": {"symptom": "Stomach Pain", "medicines": ["Iberogast Classic", "Kijimea Reizdarm PRO", "Paracetamol apodiscounter 500 mg"]},
        "mr": {"symptom": "\u092a\u094b\u091f\u0926\u0941\u0916\u0940", "medicines": ["Iberogast Classic", "Kijimea Reizdarm PRO", "Paracetamol apodiscounter 500 mg"]},
        "hi": {"symptom": "\u092a\u0947\u091f \u0926\u0930\u094d\u0926", "medicines": ["Iberogast Classic", "Kijimea Reizdarm PRO", "Paracetamol apodiscounter 500 mg"]},
    },
    "heartburn": {
        "en": {"symptom": "Heartburn", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
        "mr": {"symptom": "\u0906\u092e\u094d\u0932\u092a\u093f\u0924\u094d\u0924", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
        "hi": {"symptom": "\u0938\u0940\u0928\u0947 \u092e\u0947\u0902 \u091c\u0932\u0928", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
    },
    "bloating": {
        "en": {"symptom": "Bloating", "medicines": ["Kijimea Reizdarm PRO", "Iberogast Classic"]},
        "mr": {"symptom": "\u092a\u094b\u091f \u092b\u0941\u0917\u0923\u0947", "medicines": ["Kijimea Reizdarm PRO", "Iberogast Classic"]},
        "hi": {"symptom": "\u092a\u0947\u091f \u092b\u0942\u0932\u0928\u093e", "medicines": ["Kijimea Reizdarm PRO", "Iberogast Classic"]},
    },
    "nausea": {
        "en": {"symptom": "Nausea", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
        "mr": {"symptom": "\u092e\u0933\u092e\u0933", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
        "hi": {"symptom": "\u092e\u093f\u091a\u0932\u0940", "medicines": ["Paracetamol apodiscounter 500 mg", "Kijimea Reizdarm PRO"]},
    },
    "muscle pain": {
        "en": {"symptom": "Muscle Pain", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
        "mr": {"symptom": "\u0938\u094d\u0928\u093e\u092f\u0942 \u0926\u0941\u0916\u0940", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
        "hi": {"symptom": "\u092e\u093e\u0902\u0938\u092a\u0947\u0936\u0940 \u0926\u0930\u094d\u0926", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
    },
    "joint pain": {
        "en": {"symptom": "Joint Pain", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
        "mr": {"symptom": "\u0938\u093e\u0902\u0927\u0947\u0926\u0941\u0916\u0940", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
        "hi": {"symptom": "\u091c\u094b\u0921\u093c\u094b\u0902 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926", "medicines": ["Diclo-ratiopharm Schmerzgel", "Paracetamol apodiscounter 500 mg"]},
    },
    "chest pain": {
        "en": {"symptom": "Chest Pain", "medicines": []},
        "mr": {"symptom": "\u091b\u093e\u0924\u0940\u0924 \u0926\u0941\u0916\u0923\u0947", "medicines": []},
        "hi": {"symptom": "\u0938\u0940\u0928\u0947 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926", "medicines": []},
    },
    "heart pain": {
        "en": {"symptom": "Heart Pain", "medicines": []},
        "mr": {"symptom": "\u0939\u0943\u0926\u092f\u093e\u0924 \u0926\u0941\u0916\u0923\u0947", "medicines": []},
        "hi": {"symptom": "\u0926\u093f\u0932 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926", "medicines": []},
    },
    "fever": {
        "en": {"symptom": "Fever", "medicines": ["Paracetamol apodiscounter 500 mg"]},
        "mr": {"symptom": "\u0924\u093e\u092a", "medicines": ["Paracetamol apodiscounter 500 mg"]},
        "hi": {"symptom": "\u092c\u0941\u0916\u093e\u0930", "medicines": ["Paracetamol apodiscounter 500 mg"]},
    },
    "cough": {
        "en": {"symptom": "Cough", "medicines": []},
        "mr": {"symptom": "\u0916\u094b\u0915\u0932\u093e", "medicines": []},
        "hi": {"symptom": "\u0916\u093e\u0902\u0938\u0940", "medicines": []},
    },
    "cold": {
        "en": {"symptom": "Cold", "medicines": []},
        "mr": {"symptom": "\u0938\u0930\u094d\u0926\u0940", "medicines": []},
        "hi": {"symptom": "\u091c\u0941\u0915\u093e\u092e", "medicines": []},
    },
    "sinus": {
        "en": {"symptom": "Sinus Congestion", "medicines": ["Sinupret\u00ae Saft"]},
        "mr": {"symptom": "\u0938\u093e\u0907\u0928\u0938 \u092c\u0928\u094d\u0926", "medicines": ["Sinupret\u00ae Saft"]},
        "hi": {"symptom": "\u0938\u093e\u0907\u0928\u0938 \u091c\u092e\u093e\u0935", "medicines": ["Sinupret\u00ae Saft"]},
    },
    "blocked nose": {
        "en": {"symptom": "Blocked Nose", "medicines": ["Sinupret\u00ae Saft"]},
        "mr": {"symptom": "\u0928\u093e\u0915 \u092c\u0902\u0926", "medicines": ["Sinupret\u00ae Saft"]},
        "hi": {"symptom": "\u0928\u093e\u0915 \u092c\u0902\u0926", "medicines": ["Sinupret\u00ae Saft"]},
    },
    "itchy eyes": {
        "en": {"symptom": "Itchy Eyes", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Livocab\u00ae direkt Augentropfen, 0,05 % Augentropfen, Suspension"]},
        "mr": {"symptom": "\u0921\u094b\u0933\u094d\u092f\u093e\u0902\u092e\u0927\u094d\u092f\u0947 \u0916\u093e\u091c", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Livocab\u00ae direkt Augentropfen, 0,05 % Augentropfen, Suspension"]},
        "hi": {"symptom": "\u0906\u0902\u0916\u094b\u0902 \u092e\u0947\u0902 \u0916\u0941\u091c\u0932\u0940", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Livocab\u00ae direkt Augentropfen, 0,05 % Augentropfen, Suspension"]},
    },
    "red eyes": {
        "en": {"symptom": "Red Eyes", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Cromo-ratiopharm\u00ae Augentropfen Einzeldosis"]},
        "mr": {"symptom": "\u0932\u093e\u0932 \u0921\u094b\u0933\u0947", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Cromo-ratiopharm\u00ae Augentropfen Einzeldosis"]},
        "hi": {"symptom": "\u0932\u093e\u0932 \u0906\u0902\u0916\u0947\u0902", "medicines": ["Vividrin\u00ae iso EDO\u00ae antiallergische Augentropfen", "Cromo-ratiopharm\u00ae Augentropfen Einzeldosis"]},
    },
    "constipation": {
        "en": {"symptom": "Constipation", "medicines": ["DulcoLax\u00ae Drag\u00e9es, 5 mg magensaftresistente Tabletten"]},
        "mr": {"symptom": "\u092c\u0926\u094d\u0927\u0915\u094b\u0937\u094d\u0920\u0924\u093e", "medicines": ["DulcoLax\u00ae Drag\u00e9es, 5 mg magensaftresistente Tabletten"]},
        "hi": {"symptom": "\u0915\u092c\u094d\u091c", "medicines": ["DulcoLax\u00ae Drag\u00e9es, 5 mg magensaftresistente Tabletten"]},
    },
    "diarrhea": {
        "en": {"symptom": "Diarrhea", "medicines": ["Loperamid akut - 1 A Pharma\u00ae, 2 mg Hartkapseln"]},
        "mr": {"symptom": "\u091c\u0941\u0932\u093e\u092c", "medicines": ["Loperamid akut - 1 A Pharma\u00ae, 2 mg Hartkapseln"]},
        "hi": {"symptom": "\u0926\u0938\u094d\u0924", "medicines": ["Loperamid akut - 1 A Pharma\u00ae, 2 mg Hartkapseln"]},
    },
    "fatigue": {
        "en": {"symptom": "Fatigue", "medicines": ["NORSAN Omega-3 Total"]},
        "mr": {"symptom": "\u0925\u0915\u0935\u093e", "medicines": ["NORSAN Omega-3 Total"]},
        "hi": {"symptom": "\u0925\u0915\u093e\u0928", "medicines": ["NORSAN Omega-3 Total"]},
    },
    "exhaustion": {
        "en": {"symptom": "Exhaustion", "medicines": ["NORSAN Omega-3 Total"]},
        "mr": {"symptom": "\u0916\u0942\u092a \u0925\u0915\u0935\u093e", "medicines": ["NORSAN Omega-3 Total"]},
        "hi": {"symptom": "\u092c\u0939\u0941\u0924 \u0925\u0915\u093e\u0928", "medicines": ["NORSAN Omega-3 Total"]},
    },
}

SYMPTOM_ALIASES = {
    "head pain": "headache",
    "head ache": "headache",
    "migraine": "headache",
    "head hurts": "headache",
    "pain in head": "headache",
    "belly pain": "stomach pain",
    "abdominal pain": "stomach pain",
    "gastric issue": "stomach pain",
    "indigestion": "stomach pain",
    "burning chest": "heartburn",
    "acid reflux": "heartburn",
    "heart ache": "heart pain",
    "cardiac pain": "heart pain",
    "swelling": "bloating",
    "gas": "bloating",
    "back pain": "muscle pain",
    "neck pain": "muscle pain",
    "body ache": "muscle pain",
    "body pain": "muscle pain",
    "leg pain": "muscle pain",
    "pain in leg": "muscle pain",
    "pain in my leg": "muscle pain",
    "pain in the leg": "muscle pain",
    "legs hurt": "muscle pain",
    "leg ache": "muscle pain",
    "sore legs": "muscle pain",
    "thigh pain": "muscle pain",
    "calf pain": "muscle pain",
    "leg strain": "muscle pain",
    "leg sprain": "joint pain",
    "ankle pain": "joint pain",
    "knee pain": "joint pain",
    "shoulder pain": "joint pain",
    "arthritis": "joint pain",
    "rheumatism": "joint pain",
    "high temperature": "fever",
    "sinus congestion": "sinus",
    "sinus problem": "sinus",
    "sinus pressure": "sinus",
    "stuffy nose": "blocked nose",
    "blocked nostril": "blocked nose",
    "nose blocked": "blocked nose",
    "nasal congestion": "blocked nose",
    "cold and cough": "cough",
    "itchy eye": "itchy eyes",
    "eye itching": "itchy eyes",
    "itchy red eyes": "itchy eyes",
    "red eye": "red eyes",
    "eye redness": "red eyes",
    "allergic eyes": "itchy eyes",
    "loose motion": "diarrhea",
    "loose motions": "diarrhea",
    "motions": "diarrhea",
    "hard stool": "constipation",
    "cannot pass stool": "constipation",
    "tiredness": "fatigue",
    "weak": "fatigue",
    "energy loss": "fatigue",
    "\u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940": "headache",
    "\u0938\u0930\u0926\u0930\u094d\u0926": "headache",
    "\u092e\u093e\u091d\u0947 \u0921\u094b\u0915\u0947 \u0926\u0941\u0916\u0924 \u0906\u0939\u0947": "headache",
    "\u092e\u0932\u093e \u0921\u094b\u0915\u0947\u0926\u0941\u0916\u0940 \u0939\u094b\u0924 \u0906\u0939\u0947": "headache",
    "\u092a\u094b\u091f \u0926\u0941\u0916\u0924 \u0906\u0939\u0947": "stomach pain",
    "\u092a\u094b\u091f \u0926\u0941\u0916\u0924\u092f": "stomach pain",
    "\u091b\u093e\u0924\u0940\u0924 \u091c\u0933\u091c\u0933": "heartburn",
    "\u0939\u0943\u0926\u092f\u093e\u0924 \u0926\u0941\u0916\u0924\u0947": "heart pain",
    "\u092e\u0933\u092e\u0933 \u0939\u094b\u0924 \u0906\u0939\u0947": "nausea",
    "\u092e\u093e\u0902\u0938\u092a\u0947\u0936\u0940 \u0926\u0941\u0916\u0940": "muscle pain",
    "\u0938\u093e\u0902\u0927\u0947 \u0926\u0941\u0916\u0940": "joint pain",
    "\u0924\u093e\u092a \u0906\u0939\u0947": "fever",
    "\u0916\u094b\u0915\u0932\u093e \u0906\u0939\u0947": "cough",
    "\u0938\u0930\u094d\u0926\u0940 \u0906\u0939\u0947": "cold",
    "\u0925\u0915\u0935\u093e \u0906\u0932\u093e \u0906\u0939\u0947": "fatigue",
    "\u0938\u093f\u0930 \u0926\u0930\u094d\u0926": "headache",
    "\u0938\u093f\u0930\u0926\u0930\u094d\u0926": "headache",
    "\u092e\u0948\u0902 \u0938\u093f\u0930\u0926\u0930\u094d\u0926 \u0938\u0947 \u092a\u0930\u0947\u0936\u093e\u0928 \u0939\u0942\u0901": "headache",
    "\u092e\u0941\u091d\u0947 \u0938\u093f\u0930\u0926\u0930\u094d\u0926 \u0939\u0948": "headache",
    "\u092a\u0947\u091f \u0926\u0930\u094d\u0926": "stomach pain",
    "\u092a\u0947\u091f \u0926\u0941\u0916\u0928\u093e": "stomach pain",
    "\u090f\u0938\u093f\u0921\u093f\u091f\u0940": "heartburn",
    "\u0926\u093f\u0932 \u092e\u0947\u0902 \u0926\u0930\u094d\u0926": "heart pain",
    "\u091c\u0940 \u092e\u093f\u091a\u0932\u093e\u0928\u093e": "nausea",
    "\u092e\u093e\u0902\u0938\u092a\u0947\u0936\u0940 \u0926\u0930\u094d\u0926": "muscle pain",
    "\u091c\u094b\u0921\u093c \u0926\u0930\u094d\u0926": "joint pain",
    "\u092c\u0941\u0916\u093e\u0930": "fever",
    "\u0916\u093e\u0902\u0938\u0940": "cough",
    "\u091c\u0941\u0915\u093e\u092e": "cold",
    "\u0925\u0915\u093e\u0928": "fatigue",
    "\u0915\u092e\u091c\u094b\u0930\u0940": "exhaustion",
}

SYMPTOM_GUIDANCE = {
    "headache": {
        "best_option_contains": "nurofen 200 mg",
        "summary": {"en": "This medicine is commonly used for headache and migraine relief."},
        "best_reason": {"en": "It contains ibuprofen and is one of the most suitable options from your list for headache pain relief."},
        "use": {"en": ["Take after food.", "Use the usual dose only as directed on the pack or by your doctor."]},
        "helps_with": {"en": ["Headache", "Migraine", "Body pain"]},
        "tablet_intro": {"en": "One related alternative from your list:"},
    },
    "muscle pain": {
        "best_option_contains": "diclo ratiopharm schmerzgel",
        "summary": {"en": "This looks most similar to muscle or soft-tissue pain."},
        "best_reason": {"en": "Best for local muscle pain because it works directly on the painful area and may help with pain, strain, and swelling."},
        "use": {"en": ["Apply a thin layer on the painful area 2-3 times daily.", "Massage gently unless the area is very tender.", "Do not apply on broken skin."]},
        "helps_with": {"en": ["Muscle pain", "Sprain or strain", "Mild swelling"]},
        "tablet_intro": {"en": "If pain feels stronger, you can consider this related tablet from your list:"},
    },
    "joint pain": {
        "best_option_contains": "diclo ratiopharm schmerzgel",
        "summary": {"en": "This sounds closer to a joint-related pain problem."},
        "best_reason": {"en": "A topical anti-inflammatory gel is often the most targeted first option for mild joint pain."},
        "use": {"en": ["Apply on the affected joint area 2-3 times daily.", "Massage gently around the joint.", "Avoid use on cuts or irritated skin."]},
        "helps_with": {"en": ["Joint pain", "Movement-related pain", "Mild inflammation"]},
        "tablet_intro": {"en": "If pain is stronger, this related tablet may help:"},
    },
}

GENERIC_GUIDANCE = {
    "summary": {"en": "This looks like the closest available match from your current medicine list."},
    "best_reason": {"en": "This option appears most relevant based on your symptom description and the medicines currently in stock."},
    "use": {"en": []},
    "helps_with": {"en": []},
    "tablet_intro": {"en": "One related alternative from your list:"},
    "best_option_contains": "",
}

TEXT_PREFIX_PATTERNS = [
    r"\bi\s+have\b",
    r"\bi\s+am\s+having\b",
    r"\bi\s+feel\b",
    r"\bi\s+got\b",
    r"\bmy\b",
    r"\bim\b",
    r"\bi'?m\b",
    r"\bme\b",
    r"\bmine\b",
    r"\bplease\b",
    r"\bneed\b",
    r"\bwant\b",
    r"\bhelp\b",
    r"\bwith\b",
    r"\u092e\u0932\u093e",
    r"\u092e\u093e\u091d\u094d\u092f\u093e",
    r"\u092e\u093e\u091d\u0947",
    r"\u0906\u0939\u0947",
    r"\u0939\u094b\u0924 \u0906\u0939\u0947",
    r"\u092e\u0941\u091d\u0947",
    r"\u092e\u0947\u0930\u0947",
    r"\u0939\u0948",
]


class SymptomMapper:
    """Service to map symptoms to medicines with exact matching."""

    @staticmethod
    def normalize_symptom(symptom: str) -> str:
        if not symptom:
            return ""

        normalized = str(symptom).lower().strip()
        normalized = re.sub(r"[^\w\s]", " ", normalized, flags=re.UNICODE)
        normalized = normalized.replace("_", " ")
        for pattern in TEXT_PREFIX_PATTERNS:
            normalized = re.sub(pattern, " ", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\b(a|an|the|and|to|for|of|on|in)\b", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    @classmethod
    def _find_symptom_key(cls, symptom: str) -> str | None:
        normalized_symptom = cls.normalize_symptom(symptom)
        if not normalized_symptom:
            return None

        for key in SYMPTOM_MEDICINE_MAP:
            if cls.normalize_symptom(key) == normalized_symptom:
                return key

        for alias, base_symptom in SYMPTOM_ALIASES.items():
            normalized_alias = cls.normalize_symptom(alias)
            if not normalized_alias:
                continue
            if normalized_alias == normalized_symptom:
                return base_symptom
            if normalized_alias in normalized_symptom or normalized_symptom in normalized_alias:
                return base_symptom

        for key, translation_dict in SYMPTOM_MEDICINE_MAP.items():
            for lang_data in translation_dict.values():
                translated_symptom = cls.normalize_symptom(lang_data.get("symptom", ""))
                if translated_symptom and translated_symptom == normalized_symptom:
                    return key

        for key in SYMPTOM_MEDICINE_MAP:
            normalized_key = cls.normalize_symptom(key)
            if normalized_key in normalized_symptom or normalized_symptom in normalized_key:
                return key

        return None

    @classmethod
    def find_matching_medicines(cls, symptom: str, language: str = "en") -> dict:
        symptom_key = cls._find_symptom_key(symptom)
        if not symptom_key:
            return {
                "found": False,
                "symptom": symptom,
                "medicines": [],
                "language": language,
                "message": f"I could not find medicines for '{symptom}'. Please consult a doctor.",
            }

        mapping = SYMPTOM_MEDICINE_MAP.get(symptom_key, {})
        language_data = mapping.get(language, mapping.get("en", {}))
        medicines = language_data.get("medicines", [])
        symptom_translated = language_data.get("symptom", symptom)

        if not medicines:
            return {
                "found": True,
                "symptom": symptom_translated,
                "medicines": [],
                "language": language,
                "message": f"No medicines are currently available to treat '{symptom_translated}'. Please consult a doctor.",
                "not_available": True,
            }

        return {
            "found": True,
            "symptom": symptom_translated,
            "medicines": medicines,
            "language": language,
            "message": None,
            "matched_key": symptom_key,
        }

    @classmethod
    def build_recommendation_response(cls, symptom_result: dict, original_query: str = "", language: str = "en") -> str:
        medicines = symptom_result.get("medicines", []) or []
        symptom_name = symptom_result.get("symptom") or original_query or "your symptoms"

        if not medicines:
            return symptom_result.get("message") or f"I could not find medicines for '{symptom_name}'. Please consult a doctor."

        matched_key = symptom_result.get("matched_key") or cls._find_symptom_key(original_query or symptom_name)
        guide = SYMPTOM_GUIDANCE.get(matched_key or "", GENERIC_GUIDANCE)
        best_hint = guide.get("best_option_contains", "")
        ai_selection = symptom_result.get("ai_selection") or {}

        def normalized_name(item: dict) -> str:
            return cls.normalize_symptom(item.get("name", ""))

        best = next((item for item in medicines if best_hint and best_hint in normalized_name(item)), medicines[0])
        alternatives = [item for item in medicines if item is not best][:1]
        best_reason = ai_selection.get("best_reason") or guide.get("best_reason", {}).get(
            "en",
            "This option looks most suitable from the medicines currently available in your list.",
        )

        response_lines = [
            f"**Medicine that works best for {symptom_name}**",
            "",
            f"**{best.get('name', 'Recommended medicine')}**",
            "",
            guide.get("summary", {}).get("en", "This is one of the closest available matches for your symptoms."),
            "",
            "**Why I recommend this**",
            f"- {best_reason}",
        ]

        if best.get("price") not in (None, ""):
            response_lines.append(f"- Price: ${best.get('price')}")
        if isinstance(best.get("stock"), int):
            response_lines.append(f"- In stock: {best.get('stock')}")

        helps_with = guide.get("helps_with", {}).get("en", [])
        if helps_with:
            response_lines.extend(["", "**Helpful for**"])
            response_lines.extend([f"- {item}" for item in helps_with])

        use_steps = guide.get("use", {}).get("en", [])
        if use_steps:
            response_lines.extend(["", "**How to use**"])
            response_lines.extend([f"- {step}" for step in use_steps])

        if alternatives:
            response_lines.extend(["", "**One related alternative**"])
            for item in alternatives:
                line = f"- **{item.get('name', 'Medicine')}**"
                if item.get("price") not in (None, ""):
                    line += f" (${item.get('price')})"
                if ai_selection.get("related_reason"):
                    line += f" - {ai_selection.get('related_reason')}"
                response_lines.append(line)
        else:
            response_lines.extend(["", "**Related option**", "- No close second option from your current in-stock list."])

        response_lines.extend(["", "If you want, I can help you order this medicine."])
        return "\n".join(response_lines)
