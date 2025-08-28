"""
Communication Gateway Schemas
Privacy-first messaging and notification contracts
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class CommunicationChannel(str, Enum):
    """Supported communication channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    PERSONAL_LOG_SERVER = "personal_log_server"


class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class DeliveryStatus(str, Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """Message content types"""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    ENCRYPTED = "encrypted"
    SYSTEM_NOTIFICATION = "system_notification"
    SECURITY_ALERT = "security_alert"


class RetryPolicy(BaseModel):
    """Message retry configuration"""
    
    max_attempts: int = Field(default=3, ge=1, le=10)
    backoff_seconds: int = Field(default=60, ge=1)
    exponential_backoff: bool = Field(default=True)
    retry_channels: List[CommunicationChannel] = Field(default_factory=list)


class MessageRoute(BaseModel):
    """Message routing configuration"""
    
    # Primary delivery
    primary_channel: CommunicationChannel
    primary_destination: str = Field(..., description="Channel-specific destination (chat_id, email, etc.)")
    
    # Fallback channels
    fallback_channels: List[CommunicationChannel] = Field(default_factory=list)
    fallback_destinations: Dict[str, str] = Field(default_factory=dict)
    
    # Routing preferences
    prefer_encrypted: bool = Field(default=True)
    require_authentication: bool = Field(default=True)
    log_to_personal_server: bool = Field(default=True)
    
    # Delivery settings
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    expiry_seconds: int = Field(default=86400, ge=60)  # 24 hours default


class MessageContent(BaseModel):
    """Message content with privacy controls"""
    
    # Content
    message_type: MessageType = Field(default=MessageType.TEXT)
    text: Optional[str] = Field(default=None)
    html: Optional[str] = Field(default=None)
    markdown: Optional[str] = Field(default=None)
    json_data: Optional[Dict[str, Any]] = Field(default=None)
    
    # Encryption
    encrypted_content: Optional[str] = Field(default=None, description="GPG-encrypted message content")
    encryption_recipients: List[str] = Field(default_factory=list, description="GPG key fingerprints")
    
    # Metadata
    subject: Optional[str] = Field(default=None, max_length=200)
    sender_name: Optional[str] = Field(default=None, max_length=100)
    reply_to: Optional[str] = Field(default=None)
    
    # Privacy settings
    ephemeral: bool = Field(default=False, description="Delete after reading")
    self_destruct_seconds: Optional[int] = Field(default=None, ge=1)
    disable_preview: bool = Field(default=False)
    
    @field_validator('text', 'html', 'markdown', 'encrypted_content', mode="before", always=True)
    def validate_content_present(cls, v, values, field):
        """Ensure at least one content type is provided"""
        content_fields = ['text', 'html', 'markdown', 'encrypted_content', 'json_data']
        if field.name in content_fields:
            has_content = any(values.get(f) for f in content_fields if f != field.name) or v
            if not has_content and not values.get('json_data'):
                raise ValueError('At least one content type must be provided')
        return v


class MessageRequest(BaseModel):
    """Message sending request with privacy-first design"""
    
    # Recipients
    user_id: Optional[str] = Field(default=None, description="Internal user ID for authenticated messaging")
    route: MessageRoute
    
    # Content
    content: MessageContent
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    
    # Context and tracking
    context_labels: Dict[str, str] = Field(default_factory=dict, description="Context-Lock signature labels")
    tracking_id: Optional[str] = Field(default=None, description="External tracking reference")
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")
    
    # Privacy and compliance
    gdpr_compliant: bool = Field(default=True, description="Ensure GDPR compliance")
    retention_seconds: Optional[int] = Field(default=86400, ge=0, description="Message retention period")
    personal_data_included: bool = Field(default=False, description="Whether message contains personal data")
    
    # Scheduling
    send_at: Optional[datetime] = Field(default=None, description="Schedule message delivery")
    timezone: str = Field(default="UTC")
    
    # Integration context
    source_module: str = Field(default="communication", description="Originating module")
    source_action: Optional[str] = Field(default=None, description="Triggering action")


class MessageResponse(BaseModel):
    """Message sending response"""
    
    success: bool
    message_id: str = Field(..., description="Unique message identifier")
    
    # Delivery information
    delivery_status: DeliveryStatus
    channel_used: CommunicationChannel
    destination_reached: str = Field(..., description="Actual destination used")
    
    # Timing
    sent_at: datetime
    estimated_delivery: Optional[datetime] = Field(default=None)
    
    # Privacy compliance
    personal_log_recorded: bool = Field(default=False)
    retention_expires_at: Optional[datetime] = Field(default=None)
    
    # Error handling
    error: Optional[str] = Field(default=None)
    retry_count: int = Field(default=0, ge=0)
    next_retry_at: Optional[datetime] = Field(default=None)
    
    # Tracking
    correlation_id: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


class NotificationPreferences(BaseModel):
    """User notification preferences stored in personal log server"""
    
    user_id: str
    
    # Channel preferences
    preferred_channels: List[CommunicationChannel] = Field(
        default_factory=lambda: [CommunicationChannel.TELEGRAM, CommunicationChannel.EMAIL]
    )
    disabled_channels: List[CommunicationChannel] = Field(default_factory=list)
    
    # Content preferences
    markdown_enabled: bool = Field(default=True)
    html_enabled: bool = Field(default=False)
    emoji_enabled: bool = Field(default=True)
    
    # Privacy preferences
    encrypt_notifications: bool = Field(default=True)
    ephemeral_notifications: bool = Field(default=False)
    disable_read_receipts: bool = Field(default=True)
    
    # Timing preferences
    quiet_hours_start: Optional[str] = Field(default="22:00", pattern=r"^\d{2}:\d{2}$")
    quiet_hours_end: Optional[str] = Field(default="08:00", pattern=r"^\d{2}:\d{2}$")
    timezone: str = Field(default="Asia/Tokyo")
    
    # Category-specific settings
    security_alerts: bool = Field(default=True)
    system_notifications: bool = Field(default=True)
    plugin_notifications: bool = Field(default=False)
    payment_notifications: bool = Field(default=True)
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NotificationRequest(BaseModel):
    """System notification request"""
    
    # Recipients
    user_ids: List[str] = Field(..., min_items=1, description="Target user IDs")
    
    # Notification content
    title: str = Field(..., max_length=100)
    message: str = Field(..., max_length=1000)
    notification_type: str = Field(..., pattern=r"^[a-z_]+$", description="Notification category")
    
    # Presentation
    icon: Optional[str] = Field(default=None, description="Notification icon emoji or URL")
    action_buttons: List[Dict[str, str]] = Field(default_factory=list, max_items=3)
    deep_link: Optional[str] = Field(default=None, description="App deep link URL")
    
    # Priority and timing
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Privacy settings
    encrypted: bool = Field(default=False, description="Encrypt notification content")
    log_to_personal_server: bool = Field(default=True)
    
    # Context
    context_labels: Dict[str, str] = Field(default_factory=dict)
    source_module: str = Field(default="system")


class NotificationResponse(BaseModel):
    """System notification response"""
    
    success: bool
    notification_id: str
    
    # Delivery results
    delivered_to: List[str] = Field(default_factory=list, description="Successfully delivered user IDs")
    failed_deliveries: List[str] = Field(default_factory=list, description="Failed delivery user IDs")
    
    # Channel breakdown
    delivery_by_channel: Dict[str, int] = Field(default_factory=dict)
    
    # Privacy compliance
    personal_logs_recorded: int = Field(default=0, ge=0)
    
    # Error information
    errors: List[str] = Field(default_factory=list)
    
    request_id: str = Field(..., description="Unique request identifier")


class WebhookEvent(BaseModel):
    """Webhook event for external integrations"""
    
    # Event identification
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type identifier")
    
    # Payload
    payload: Dict[str, Any] = Field(..., description="Event payload")
    signature: Optional[str] = Field(default=None, description="HMAC signature for verification")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Event source identifier")
    version: str = Field(default="1.0")
    
    # Privacy context
    user_controlled: bool = Field(default=True)
    personal_data_included: bool = Field(default=False)


class CommunicationHealthResponse(BaseModel):
    """Communication module health check response"""
    
    status: str = Field(..., description="Module status")
    
    # Channel connectivity
    telegram_api_accessible: bool
    email_service_accessible: bool
    webhook_endpoints_healthy: int = Field(ge=0)
    
    # Performance metrics
    messages_sent_last_hour: int = Field(ge=0)
    average_delivery_time_ms: Optional[int] = Field(default=None, ge=0)
    delivery_success_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Queue status
    pending_messages: int = Field(ge=0)
    failed_messages_last_hour: int = Field(ge=0)
    retry_queue_size: int = Field(ge=0)
    
    # Privacy compliance
    personal_logs_active: int = Field(ge=0)
    gdpr_compliant_operations: bool = Field(default=True)
    encrypted_messages_percentage: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Integration status
    auth_service_connected: bool = Field(default=True)
    gpg_service_available: bool = Field(default=True)
    
    last_check: datetime = Field(..., description="Last health check timestamp")