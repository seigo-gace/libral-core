"""
Authentication Module Schemas
Privacy-first user authentication and session management
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class AuthProvider(str, Enum):
    """Supported authentication providers"""
    TELEGRAM = "telegram"
    GPG_KEY = "gpg_key" 
    ANONYMOUS = "anonymous"


class SessionStatus(str, Enum):
    """Authentication session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class PersonalLogServerStatus(str, Enum):
    """Personal log server setup status"""
    NOT_INITIALIZED = "not_initialized"
    SETTING_UP = "setting_up"
    ACTIVE = "active"
    ERROR = "error"
    SUSPENDED = "suspended"


class UserRole(str, Enum):
    """User roles for access control"""
    USER = "user"
    PREMIUM = "premium"
    DEVELOPER = "developer"
    ADMIN = "admin"


# Core Authentication Schemas
class TelegramAuthRequest(BaseModel):
    """Telegram OAuth authentication request"""
    
    # Telegram OAuth data
    id: int = Field(..., description="Telegram user ID")
    first_name: str = Field(..., max_length=64)
    last_name: Optional[str] = Field(default=None, max_length=64)
    username: Optional[str] = Field(default=None, max_length=32)
    photo_url: Optional[str] = Field(default=None)
    auth_date: int = Field(..., description="Unix timestamp of auth")
    hash: str = Field(..., description="Telegram auth hash")
    
    # Privacy preferences
    create_personal_log_server: bool = Field(default=True, description="Initialize personal log server")
    data_retention_policy: str = Field(default="user_controlled", description="Data retention preference")
    
    @validator('auth_date')
    def validate_auth_date(cls, v):
        # Check auth date is recent (within 24 hours)
        current_time = datetime.utcnow().timestamp()
        if current_time - v > 86400:  # 24 hours
            raise ValueError('Authentication data is too old')
        return v


class UserProfile(BaseModel):
    """User profile information (privacy-compliant)"""
    
    # Minimal identifying information
    user_id: str = Field(..., description="Internal user ID (UUID)")
    telegram_id: Optional[int] = Field(default=None, description="Telegram user ID")
    username: Optional[str] = Field(default=None, max_length=32)
    display_name: str = Field(..., max_length=64, description="User display name")
    
    # User preferences (stored locally)
    preferred_language: str = Field(default="ja", regex="^[a-z]{2}$")
    timezone: str = Field(default="Asia/Tokyo")
    role: UserRole = Field(default=UserRole.USER)
    
    # Privacy settings
    data_retention_hours: int = Field(default=24, ge=1, le=8760)  # Max 1 year
    analytics_enabled: bool = Field(default=False)
    usage_tracking_enabled: bool = Field(default=False)
    
    # Account status
    created_at: datetime
    last_active: datetime
    is_active: bool = Field(default=True)
    
    # GPG integration
    gpg_key_fingerprint: Optional[str] = Field(default=None, description="User's GPG key")
    context_lock_enabled: bool = Field(default=True, description="Enable Context-Lock signatures")


class PersonalLogServer(BaseModel):
    """Personal log server configuration"""
    
    user_id: str
    status: PersonalLogServerStatus = Field(default=PersonalLogServerStatus.NOT_INITIALIZED)
    
    # Telegram supergroup information
    telegram_group_id: Optional[int] = Field(default=None, description="Personal log supergroup ID")
    telegram_group_invite_link: Optional[str] = Field(default=None)
    telegram_bot_added: bool = Field(default=False)
    
    # GPG encryption for logs
    log_encryption_key: Optional[str] = Field(default=None, description="GPG key for log encryption")
    encryption_enabled: bool = Field(default=True)
    
    # Configuration
    setup_started_at: Optional[datetime] = Field(default=None)
    setup_completed_at: Optional[datetime] = Field(default=None)
    last_log_sent: Optional[datetime] = Field(default=None)
    
    # Error tracking
    setup_errors: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0, ge=0)
    
    # Data policy
    auto_delete_after_days: int = Field(default=30, ge=1, le=365)
    log_categories: List[str] = Field(default_factory=lambda: ["auth", "data_access", "plugin_activity"])


class AuthToken(BaseModel):
    """Authentication token (GPG-encrypted)"""
    
    token_id: str = Field(..., description="Unique token identifier")
    user_id: str
    
    # Token properties
    token_type: str = Field(default="session", regex="^(session|api|refresh)$")
    encrypted_payload: str = Field(..., description="GPG-encrypted token payload")
    
    # Lifecycle
    created_at: datetime
    expires_at: datetime
    last_used: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0, ge=0)
    
    # Security context
    context_labels: Dict[str, str] = Field(default_factory=dict)
    client_fingerprint: Optional[str] = Field(default=None, description="Client device fingerprint")
    ip_address_hash: Optional[str] = Field(default=None, description="Hashed IP address")
    
    # Status
    status: SessionStatus = Field(default=SessionStatus.ACTIVE)
    revoked_at: Optional[datetime] = Field(default=None)
    revocation_reason: Optional[str] = Field(default=None)
    
    @validator('expires_at')
    def validate_expiry(cls, v, values):
        if 'created_at' in values and v <= values['created_at']:
            raise ValueError('Expiry time must be after creation time')
        return v


