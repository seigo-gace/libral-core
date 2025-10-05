"""
API Hub Schemas
External API integration and usage tracking contracts
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class APIProvider(str, Enum):
    """Supported API providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_CLOUD = "google_cloud"
    AWS = "aws"
    AZURE = "azure"
    STRIPE = "stripe"
    TELEGRAM = "telegram"
    GITHUB = "github"
    SLACK = "slack"
    DISCORD = "discord"
    CUSTOM = "custom"


class APIStatus(str, Enum):
    """API credential and service status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class UsagePeriod(str, Enum):
    """API usage tracking periods"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class IntegrationType(str, Enum):
    """Types of third-party integrations"""
    API_PROXY = "api_proxy"
    WEBHOOK = "webhook"
    OAUTH = "oauth"
    DIRECT_CONNECTION = "direct_connection"
    PLUGIN_INTEGRATION = "plugin_integration"


class APICredential(BaseModel):
    """API credential model with encryption"""
    
    # Credential identification
    credential_id: str = Field(..., description="Unique credential identifier")
    user_id: str = Field(..., description="Owner user ID")
    provider: APIProvider
    
    # Credential details
    name: str = Field(..., max_length=100, description="User-friendly credential name")
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Encrypted credentials
    encrypted_api_key: str = Field(..., description="GPG-encrypted API key")
    encrypted_secret: Optional[str] = Field(default=None, description="GPG-encrypted API secret")
    encrypted_config: Optional[str] = Field(default=None, description="GPG-encrypted additional config")
    encryption_recipient: str = Field(..., description="GPG key fingerprint")
    
    # Access control
    status: APIStatus = Field(default=APIStatus.ACTIVE)
    allowed_origins: List[str] = Field(default_factory=list, max_length=20)
    ip_whitelist: List[str] = Field(default_factory=list, max_length=50)
    
    # Usage limits
    daily_quota: Optional[int] = Field(default=None, ge=0, description="Daily API call limit")
    monthly_quota: Optional[int] = Field(default=None, ge=0, description="Monthly API call limit")
    cost_limit_usd: Optional[Decimal] = Field(default=None, ge=0, description="Monthly cost limit")
    
    # Security settings
    require_authentication: bool = Field(default=True)
    log_requests: bool = Field(default=True)
    log_responses: bool = Field(default=False, description="Log API responses (privacy risk)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = Field(default=None)
    
    # Privacy settings
    log_to_personal_server: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)


class APICredentialCreate(BaseModel):
    """API credential creation request"""
    
    provider: APIProvider
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    
    # Raw credentials (will be encrypted)
    api_key: str = Field(..., description="API key to encrypt")
    api_secret: Optional[str] = Field(default=None, description="API secret to encrypt")
    additional_config: Optional[Dict[str, Any]] = Field(default=None)
    
    # Access control
    allowed_origins: List[str] = Field(default_factory=list, max_length=20)
    ip_whitelist: List[str] = Field(default_factory=list, max_length=50)
    
    # Usage limits
    daily_quota: Optional[int] = Field(default=None, ge=0)
    monthly_quota: Optional[int] = Field(default=None, ge=0)
    cost_limit_usd: Optional[Decimal] = Field(default=None, ge=0)
    
    # Security settings
    require_authentication: bool = Field(default=True)
    log_requests: bool = Field(default=True)
    log_responses: bool = Field(default=False)
    
    # Privacy settings
    log_to_personal_server: bool = Field(default=True)


class APIUsage(BaseModel):
    """API usage tracking record"""
    
    # Usage identification
    usage_id: str = Field(..., description="Unique usage record identifier")
    user_id: str = Field(..., description="API user ID")
    credential_id: str = Field(..., description="Used credential ID")
    
    # API call details
    provider: APIProvider
    endpoint: str = Field(..., max_length=500, description="API endpoint called")
    method: str = Field(..., pattern=r"^(GET|POST|PUT|DELETE|PATCH)$")
    
    # Request details
    request_size_bytes: Optional[int] = Field(default=None, ge=0)
    response_size_bytes: Optional[int] = Field(default=None, ge=0)
    response_time_ms: Optional[int] = Field(default=None, ge=0)
    status_code: Optional[int] = Field(default=None, ge=100, le=599)
    
    # Cost tracking
    estimated_cost_usd: Optional[Decimal] = Field(default=None, ge=0)
    tokens_used: Optional[int] = Field(default=None, ge=0, description="For AI APIs")
    credits_consumed: Optional[int] = Field(default=None, ge=0)
    
    # Context
    purpose: Optional[str] = Field(default=None, max_length=200, description="Usage purpose")
    plugin_id: Optional[str] = Field(default=None, description="Calling plugin ID")
    session_id: Optional[str] = Field(default=None, description="User session ID")
    
    # Error handling
    success: bool = Field(default=True)
    error_code: Optional[str] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=1000)
    
    # Timing
    called_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Privacy compliance
    contains_personal_data: bool = Field(default=False)
    log_to_personal_server: bool = Field(default=True)
    retention_days: int = Field(default=90, ge=1, le=365)


