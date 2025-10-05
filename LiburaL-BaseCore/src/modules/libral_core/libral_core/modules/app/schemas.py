"""
Libral APP Module - Data Schemas
Application management data models with privacy-first design
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


# Enums
class AppStatus(str, Enum):
    """Application lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AppType(str, Enum):
    """Application type classification"""
    WEB = "web"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    API = "api"
    PLUGIN = "plugin"
    MICROSERVICE = "microservice"


class AppPermission(str, Enum):
    """Application permission levels"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    OWNER = "owner"


# Base Models
class AppBase(BaseModel):
    """Base application model"""
    name: str = Field(..., min_length=1, max_length=255, description="Application name")
    description: Optional[str] = Field(None, max_length=1000, description="Application description")
    app_type: AppType = Field(default=AppType.WEB, description="Application type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    tags: List[str] = Field(default_factory=list, description="Application tags")


class AppCreate(AppBase):
    """Schema for creating a new application"""
    owner_id: str = Field(..., description="Owner user ID")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Application settings")


class AppUpdate(BaseModel):
    """Schema for updating an existing application"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    app_type: Optional[AppType] = None
    status: Optional[AppStatus] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    settings: Optional[Dict[str, Any]] = None


class App(AppBase):
    """Complete application model"""
    app_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique application ID")
    owner_id: str = Field(..., description="Owner user ID")
    status: AppStatus = Field(default=AppStatus.DRAFT, description="Application status")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Application settings")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    access_count: int = Field(default=0, description="Total access count")
    
    class Config:
        from_attributes = True


# App Permission Models
class AppPermissionBase(BaseModel):
    """Base permission model"""
    app_id: str = Field(..., description="Application ID")
    user_id: str = Field(..., description="User ID")
    permission: AppPermission = Field(..., description="Permission level")


class AppPermissionCreate(AppPermissionBase):
    """Schema for creating application permission"""
    pass


class AppPermissionModel(AppPermissionBase):
    """Complete permission model"""
    permission_id: str = Field(default_factory=lambda: str(uuid4()), description="Permission ID")
    granted_at: datetime = Field(default_factory=datetime.utcnow, description="Grant timestamp")
    granted_by: str = Field(..., description="User who granted permission")
    
    class Config:
        from_attributes = True


# App Analytics Models
class AppAnalytics(BaseModel):
    """Application analytics and usage statistics"""
    app_id: str = Field(..., description="Application ID")
    total_accesses: int = Field(default=0, description="Total access count")
    unique_users: int = Field(default=0, description="Unique user count")
    last_24h_accesses: int = Field(default=0, description="Accesses in last 24 hours")
    average_response_time_ms: float = Field(default=0.0, description="Average response time")
    error_rate: float = Field(default=0.0, description="Error rate percentage")
    
    class Config:
        from_attributes = True


# Health and Status Models
class AppHealth(BaseModel):
    """Application health status"""
    app_id: str = Field(..., description="Application ID")
    status: str = Field(..., description="Health status")
    uptime_percentage: float = Field(default=100.0, description="Uptime percentage")
    last_health_check: datetime = Field(default_factory=datetime.utcnow)
    issues: List[str] = Field(default_factory=list, description="Current issues")


class AppModuleHealth(BaseModel):
    """APP Module health response"""
    status: str = Field(default="healthy", description="Overall status")
    version: str = Field(default="1.0.0", description="Module version")
    components: Dict[str, Any] = Field(default_factory=dict, description="Component health")
    total_apps: int = Field(default=0, description="Total applications")
    active_apps: int = Field(default=0, description="Active applications")
    uptime_seconds: float = Field(default=0.0, description="Module uptime")
    last_health_check: datetime = Field(default_factory=datetime.utcnow)


# Configuration Models
class AppConfig(BaseModel):
    """APP Module configuration"""
    database_url: str = Field(default="postgresql://localhost/libral_app")
    redis_url: str = Field(default="redis://localhost:6379")
    cache_ttl_hours: int = Field(default=24, description="Cache TTL in hours")
    max_apps_per_user: int = Field(default=100, description="Maximum apps per user")
    enable_analytics: bool = Field(default=True, description="Enable analytics")
    enable_permissions: bool = Field(default=True, description="Enable permission system")
    auto_archive_days: int = Field(default=90, description="Auto-archive after N days of inactivity")
    
    class Config:
        env_prefix = "APP_"


# Response Models
class AppListResponse(BaseModel):
    """Response for listing applications"""
    apps: List[App] = Field(default_factory=list, description="List of applications")
    total: int = Field(default=0, description="Total count")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=50, description="Page size")


class AppOperationResponse(BaseModel):
    """Generic operation response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    app_id: Optional[str] = Field(None, description="Application ID")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")


# Error Models
class AppError(BaseModel):
    """Application error model"""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
