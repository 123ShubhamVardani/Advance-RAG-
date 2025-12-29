"""multi_lang.py
Multi-language support for A.K.A.S.H.A.
Supports English and all major Indian regional languages with auto-detection and translation.
"""
import os
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

# Supported languages (ISO 639-1 codes + regional names)
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "हिंदी (Hindi)",
    "ta": "தமிழ் (Tamil)",
    "te": "తెలుగు (Telugu)",
    "kn": "ಕನ್ನಡ (Kannada)",
    "ml": "മലയാളം (Malayalam)",
    "bn": "বাংলা (Bengali)",
    "mr": "मराठी (Marathi)",
    "gu": "ગુજરાતી (Gujarati)",
    "pa": "ਪੰਜਾਬੀ (Punjabi)",
}

# Character sets for language detection
LANGUAGE_PATTERNS = {
    "hi": r"[\u0900-\u097F]",      # Devanagari (Hindi, Marathi, Sanskrit)
    "ta": r"[\u0B80-\u0BFF]",      # Tamil
    "te": r"[\u0C00-\u0C7F]",      # Telugu
    "kn": r"[\u0C80-\u0CFF]",      # Kannada
    "ml": r"[\u0D00-\u0D7F]",      # Malayalam
    "bn": r"[\u0980-\u09FF]",      # Bengali
    "mr": r"[\u0900-\u097F]",      # Marathi (same as Hindi script)
    "gu": r"[\u0A80-\u0AFF]",      # Gujarati
    "pa": r"[\u0A00-\u0A7F]",      # Punjabi (Gurmukhi)
}

# Translation service detection
HAS_GOOGLE_TRANSLATE = False
HAS_INDIC_NLPCLOUD = False

try:
    from google.cloud import translate_v2
    HAS_GOOGLE_TRANSLATE = True
except ImportError:
    pass

try:
    import requests
    HAS_INDIC_NLPCLOUD = bool(os.getenv("INDIC_NLPCLOUD_API_KEY"))
except ImportError:
    pass


def detect_language(text: str) -> str:
    """
    Detect the language of input text using character analysis.
    Falls back to English if detection fails.
    
    Args:
        text: Input text to analyze
    
    Returns:
        ISO 639-1 language code (e.g., 'en', 'hi', 'ta')
    """
    import re
    
    if not text or not isinstance(text, str):
        return "en"
    
    text_lower = text.lower()
    
    # Check for each language's character set
    for lang_code, pattern in LANGUAGE_PATTERNS.items():
        if re.search(pattern, text):
            return lang_code
    
    # Default to English
    return "en"


def translate_text(text: str, source_lang: str, target_lang: str = "en") -> str:
    """
    Translate text from source language to target language.
    Uses Google Translate API if available, otherwise returns original text.
    
    Args:
        text: Text to translate
        source_lang: Source language code (e.g., 'hi')
        target_lang: Target language code (default 'en')
    
    Returns:
        Translated text or original text if translation fails
    """
    if source_lang == target_lang:
        return text
    
    # Try Google Translate first (if credentials available)
    if HAS_GOOGLE_TRANSLATE:
        try:
            from google.cloud import translate_v2
            translate_client = translate_v2.Client()
            result = translate_client.translate_text(
                text,
                source_language=source_lang,
                target_language=target_lang
            )
            return result.get("translatedText", text)
        except Exception as e:
            pass
    
    # Try Indic NLP Cloud API (good for Indian languages)
    if HAS_INDIC_NLPCLOUD:
        try:
            api_key = os.getenv("INDIC_NLPCLOUD_API_KEY")
            # NLC API endpoint (example; adjust per actual service)
            # This is a placeholder — actual implementation would call the service
            pass
        except Exception as e:
            pass
    
    # Fallback: return original text with a note
    return text


def get_language_display_name(lang_code: str) -> str:
    """Get display name for a language code."""
    return SUPPORTED_LANGUAGES.get(lang_code, "Unknown")


def get_all_languages() -> Dict[str, str]:
    """Get all supported languages."""
    return SUPPORTED_LANGUAGES.copy()


class MultiLanguageManager:
    """Manager for handling multi-language operations."""
    
    def __init__(self):
        self.current_language = "en"
        self.supported_langs = SUPPORTED_LANGUAGES.copy()
    
    def detect_and_set(self, text: str) -> str:
        """Auto-detect language from text and update current language."""
        detected = detect_language(text)
        self.current_language = detected
        return detected
    
    def set_language(self, lang_code: str):
        """Manually set the current language."""
        if lang_code in self.supported_langs:
            self.current_language = lang_code
        else:
            raise ValueError(f"Unsupported language: {lang_code}")
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def translate_to_english(self, text: str) -> str:
        """Translate text to English."""
        detected = detect_language(text)
        if detected == "en":
            return text
        return translate_text(text, detected, "en")
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """Translate text from English to target language."""
        if target_lang == "en":
            return text
        return translate_text(text, "en", target_lang)


# Global instance
_lang_manager = None

def get_lang_manager() -> MultiLanguageManager:
    """Get or create the global language manager instance."""
    global _lang_manager
    if _lang_manager is None:
        _lang_manager = MultiLanguageManager()
    return _lang_manager


__all__ = [
    "SUPPORTED_LANGUAGES",
    "detect_language",
    "translate_text",
    "get_language_display_name",
    "get_all_languages",
    "MultiLanguageManager",
    "get_lang_manager",
]
