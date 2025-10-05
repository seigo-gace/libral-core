"""
Authentication Module - Week 3 Implementation
Telegram OAuth integration with personal log server setup

Features:
- Telegram OAuth 2.0 authentication
- Personal log server initialization in user's Telegram groups
- GPG-encrypted session management
- User preference storage with privacy controls
- Zero personal data retention on central servers
- Context-Lock authentication tokens
"""

from .service import AuthService
from .schemas import (
    TelegramAuthRequest,
    TelegramAuthResponse,
    UserProfile,
    PersonalLogServer,
    AuthToken,
    SessionInfo,
    UserPreferences
)

__all__ = [
    "AuthService",
    "TelegramAuthRequest", 
    "TelegramAuthResponse",
    "UserProfile",
    "PersonalLogServer",
    "AuthToken",
    "SessionInfo",
    "UserPreferences"
]