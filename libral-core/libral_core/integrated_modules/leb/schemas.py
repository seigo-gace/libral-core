"""
Libral Event Bus (LEB) - Unified Schemas
Integrated Communication Gateway + Event Management functionality
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# Core Event Types
class EventType(str, Enum):
    """Event type categories"""
    SYSTEM = "system"
    USER = "user"
    COMMUNICATION = "communication"
    PLUGIN = "plugin"
    PAYMENT = "payment"
    SECURITY = "security"
    API = "api"
    WEBHOOK = "webhook"
    NOTIFICATION = "notification"
    ERROR = "error"


class EventPriority(str, Enum):
    """Event processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MessageProtocol(str, Enum):
    """Supported message protocols"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEBHOOK = "webhook"
    WEBSOCKET = "websocket"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"


class MessageStatus(str, Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


class TopicCategory(str, Enum):
    """Personal log server topic categories"""
    AUTHENTICATION = "authentication"
    PLUGIN_ACTIVITY = "plugin_activity"
    PAYMENTS = "payments"
    COMMUNICATION = "communication"
    SYSTEM_EVENTS = "system_events"
    GENERAL = "general"


class EventProcessingStatus(str, Enum):
    """Event processing status"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


# Core Event Schema
class BaseEvent(BaseModel):
    """Base event structure"""
    event_id: str = Field(..., description="Unique event identifier")
    event_type: EventType
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    source: str = Field(..., description="Event source (module/service name)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # User context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Event data
    title: str = Field(..., max_length=256)
    description: Optional[str] = Field(default=None, max_length=2048)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Classification
    tags: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)
    topic_category: Optional[TopicCategory] = None
    
    # Processing metadata
    processing_status: EventProcessingStatus = Field(default=EventProcessingStatus.QUEUED)
    retry_count: int = Field(default=0, ge=0, le=5)
    expires_at: Optional[datetime] = None
    
    # Privacy and encryption
    encrypted: bool = Field(default=False)
    context_labels: Optional[Dict[str, str]] = None
    personal_log_only: bool = Field(default=False)
    
    @field_validator('hashtags')
    def validate_hashtags(cls, v):
        """Ensure hashtags start with #"""
        return [tag if tag.startswith('#') else f'#{tag}' for tag in v]


# Communication Schemas
class MessageRecipient(BaseModel):
    """Message recipient information"""
    protocol: MessageProtocol
    address: str = Field(..., description="Email, phone, user_id, chat_id, etc.")
    name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MessageTemplate(BaseModel):
    """Message template with multiple protocol support"""
    template_id: str
    name: str
    description: Optional[str] = None
    
    # Protocol-specific templates
    telegram_template: Optional[str] = None
    email_template: Optional[str] = None
    webhook_template: Optional[str] = None
    sms_template: Optional[str] = None
    
    # Template variables
    variables: List[str] = Field(default_factory=list)
    default_values: Dict[str, str] = Field(default_factory=dict)
    
    # Formatting options
    supports_html: bool = Field(default=False)
    supports_markdown: bool = Field(default=True)


class Message(BaseModel):
    """Unified message structure"""
    message_id: str = Field(..., description="Unique message identifier")
    
    # Content
    subject: Optional[str] = None
    content: str = Field(..., max_length=4096)
    template_id: Optional[str] = None
    template_variables: Dict[str, str] = Field(default_factory=dict)
    
    # Recipients and routing
    recipients: List[MessageRecipient]
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    protocol_fallback: bool = Field(default=True, description="Try alternative protocols if primary fails")
    
    # Scheduling
    send_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Privacy and encryption
    encrypt_content: bool = Field(default=True)
    log_to_personal_server: bool = Field(default=True)
    topic_category: Optional[TopicCategory] = None
    
    # Metadata
    source_event_id: Optional[str] = None
    user_id: Optional[str] = None
    context_labels: Optional[Dict[str, str]] = None
    
    # Status tracking
    status: MessageStatus = Field(default=MessageStatus.PENDING)
    delivery_attempts: int = Field(default=0)
    last_attempt: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None


class WebhookEvent(BaseModel):
    """Webhook event payload"""
    webhook_id: str
    source: str = Field(..., description="External service name")
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification
    signature: Optional[str] = None
    verified: bool = Field(default=False)
    
    # Processing
    processed: bool = Field(default=False)
    processing_error: Optional[str] = None


# Event Bus Configuration
class EventBusConfig(BaseModel):
    """Event bus configuration"""
    max_queue_size: int = Field(default=10000)
    max_retry_attempts: int = Field(default=3)
    retry_delay_seconds: int = Field(default=60)
    
    # Message delivery
    default_message_ttl_hours: int = Field(default=24)
    max_message_size_bytes: int = Field(default=1048576)  # 1MB
    
    # Personal log server integration
    personal_log_encryption: bool = Field(default=True)
    auto_create_topics: bool = Field(default=True)
    topic_retention_days: int = Field(default=30)
    
    # WebSocket broadcasting
    websocket_enabled: bool = Field(default=True)
    broadcast_system_events: bool = Field(default=True)
    broadcast_user_events: bool = Field(default=False)


