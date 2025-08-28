"""
String Utilities

Provides safe and consistent string processing functions for all Libral Core modules.
These utilities handle common string operations with security and UI considerations.
"""

import re
import html
from typing import Optional


class StringUtils:
    """
    Utility class for secure and consistent string processing.
    
    Design Intent:
    - Prevent security vulnerabilities from user input
    - Ensure consistent text formatting across the platform
    - Handle UI display constraints gracefully
    """
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Remove dangerous characters from user input to prevent security risks.
        
        This method eliminates HTML tags, script elements, and other potentially
        harmful content that could lead to XSS attacks or content injection.
        
        Args:
            text: Raw user input text
            
        Returns:
            Sanitized text safe for storage and display
            
        Example:
            >>> StringUtils.sanitize_text("<script>alert('xss')</script>Hello")
            "Hello"
        """
        if not text:
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Escape HTML entities
        text = html.escape(text)
        
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def truncate_text(text: str, length: int, suffix: str = "...") -> str:
        """
        Truncate text to fit UI display constraints while preserving readability.
        
        This method ensures text fits within specified character limits,
        adding an ellipsis to indicate truncation.
        
        Args:
            text: Original text to truncate
            length: Maximum allowed character length
            suffix: String to append when text is truncated
            
        Returns:
            Truncated text with suffix if needed
            
        Example:
            >>> StringUtils.truncate_text("Very long text here", 10)
            "Very lo..."
        """
        if not text:
            return ""
            
        if length <= 0:
            return ""
            
        if len(text) <= length:
            return text
            
        # Ensure suffix fits within length constraint
        if len(suffix) >= length:
            return text[:length]
            
        truncated_length = length - len(suffix)
        return text[:truncated_length] + suffix
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace characters for consistent processing.
        
        Args:
            text: Text with potentially irregular whitespace
            
        Returns:
            Text with normalized whitespace
        """
        if not text:
            return ""
            
        # Replace all whitespace with single spaces
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def extract_hashtags(text: str) -> list[str]:
        """
        Extract hashtags from text for Telegram topic organization.
        
        Design Intent: Support Telegram topics and hashtag improvement system
        
        Args:
            text: Text containing potential hashtags
            
        Returns:
            List of hashtags found in the text
        """
        if not text:
            return []
            
        # Find hashtags (# followed by alphanumeric characters)
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates
    
    @staticmethod
    def validate_telegram_username(username: str) -> bool:
        """
        Validate Telegram username format for authentication system.
        
        Args:
            username: Telegram username to validate
            
        Returns:
            True if username is valid, False otherwise
        """
        if not username:
            return False
            
        # Telegram username rules: 5-32 chars, alphanumeric + underscores
        pattern = r'^[a-zA-Z0-9_]{5,32}$'
        return bool(re.match(pattern, username))