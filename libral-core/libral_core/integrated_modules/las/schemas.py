"""
Libral Asset Service (LAS) - Unified Schemas
Integrated Library utilities + UI Asset Management + WebAssembly functionality
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, BinaryIO
from decimal import Decimal
import mimetypes

from pydantic import BaseModel, Field, field_validator


# Asset Types
class AssetType(str, Enum):
    """Supported asset types"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    FONT = "font"
    STYLE = "style"  # CSS
    SCRIPT = "script"  # JS
    WASM = "wasm"  # WebAssembly
    BINARY = "binary"
    TEXT = "text"
    ARCHIVE = "archive"


class ProcessingStatus(str, Enum):
    """Asset processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    OPTIMIZED = "optimized"
    CACHED = "cached"


class AssetFormat(str, Enum):
    """Asset format specifications"""
    # Images
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    SVG = "svg"
    GIF = "gif"
    AVIF = "avif"
    
    # Videos
    MP4 = "mp4"
    WEBM = "webm"
    AVI = "avi"
    MOV = "mov"
    
    # Audio
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    AAC = "aac"
    
    # Documents
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    
    # Web Assets
    CSS = "css"
    JS = "js"
    HTML = "html"
    JSON = "json"
    
    # WebAssembly
    WASM = "wasm"
    WAT = "wat"  # WebAssembly Text


class OptimizationLevel(str, Enum):
    """Asset optimization levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class AccessLevel(str, Enum):
    """Asset access control levels"""
    PUBLIC = "public"
    AUTHENTICATED = "authenticated"
    PRIVATE = "private"
    RESTRICTED = "restricted"


# Core Asset Schema
class Asset(BaseModel):
    """Core asset representation"""
    asset_id: str = Field(..., description="Unique asset identifier")
    
    # Basic metadata
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=1024)
    asset_type: AssetType
    format: AssetFormat
    mime_type: str
    
    # File properties
    file_size: int = Field(..., ge=0, description="File size in bytes")
    checksum: str = Field(..., description="SHA-256 checksum")
    original_filename: Optional[str] = None
    
    # Storage information
    storage_path: str = Field(..., description="Storage location path")
    cdn_url: Optional[str] = None
    cache_url: Optional[str] = None
    
    # Processing metadata
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.MEDIUM)
    processed_variants: Dict[str, str] = Field(default_factory=dict)
    
    # Access control
    access_level: AccessLevel = Field(default=AccessLevel.PRIVATE)
    owner_id: str = Field(..., description="Asset owner user ID")
    allowed_users: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Additional metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Asset-specific properties
    dimensions: Optional[Dict[str, int]] = None  # width, height for images/videos
    duration: Optional[float] = None  # duration in seconds for audio/video
    quality: Optional[str] = None  # quality indicator


# Utility Library Schemas
class StringProcessingRequest(BaseModel):
    """String processing operation request"""
    operation: str = Field(..., description="sanitize|truncate|validate|format")
    input_text: str
    options: Dict[str, Any] = Field(default_factory=dict)