# Event Processing Schemas
class EventFilter(BaseModel):
    """Event filtering criteria"""
    event_types: Optional[List[EventType]] = None
    priorities: Optional[List[EventPriority]] = None
    sources: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    topic_categories: Optional[List[TopicCategory]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    encrypted_only: Optional[bool] = None
    personal_log_only: Optional[bool] = None


class EventQuery(BaseModel):
    """Event query parameters"""
    filter: Optional[EventFilter] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="timestamp")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    include_data: bool = Field(default=True)


class EventBatch(BaseModel):
    """Batch event processing"""
    batch_id: str
    events: List[BaseEvent]
    processing_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Batch metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_events: int = Field(..., ge=1)
    processed_events: int = Field(default=0)
    failed_events: int = Field(default=0)
    
    # Status
    status: EventProcessingStatus = Field(default=EventProcessingStatus.QUEUED)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


# Personal Log Server Schemas
class PersonalLogEntry(BaseModel):
    """Personal log server entry"""
    log_id: str
    user_id: str
    
    # Telegram integration
    telegram_group_id: int
    telegram_message_id: Optional[int] = None
    topic_id: Optional[int] = None
    
    # Content
    event_id: str
    title: str
    content: str
    hashtags: List[str] = Field(default_factory=list)
    topic_category: TopicCategory
    
    # Encryption
    encrypted: bool = Field(default=True)
    encryption_key_fingerprint: Optional[str] = None
    
    # Metadata
    logged_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class TopicConfiguration(BaseModel):
    """Personal log server topic configuration"""
    topic_id: int
    name: str
    category: TopicCategory
    description: str
    hashtags: List[str]
    
    # Auto-routing rules
    event_types: List[EventType] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    
    # Settings
    auto_delete_hours: Optional[int] = None
    encryption_required: bool = Field(default=True)
    admin_only: bool = Field(default=False)


# System Health and Metrics
class EventBusHealth(BaseModel):
    """Event bus health status"""
    status: str
    version: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "event_queue": {"status": "unknown", "queue_size": 0, "processing_rate": 0},
        "message_delivery": {"status": "unknown", "success_rate": 0, "failed_messages": 0},
        "personal_log_servers": {"status": "unknown", "active_servers": 0, "log_entries_today": 0},
        "webhooks": {"status": "unknown", "registered_hooks": 0, "events_today": 0},
        "websocket_broadcast": {"status": "unknown", "connected_clients": 0, "messages_sent": 0}
    })
    uptime_seconds: float
    last_health_check: datetime


class EventMetrics(BaseModel):
    """Event processing metrics"""
    period_start: datetime
    period_end: datetime
    
    # Event statistics
    total_events: int
    events_by_type: Dict[EventType, int] = Field(default_factory=dict)
    events_by_priority: Dict[EventPriority, int] = Field(default_factory=dict)
    events_by_status: Dict[EventProcessingStatus, int] = Field(default_factory=dict)
    
    # Processing performance
    average_processing_time_ms: float
    successful_processing_rate: float
    failed_events: int
    retry_events: int
    
    # Message delivery
    total_messages: int
    messages_by_protocol: Dict[MessageProtocol, int] = Field(default_factory=dict)
    delivery_success_rate: float
    failed_deliveries: int
    
    # Personal log integration
    log_entries_created: int
    topics_used: Dict[TopicCategory, int] = Field(default_factory=dict)
    encrypted_logs_percentage: float
    
    # WebSocket broadcasting
    websocket_messages_sent: int
    active_websocket_connections: int


# Request/Response Schemas
class EventPublishRequest(BaseModel):
    """Publish event request"""
    event: BaseEvent
    routing_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    immediate_processing: bool = Field(default=False)


class EventPublishResponse(BaseModel):
    """Publish event response"""
    success: bool
    event_id: str
    queued_at: datetime
    estimated_processing_time_ms: Optional[int] = None
    error: Optional[str] = None


class MessageSendRequest(BaseModel):
    """Send message request"""
    message: Message
    routing_options: Optional[Dict[str, Any]] = Field(default_factory=dict)
    test_mode: bool = Field(default=False)


class MessageSendResponse(BaseModel):
    """Send message response"""
    success: bool
    message_id: str
    delivery_status: Dict[MessageProtocol, MessageStatus] = Field(default_factory=dict)
    estimated_delivery_time: Optional[datetime] = None
    error: Optional[str] = None


class WebhookRegistrationRequest(BaseModel):
    """Webhook registration request"""
    webhook_id: str
    source: str
    endpoint_url: str
    secret_token: Optional[str] = None
    event_types: List[str] = Field(default_factory=list)
    active: bool = Field(default=True)
    
    # Security
    verify_signature: bool = Field(default=True)
    allowed_ips: Optional[List[str]] = None
    
    # Processing
    max_retries: int = Field(default=3)
    timeout_seconds: int = Field(default=30)


class LEBError(BaseModel):
    """LEB module error response"""
    error_code: str
    error_message: str
    component: str = Field(..., description="event_queue|message_delivery|personal_log|webhook")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str