"""
Configuration management for the LangChain Chatbot
"""

import os
from dataclasses import dataclass
from typing import List

@dataclass
class ChatbotConfig:
    """Configuration class for chatbot settings"""
    
    # Model settings
    default_temperature: float = 0.7
    max_tokens: int = 2048
    max_history_length: int = 50
    
    # File upload limits
    max_file_size_mb: int = 50
    supported_file_types: List[str] = None
    
    # RAG settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Voice settings
    voice_timeout: int = 5
    tts_language: str = "en"
    
    # Caching
    cache_ttl_hours: int = 1
    max_cache_size_mb: int = 100
    
    # Security
    max_input_length: int = 4000
    enable_debug_mode: bool = False
    
    def __post_init__(self):
        if self.supported_file_types is None:
            self.supported_file_types = ["pdf", "docx", "txt", "csv"]
    
    @classmethod
    def from_env(cls) -> 'ChatbotConfig':
        """Create config from environment variables"""
        return cls(
            default_temperature=float(os.getenv("DEFAULT_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2048")),
            max_history_length=int(os.getenv("MAX_HISTORY_LENGTH", "50")),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "50")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            voice_timeout=int(os.getenv("VOICE_TIMEOUT", "5")),
            cache_ttl_hours=int(os.getenv("CACHE_TTL_HOURS", "1")),
            max_input_length=int(os.getenv("MAX_INPUT_LENGTH", "4000")),
            enable_debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true"
        )

# Global configuration instance
CONFIG = ChatbotConfig.from_env()