class StringProcessingResponse(BaseModel):
    """String processing operation response"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DateTimeProcessingRequest(BaseModel):
    """DateTime processing operation request"""
    operation: str = Field(..., description="parse|format|convert|validate")
    input_datetime: Optional[str] = None
    timezone: Optional[str] = Field(default="UTC")
    format_string: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)


class DateTimeProcessingResponse(BaseModel):
    """DateTime processing operation response"""
    success: bool
    result: Optional[str] = None
    timestamp: Optional[datetime] = None
    timezone: Optional[str] = None
    error: Optional[str] = None


# API Client Schemas
class APIClientConfig(BaseModel):
    """External API client configuration"""
    client_id: str
    name: str
    base_url: str
    api_version: Optional[str] = None
    
    # Authentication
    auth_type: str = Field(default="bearer", description="bearer|basic|api_key|oauth2")
    auth_token: Optional[str] = None
    api_key: Optional[str] = None
    
    # Request configuration
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    rate_limit_per_minute: Optional[int] = None
    
    # Headers and options
    default_headers: Dict[str, str] = Field(default_factory=dict)
    custom_options: Dict[str, Any] = Field(default_factory=dict)


class APIRequest(BaseModel):
    """External API request"""
    client_id: str
    method: str = Field(..., pattern="^(GET|POST|PUT|DELETE|PATCH)$")
    endpoint: str
    
    # Request data
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    json_data: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, str]] = None
    
    # Options
    timeout: Optional[int] = None
    stream: bool = Field(default=False)
    verify_ssl: bool = Field(default=True)


class APIResponse(BaseModel):
    """External API response"""
    success: bool
    status_code: int
    headers: Dict[str, str] = Field(default_factory=dict)
    
    # Response data
    data: Optional[Any] = None
    text: Optional[str] = None
    json_data: Optional[Dict[str, Any]] = None
    
    # Metadata
    response_time_ms: float
    request_id: str
    error: Optional[str] = None


# File Processing Schemas
class ImageProcessingRequest(BaseModel):
    """Image processing request"""
    asset_id: str
    operations: List[Dict[str, Any]] = Field(..., description="List of processing operations")
    output_format: Optional[AssetFormat] = None
    quality: Optional[int] = Field(default=85, ge=1, le=100)
    optimization: OptimizationLevel = Field(default=OptimizationLevel.MEDIUM)


class VideoProcessingRequest(BaseModel):
    """Video processing request"""
    asset_id: str
    operations: List[Dict[str, Any]] = Field(..., description="List of processing operations")
    output_format: Optional[AssetFormat] = None
    quality: Optional[str] = Field(default="medium")
    resolution: Optional[str] = None
    frame_rate: Optional[int] = None


class ProcessingResult(BaseModel):
    """File processing result"""
    success: bool
    processed_asset_id: Optional[str] = None
    output_url: Optional[str] = None
    processing_time_ms: float
    file_size_reduction: Optional[float] = None  # Percentage reduction
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# WebAssembly Schemas
class WASMModule(BaseModel):
    """WebAssembly module definition"""
    module_id: str
    name: str
    description: Optional[str] = None
    
    # Module file
    wasm_asset_id: str
    wat_source: Optional[str] = None  # WebAssembly text source
    
    # Execution environment
    memory_pages: int = Field(default=1, ge=1, le=65536)  # 64KB pages
    max_memory: Optional[int] = None
    table_size: Optional[int] = None
    
    # Imported functions
    imports: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    exports: Dict[str, str] = Field(default_factory=dict)
    
    # Security and access
    sandbox_enabled: bool = Field(default=True)
    allowed_users: List[str] = Field(default_factory=list)
    execution_timeout_ms: int = Field(default=5000, ge=100, le=60000)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")


class WASMExecutionRequest(BaseModel):
    """WebAssembly execution request"""
    module_id: str
    function_name: str
    
    # Function parameters
    parameters: List[Any] = Field(default_factory=list)
    parameter_types: List[str] = Field(default_factory=list)  # i32, i64, f32, f64
    
    # Execution options
    timeout_ms: Optional[int] = None
    memory_limit: Optional[int] = None
    enable_debug: bool = Field(default=False)
    
    # Context
    user_id: str
    session_context: Dict[str, Any] = Field(default_factory=dict)


class WASMExecutionResponse(BaseModel):
    """WebAssembly execution response"""
    success: bool
    result: Optional[Any] = None
    result_type: Optional[str] = None
    
    # Execution metadata
    execution_time_ms: float
    memory_used: int
    instructions_executed: Optional[int] = None
    
    # Error information
    error: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[List[str]] = None


# Asset Management Schemas
class AssetUploadRequest(BaseModel):
    """Asset upload request"""
    name: str
    description: Optional[str] = None
    asset_type: AssetType
    access_level: AccessLevel = Field(default=AccessLevel.PRIVATE)
    
    # Processing options
    auto_optimize: bool = Field(default=True)
    optimization_level: OptimizationLevel = Field(default=OptimizationLevel.MEDIUM)
    generate_thumbnails: bool = Field(default=True)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Expiration
    expires_in_hours: Optional[int] = None


class AssetUploadResponse(BaseModel):
    """Asset upload response"""
    success: bool
    asset_id: Optional[str] = None
    upload_url: Optional[str] = None
    asset_url: Optional[str] = None
    processing_status: ProcessingStatus
    error: Optional[str] = None


class AssetQuery(BaseModel):
    """Asset query parameters"""
    asset_types: Optional[List[AssetType]] = None
    formats: Optional[List[AssetFormat]] = None
    tags: Optional[List[str]] = None
    owner_id: Optional[str] = None
    access_level: Optional[AccessLevel] = None
    
    # Date filters
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    
    # Pagination
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    
    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class AssetSearchResponse(BaseModel):
    """Asset search response"""
    assets: List[Asset]
    total_count: int
    has_more: bool
    next_offset: Optional[int] = None


# System Health and Statistics
class LASHealthResponse(BaseModel):
    """LAS module health status"""
    status: str
    version: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "utilities": {"status": "unknown", "operations_processed": 0},
        "api_clients": {"status": "unknown", "active_clients": 0, "requests_today": 0},
        "file_processing": {"status": "unknown", "queue_size": 0, "processed_today": 0},
        "asset_management": {"status": "unknown", "total_assets": 0, "storage_used_mb": 0},
        "wasm_runtime": {"status": "unknown", "loaded_modules": 0, "executions_today": 0}
    })
    uptime_seconds: float
    last_health_check: datetime


class LASMetrics(BaseModel):
    """LAS module metrics"""
    period_start: datetime
    period_end: datetime
    
    # Utility operations
    string_operations: int
    datetime_operations: int
    validation_operations: int
    
    # API client metrics
    api_requests_made: int
    api_success_rate: float
    api_average_response_time_ms: float
    
    # File processing
    images_processed: int
    videos_processed: int
    total_processing_time_ms: float
    storage_savings_mb: float
    
    # Asset management
    assets_uploaded: int
    assets_downloaded: int
    cdn_hits: int
    cdn_miss_rate: float
    
    # WebAssembly
    wasm_modules_loaded: int
    wasm_executions: int
    wasm_average_execution_time_ms: float
    wasm_memory_usage_mb: float


# Error Schema
class LASError(BaseModel):
    """LAS module error response"""
    error_code: str
    error_message: str
    component: str = Field(..., description="utilities|api_clients|file_processing|asset_management|wasm_runtime")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str