class APIUsageResponse(BaseModel):
    """API usage tracking response"""
    
    success: bool
    usage_id: str
    
    # Usage stats
    current_daily_usage: int = Field(ge=0)
    current_monthly_usage: int = Field(ge=0)
    current_monthly_cost: Decimal = Field(ge=0)
    
    # Quota status
    daily_quota_remaining: Optional[int] = Field(default=None, ge=0)
    monthly_quota_remaining: Optional[int] = Field(default=None, ge=0)
    cost_limit_remaining: Optional[Decimal] = Field(default=None, ge=0)
    
    # Warnings
    quota_warnings: List[str] = Field(default_factory=list)
    cost_warnings: List[str] = Field(default_factory=list)
    
    # Privacy compliance
    logged_to_personal_server: bool = Field(default=False)
    
    request_id: str = Field(..., description="Unique request identifier")


class ExternalAPICall(BaseModel):
    """External API call request"""
    
    # API details
    credential_id: str = Field(..., description="API credential to use")
    endpoint: str = Field(..., max_length=500)
    method: str = Field(..., pattern=r"^(GET|POST|PUT|DELETE|PATCH)$")
    
    # Request data
    headers: Optional[Dict[str, str]] = Field(default=None)
    query_params: Optional[Dict[str, Any]] = Field(default=None)
    request_body: Optional[Dict[str, Any]] = Field(default=None)
    
    # Request options
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    follow_redirects: bool = Field(default=True)
    verify_ssl: bool = Field(default=True)
    
    # Cost management
    max_cost_usd: Optional[Decimal] = Field(default=None, ge=0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    
    # Context
    purpose: Optional[str] = Field(default=None, max_length=200)
    plugin_id: Optional[str] = Field(default=None)
    
    # Privacy settings
    log_request: bool = Field(default=True)
    log_response: bool = Field(default=False)
    contains_personal_data: bool = Field(default=False)


class ThirdPartyIntegration(BaseModel):
    """Third-party service integration"""
    
    # Integration identification
    integration_id: str = Field(..., description="Unique integration identifier")
    user_id: str = Field(..., description="Integration owner")
    
    # Integration details
    name: str = Field(..., max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    provider: APIProvider
    integration_type: IntegrationType
    
    # Configuration
    encrypted_config: str = Field(..., description="GPG-encrypted integration config")
    webhook_url: Optional[str] = Field(default=None, max_length=500)
    callback_url: Optional[str] = Field(default=None, max_length=500)
    
    # Security
    shared_secret: Optional[str] = Field(default=None, description="Webhook verification secret")
    oauth_scopes: List[str] = Field(default_factory=list, max_length=20)
    
    # Status and health
    status: APIStatus = Field(default=APIStatus.ACTIVE)
    last_health_check: Optional[datetime] = Field(default=None)
    health_check_url: Optional[str] = Field(default=None, max_length=500)
    
    # Usage tracking
    total_calls: int = Field(default=0, ge=0)
    successful_calls: int = Field(default=0, ge=0)
    last_call_at: Optional[datetime] = Field(default=None)
    
    # Privacy settings
    log_to_personal_server: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)
    data_retention_days: int = Field(default=90, ge=1, le=365)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class APIQuota(BaseModel):
    """API usage quota and limits"""
    
    # Quota identification
    quota_id: str = Field(..., description="Unique quota identifier")
    user_id: str = Field(..., description="Quota owner")
    credential_id: Optional[str] = Field(default=None, description="Specific credential quota")
    provider: Optional[APIProvider] = Field(default=None, description="Provider-wide quota")
    
    # Quota limits
    daily_limit: Optional[int] = Field(default=None, ge=0)
    weekly_limit: Optional[int] = Field(default=None, ge=0)
    monthly_limit: Optional[int] = Field(default=None, ge=0)
    yearly_limit: Optional[int] = Field(default=None, ge=0)
    
    # Cost limits
    daily_cost_limit: Optional[Decimal] = Field(default=None, ge=0)
    monthly_cost_limit: Optional[Decimal] = Field(default=None, ge=0)
    yearly_cost_limit: Optional[Decimal] = Field(default=None, ge=0)
    
    # Current usage
    current_daily_usage: int = Field(default=0, ge=0)
    current_weekly_usage: int = Field(default=0, ge=0)
    current_monthly_usage: int = Field(default=0, ge=0)
    current_yearly_usage: int = Field(default=0, ge=0)
    
    # Current costs
    current_daily_cost: Decimal = Field(default=Decimal("0"), ge=0)
    current_monthly_cost: Decimal = Field(default=Decimal("0"), ge=0)
    current_yearly_cost: Decimal = Field(default=Decimal("0"), ge=0)
    
    # Reset periods
    daily_reset_at: datetime = Field(..., description="Next daily reset time")
    monthly_reset_at: datetime = Field(..., description="Next monthly reset time")
    yearly_reset_at: datetime = Field(..., description="Next yearly reset time")
    
    # Warning thresholds
    warning_threshold_percentage: int = Field(default=80, ge=1, le=100)
    critical_threshold_percentage: int = Field(default=95, ge=1, le=100)
    
    # Status
    quota_exceeded: bool = Field(default=False)
    cost_limit_exceeded: bool = Field(default=False)
    last_warning_sent: Optional[datetime] = Field(default=None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class APIHealthCheck(BaseModel):
    """API health check result"""
    
    # Health check identification
    check_id: str = Field(..., description="Unique health check identifier")
    provider: APIProvider
    endpoint: str = Field(..., max_length=500)
    
    # Health status
    status: str = Field(..., pattern=r"^(healthy|degraded|unhealthy)$")
    response_time_ms: Optional[int] = Field(default=None, ge=0)
    status_code: Optional[int] = Field(default=None, ge=100, le=599)
    
    # Error details
    error_message: Optional[str] = Field(default=None, max_length=1000)
    error_count_last_hour: int = Field(default=0, ge=0)
    
    # Performance metrics
    average_response_time_ms: Optional[int] = Field(default=None, ge=0)
    success_rate_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Rate limiting
    rate_limit_remaining: Optional[int] = Field(default=None, ge=0)
    rate_limit_reset_at: Optional[datetime] = Field(default=None)
    
    # Metadata
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    check_interval_minutes: int = Field(default=5, ge=1, le=60)


class ServiceConnector(BaseModel):
    """Service connector configuration"""
    
    # Connector identification
    connector_id: str = Field(..., description="Unique connector identifier")
    user_id: str = Field(..., description="Connector owner")
    
    # Service details
    service_name: str = Field(..., max_length=100)
    service_url: str = Field(..., max_length=500)
    provider: APIProvider
    
    # Connection config
    encrypted_connection_config: str = Field(..., description="GPG-encrypted connection settings")
    connection_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    
    # Load balancing
    backup_urls: List[str] = Field(default_factory=list, max_length=5)
    failover_enabled: bool = Field(default=True)
    health_check_interval_minutes: int = Field(default=5, ge=1, le=60)
    
    # Security
    encryption_required: bool = Field(default=True)
    certificate_validation: bool = Field(default=True)
    mutual_tls: bool = Field(default=False)
    
    # Monitoring
    monitor_performance: bool = Field(default=True)
    alert_on_failures: bool = Field(default=True)
    log_all_requests: bool = Field(default=True)
    
    # Privacy compliance
    personal_data_handling: str = Field(
        default="encrypt",
        pattern=r"^(encrypt|anonymize|exclude)$",
        description="How to handle personal data"
    )
    log_to_personal_server: bool = Field(default=True)
    gdpr_compliant: bool = Field(default=True)
    
    # Status
    status: APIStatus = Field(default=APIStatus.ACTIVE)
    last_connection_test: Optional[datetime] = Field(default=None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class APIHubHealthResponse(BaseModel):
    """API Hub module health response"""
    
    status: str = Field(..., description="Module status")
    
    # API credentials status
    total_credentials: int = Field(ge=0)
    active_credentials: int = Field(ge=0)
    expired_credentials: int = Field(ge=0)
    
    # Usage statistics
    api_calls_last_hour: int = Field(ge=0)
    successful_calls_last_hour: int = Field(ge=0)
    failed_calls_last_hour: int = Field(ge=0)
    average_response_time_ms: Optional[int] = Field(default=None, ge=0)
    
    # Cost tracking
    total_cost_last_24h: Decimal = Field(ge=0)
    cost_per_call_average: Decimal = Field(ge=0)
    
    # Provider status
    healthy_providers: int = Field(ge=0)
    degraded_providers: int = Field(ge=0)
    unhealthy_providers: int = Field(ge=0)
    
    # Integration status
    active_integrations: int = Field(ge=0)
    webhook_health_percentage: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Privacy compliance
    encrypted_credentials: int = Field(ge=0)
    personal_logs_recorded_last_hour: int = Field(ge=0)
    gdpr_compliant_operations: bool = Field(default=True)
    
    # System resources
    memory_usage_mb: Optional[int] = Field(default=None, ge=0)
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Security
    security_violations_last_hour: int = Field(ge=0)
    rate_limited_requests: int = Field(ge=0)
    
    last_check: datetime = Field(..., description="Last health check timestamp")