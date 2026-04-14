"""
Event Management Schemas
Real-time event processing with privacy-first design
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class EventCategory(str, Enum):
    """Event categories for organization and filtering"""
    SYSTEM = "system"
    USER = "user"
    PLUGIN = "plugin"
    PAYMENT = "payment"
    SECURITY = "security"
    COMMUNICATION = "communication"
    STORAGE = "storage"
    KNOWLEDGE_BASE = "knowledge_base"
    PERSONAL_LOG = "personal_log"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class EventStatus(str, Enum):
    """Event processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TelegramAdminPermission(str, Enum):
    """Minimal Telegram admin permissions for personal log servers"""
    MANAGE_TOPICS = "manage_topics"                    # Create/manage topic threads
    DELETE_MESSAGES = "delete_messages"               # Delete expired logs
    RESTRICT_MEMBERS = "restrict_members"             # Bot user management
    PIN_MESSAGES = "pin_messages"                     # Pin important system messages
    MANAGE_VIDEO_CHATS = "manage_video_chats"         # Optional: voice chat for support


class PersonalServerType(str, Enum):
    """Types of personal server functionality"""
    LOG_SERVER = "log_server"                         # Activity logging
    STORAGE_SERVER = "storage_server"                 # File and data storage
    KNOWLEDGE_BASE = "knowledge_base"                 # Personal wiki/notes
    MIXED = "mixed"                                   # All functionalities combined


class Event(BaseModel):
    """Core event model with privacy controls"""
    
    # Event identification
    event_id: str = Field(..., description="Unique event identifier")
    event_type: str = Field(..., description="Event type identifier")
    category: EventCategory
    
    # Event content
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    data: Dict[str, Any] = Field(default_factory=dict, description="Event payload")
    
    # Context and source
    source: str = Field(..., description="Event source (module, service, etc.)")
    source_user_id: Optional[str] = Field(default=None, description="User who triggered event")
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")
    
    # Priority and timing
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Processing status
    status: EventStatus = Field(default=EventStatus.PENDING)
    processed_at: Optional[datetime] = Field(default=None)
    processing_duration_ms: Optional[int] = Field(default=None, ge=0)
    
    # Privacy and compliance
    contains_personal_data: bool = Field(default=False)
    retention_days: int = Field(default=30, ge=1, le=365)
    log_to_personal_server: bool = Field(default=True)
    
    # Metadata
    tags: List[str] = Field(default_factory=list, max_length=10)
    context_labels: Dict[str, str] = Field(default_factory=dict)


class EventCreate(BaseModel):
    """Event creation request"""
    
    event_type: str = Field(..., pattern=r"^[a-z_]+$", description="Event type identifier")
    category: EventCategory
    title: str = Field(..., max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Context
    source: str = Field(..., description="Event source")
    source_user_id: Optional[str] = Field(default=None)
    correlation_id: Optional[str] = Field(default=None)
    
    # Priority and timing
    priority: EventPriority = Field(default=EventPriority.NORMAL)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Privacy settings
    contains_personal_data: bool = Field(default=False)
    retention_days: int = Field(default=30, ge=1, le=365)
    log_to_personal_server: bool = Field(default=True)
    
    # Metadata
    tags: List[str] = Field(default_factory=list, max_length=10)
    context_labels: Dict[str, str] = Field(default_factory=dict)


class EventResponse(BaseModel):
    """Event creation/processing response"""
    
    success: bool
    event_id: str
    event: Optional[Event] = Field(default=None)
    
    # Processing information
    processing_time_ms: int = Field(ge=0)
    personal_log_recorded: bool = Field(default=False)
    
    # Error information
    error: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)
    
    request_id: str = Field(..., description="Unique request identifier")


class EventFilter(BaseModel):
    """Event filtering and search criteria"""
    
    # Basic filters
    categories: List[EventCategory] = Field(default_factory=list)
    priorities: List[EventPriority] = Field(default_factory=list)
    statuses: List[EventStatus] = Field(default_factory=list)
    
    # Content filters
    event_types: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # User and context filters
    user_ids: List[str] = Field(default_factory=list)
    correlation_ids: List[str] = Field(default_factory=list)
    
    # Time range filters
    created_after: Optional[datetime] = Field(default=None)
    created_before: Optional[datetime] = Field(default=None)
    
    # Text search
    search_query: Optional[str] = Field(default=None, max_length=200)
    
    # Pagination
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)
    
    # Privacy filters
    include_personal_data: bool = Field(default=False)
    user_owned_only: bool = Field(default=True, description="Only events from user's personal server")


class SystemMetric(BaseModel):
    """System performance metric"""
    
    metric_id: str = Field(..., description="Unique metric identifier")
    metric_name: str = Field(..., description="Human-readable metric name")
    metric_type: str = Field(..., pattern=r"^(counter|gauge|histogram|summary)$")
    
    # Metric value
    value: Union[int, float, str] = Field(..., description="Metric value")
    unit: Optional[str] = Field(default=None, description="Metric unit (ms, bytes, etc.)")
    
    # Context
    source: str = Field(..., description="Metric source")
    component: str = Field(..., description="System component")
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    collection_interval_seconds: Optional[int] = Field(default=None, ge=1)
    
    # Metadata
    labels: Dict[str, str] = Field(default_factory=dict)
    description: Optional[str] = Field(default=None, max_length=500)