class SessionInfo(BaseModel):
    """Current session information"""
    
    session_id: str
    user_id: str
    
    # Session details
    started_at: datetime
    expires_at: datetime
    last_activity: datetime
    
    # Client information (hashed for privacy)
    client_type: str = Field(..., description="web, mobile, api, plugin")
    user_agent_hash: Optional[str] = Field(default=None)
    device_fingerprint: Optional[str] = Field(default=None)
    
    # Location (country-level only for privacy)
    country_code: Optional[str] = Field(default=None, regex="^[A-Z]{2}$")
    
    # Activity tracking
    requests_count: int = Field(default=0, ge=0)
    last_endpoint: Optional[str] = Field(default=None)
    
    # Security flags
    suspicious_activity: bool = Field(default=False)
    rate_limited: bool = Field(default=False)
    
    # Personal log server integration
    logged_to_personal_server: bool = Field(default=False)
    last_log_sync: Optional[datetime] = Field(default=None)


class UserPreferences(BaseModel):
    """User preferences stored in personal log server"""
    
    user_id: str
    
    # Interface preferences
    language: str = Field(default="ja")
    theme: str = Field(default="dark", regex="^(light|dark|auto)$")
    timezone: str = Field(default="Asia/Tokyo")
    
    # Privacy preferences
    data_retention_days: int = Field(default=30, ge=1, le=365)
    share_analytics: bool = Field(default=False)
    allow_usage_tracking: bool = Field(default=False)
    
    # Security preferences
    require_2fa: bool = Field(default=False)
    session_timeout_minutes: int = Field(default=480, ge=15, le=43200)  # 8 hours default, max 30 days
    auto_logout_enabled: bool = Field(default=True)
    
    # Plugin preferences
    auto_update_plugins: bool = Field(default=False)
    allow_experimental_plugins: bool = Field(default=False)
    plugin_data_sharing: bool = Field(default=False)
    
    # Notification preferences
    personal_log_notifications: bool = Field(default=True)
    security_alerts: bool = Field(default=True)
    plugin_notifications: bool = Field(default=False)
    
    # Personal log server preferences
    log_encryption_required: bool = Field(default=True)
    log_categories: List[str] = Field(default_factory=lambda: ["auth", "data_access"])
    
    # Updated tracking
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by_client: str = Field(default="web")


# Request/Response Schemas
class TelegramAuthResponse(BaseModel):
    """Telegram authentication response"""
    
    success: bool
    user_profile: Optional[UserProfile] = Field(default=None)
    session_info: Optional[SessionInfo] = Field(default=None)
    
    # Authentication tokens
    access_token: Optional[str] = Field(default=None, description="GPG-encrypted access token")
    refresh_token: Optional[str] = Field(default=None, description="GPG-encrypted refresh token")
    token_expires_at: Optional[datetime] = Field(default=None)
    
    # Personal log server status
    personal_log_server: Optional[PersonalLogServer] = Field(default=None)
    setup_required: bool = Field(default=False, description="Personal log server setup needed")
    
    # Error information
    error: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)
    
    # Context information
    request_id: str = Field(..., description="Unique request identifier")
    
    # Privacy compliance
    data_retention_policy: str = Field(default="user_controlled")
    personal_data_stored: bool = Field(default=False, description="Whether personal data is stored centrally")


class PersonalLogServerSetupRequest(BaseModel):
    """Personal log server setup request"""
    
    user_id: str
    
    # Telegram group setup
    create_new_group: bool = Field(default=True, description="Create new supergroup for logs")
    existing_group_id: Optional[int] = Field(default=None, description="Use existing group")
    
    # Encryption settings
    use_gpg_encryption: bool = Field(default=True)
    gpg_key_fingerprint: Optional[str] = Field(default=None)
    
    # Log preferences
    log_categories: List[str] = Field(default_factory=lambda: ["auth", "data_access", "plugin_activity"])
    retention_days: int = Field(default=30, ge=1, le=365)
    
    # Privacy settings
    anonymous_mode: bool = Field(default=False, description="Anonymize user data in logs")


class PersonalLogServerSetupResponse(BaseModel):
    """Personal log server setup response"""
    
    success: bool
    personal_log_server: Optional[PersonalLogServer] = Field(default=None)
    
    # Setup instructions for user
    setup_instructions: List[str] = Field(default_factory=list)
    telegram_bot_username: Optional[str] = Field(default=None)
    group_invite_link: Optional[str] = Field(default=None)
    
    # Status information
    status: PersonalLogServerStatus
    estimated_setup_time_minutes: int = Field(default=5)
    
    # Error handling
    error: Optional[str] = Field(default=None)
    retry_possible: bool = Field(default=True)
    
    request_id: str = Field(..., description="Unique request identifier")


class TokenRefreshRequest(BaseModel):
    """Token refresh request"""
    
    refresh_token: str = Field(..., description="GPG-encrypted refresh token")
    client_fingerprint: Optional[str] = Field(default=None)


class TokenRefreshResponse(BaseModel):
    """Token refresh response"""
    
    success: bool
    
    # New tokens
    access_token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Session info
    session_extended: bool = Field(default=False)
    
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


# Health and Status Schemas
class AuthHealthResponse(BaseModel):
    """Authentication module health check response"""
    
    status: str = Field(..., description="Module status")
    
    # Service connectivity
    telegram_bot_accessible: bool
    gpg_service_available: bool
    personal_log_servers_operational: int = Field(ge=0)
    
    # Statistics
    active_sessions: int = Field(ge=0)
    users_with_personal_servers: int = Field(ge=0)
    
    # Performance metrics
    average_auth_time_ms: Optional[int] = Field(default=None, ge=0)
    token_refresh_success_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Security status
    suspicious_activity_detected: bool = Field(default=False)
    rate_limiting_active: bool = Field(default=False)
    
    # Privacy compliance status
    personal_data_retention_compliant: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)
    
    last_check: datetime = Field(..., description="Last health check timestamp")