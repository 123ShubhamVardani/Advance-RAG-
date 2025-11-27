"""
Centralized logging system for the chatbot
"""

import logging
import os
from datetime import datetime

class ChatbotLogger:
    """Custom logger for the chatbot application"""
    
    def __init__(self, log_level: str = "INFO"):
        self.logger = logging.getLogger("chatbot")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(f"logs/chatbot_{datetime.now().strftime('%Y%m%d')}.log")
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)

# Global logger instance
logger = ChatbotLogger(os.getenv("LOG_LEVEL", "INFO"))