class HealthCheck(BaseModel):
    """System health check result"""
    
    check_id: str = Field(..., description="Health check identifier")
    component: str = Field(..., description="Component being checked")
    status: str = Field(..., pattern=r"^(healthy|degraded|unhealthy)$")
    
    # Check results
    response_time_ms: Optional[int] = Field(default=None, ge=0)
    error_message: Optional[str] = Field(default=None)
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    check_type: str = Field(..., description="Type of health check")
    dependencies: List[str] = Field(default_factory=list, description="Dependent services")
    
    # Detailed information
    details: Dict[str, Any] = Field(default_factory=dict)


class PersonalServerSetupButton(BaseModel):
    """Personal server setup button configuration"""
    
    button_id: str = Field(..., description="Unique button identifier")
    button_text: str = Field(..., max_length=50, description="Button display text")
    button_emoji: str = Field(default="🔧", description="Button emoji")
    
    # Server configuration
    server_type: PersonalServerType
    server_name: str = Field(..., max_length=100)
    
    # Telegram configuration
    required_permissions: List[TelegramAdminPermission] = Field(
        default_factory=lambda: [
            TelegramAdminPermission.MANAGE_TOPICS,
            TelegramAdminPermission.DELETE_MESSAGES,
            TelegramAdminPermission.PIN_MESSAGES
        ]
    )
    
    # Setup flow
    setup_steps: List[str] = Field(default_factory=list)
    estimated_setup_time_minutes: int = Field(default=3, ge=1, le=30)
    
    # Privacy and security
    data_encryption_required: bool = Field(default=True)
    minimum_security_level: str = Field(default="standard", pattern=r"^(basic|standard|high)$")
    
    # Feature configuration
    enable_storage: bool = Field(default=False)
    enable_knowledge_base: bool = Field(default=False)
    max_storage_mb: int = Field(default=100, ge=10, le=10000)
    
    # User guidance
    description: str = Field(..., max_length=300)
    benefits: List[str] = Field(default_factory=list, max_length=5)
    warnings: List[str] = Field(default_factory=list, max_length=3)


class PersonalServerAdminRequest(BaseModel):
    """Request to create admin registration button"""
    
    user_id: str
    server_type: PersonalServerType = Field(default=PersonalServerType.MIXED)
    
    # Customization
    custom_name: Optional[str] = Field(default=None, max_length=100)
    preferred_permissions: List[TelegramAdminPermission] = Field(
        default_factory=lambda: [
            TelegramAdminPermission.MANAGE_TOPICS,
            TelegramAdminPermission.DELETE_MESSAGES
        ]
    )
    
    # Feature requests
    enable_storage: bool = Field(default=True)
    enable_knowledge_base: bool = Field(default=True)
    storage_limit_mb: int = Field(default=500, ge=10, le=5000)
    
    # Privacy preferences
    encryption_required: bool = Field(default=True)
    auto_delete_days: int = Field(default=30, ge=1, le=365)
    
    # Integration preferences
    integrate_with_existing_group: bool = Field(default=False)
    existing_group_id: Optional[int] = Field(default=None)


class PersonalServerAdminResponse(BaseModel):
    """Response with admin registration button"""
    
    success: bool
    button_id: str
    
    # Button information
    telegram_button_url: Optional[str] = Field(default=None)
    setup_instructions: List[str] = Field(default_factory=list)
    
    # Server configuration
    server_config: Optional[PersonalServerSetupButton] = Field(default=None)
    
    # Required permissions display
    permissions_explanation: Dict[str, str] = Field(default_factory=dict)
    security_notes: List[str] = Field(default_factory=list)
    
    # Error handling
    error: Optional[str] = Field(default=None)
    retry_possible: bool = Field(default=True)
    
    request_id: str = Field(..., description="Unique request identifier")


class RealTimeEventStream(BaseModel):
    """Real-time event stream configuration"""
    
    stream_id: str = Field(..., description="Stream identifier")
    user_id: str
    
    # Stream filters
    categories: List[EventCategory] = Field(default_factory=list)
    priorities: List[EventPriority] = Field(default_factory=list)
    event_types: List[str] = Field(default_factory=list)
    
    # Stream settings
    buffer_size: int = Field(default=100, ge=1, le=1000)
    max_age_seconds: int = Field(default=3600, ge=60, le=86400)  # 1 hour default, max 24 hours
    
    # Privacy settings
    include_personal_data: bool = Field(default=False)
    encrypt_stream: bool = Field(default=True)
    
    # Connection info
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    events_delivered: int = Field(default=0, ge=0)


class EventHealthResponse(BaseModel):
    """Event management module health response"""
    
    status: str = Field(..., description="Module status")
    
    # Event processing stats
    events_processed_last_hour: int = Field(ge=0)
    average_processing_time_ms: Optional[int] = Field(default=None, ge=0)
    failed_events_last_hour: int = Field(ge=0)
    
    # Queue status
    pending_events: int = Field(ge=0)
    processing_events: int = Field(ge=0)
    event_backlog_age_seconds: Optional[int] = Field(default=None, ge=0)
    
    # Personal log server integration
    personal_servers_active: int = Field(ge=0)
    personal_logs_recorded_last_hour: int = Field(ge=0)
    personal_log_success_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # System metrics
    memory_usage_mb: Optional[int] = Field(default=None, ge=0)
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Privacy compliance
    gdpr_compliant: bool = Field(default=True)
    personal_data_retention_compliant: bool = Field(default=True)
    
    # Integration status
    communication_service_connected: bool = Field(default=True)
    auth_service_connected: bool = Field(default=True)
    redis_connected: bool = Field(default=True)
    
    last_check: datetime = Field(..., description="Last health check timestamp")