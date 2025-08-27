"""
Plugin Marketplace Schemas
Type-safe contracts for plugin management and marketplace operations
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from decimal import Decimal

from pydantic import BaseModel, Field, validator


class PluginCategory(str, Enum):
    """Plugin categories for marketplace organization"""
    AI_AGENTS = "ai-agents"
    CREATIVE_TOOLS = "creative-tools"  
    PRODUCTIVITY = "productivity"
    INTEGRATIONS = "integrations"
    UTILITIES = "utilities"
    SECURITY = "security"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    EXPERIMENTAL = "experimental"


class PluginStatus(str, Enum):
    """Plugin status in marketplace"""
    AVAILABLE = "available"
    INSTALLED = "installed"
    UPDATING = "updating"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"
    PENDING_APPROVAL = "pending_approval"


class PluginPricingModel(str, Enum):
    """Plugin pricing models"""
    FREE = "free"
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    USAGE_BASED = "usage_based"
    FREEMIUM = "freemium"


class PluginPermission(BaseModel):
    """Plugin permission request"""
    name: str = Field(..., description="Permission name")
    description: str = Field(..., description="Human-readable permission description")
    required: bool = Field(default=True, description="Whether permission is required")
    sensitive: bool = Field(default=False, description="Whether permission accesses sensitive data")


class PluginDependency(BaseModel):
    """Plugin dependency specification"""
    name: str = Field(..., description="Dependency name")
    version: str = Field(..., description="Required version (semver)")
    optional: bool = Field(default=False, description="Whether dependency is optional")
    marketplace_id: Optional[str] = Field(default=None, description="Marketplace plugin ID if available")


class PluginManifest(BaseModel):
    """Plugin manifest file structure"""
    
    # Core Plugin Information
    name: str = Field(..., min_length=3, max_length=50)
    id: str = Field(..., regex=r"^[a-z0-9-]+$", description="Unique plugin identifier")
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$", description="Semantic version")
    description: str = Field(..., min_length=10, max_length=500)
    category: PluginCategory
    
    # Developer Information
    developer_name: str = Field(..., max_length=100)
    developer_email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    developer_website: Optional[str] = Field(default=None)
    
    # Technical Specifications
    main_entry: str = Field(..., description="Main plugin entry point file")
    api_version: str = Field(default="1.0.0", description="Required Libral Core API version")
    python_version: str = Field(default=">=3.11", description="Required Python version")
    
    # Dependencies and Permissions
    dependencies: List[PluginDependency] = Field(default_factory=list)
    permissions: List[PluginPermission] = Field(default_factory=list)
    
    # Pricing and Distribution
    pricing_model: PluginPricingModel = Field(default=PluginPricingModel.FREE)
    price: Optional[Decimal] = Field(default=None, ge=0, description="Price in USD")
    subscription_monthly: Optional[Decimal] = Field(default=None, ge=0)
    
    # Security and Trust
    gpg_signature: Optional[str] = Field(default=None, description="GPG signature for plugin verification")
    trusted_publisher: bool = Field(default=False, description="Whether developer is verified")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, max_items=10)
    homepage: Optional[str] = Field(default=None)
    repository: Optional[str] = Field(default=None)
    documentation: Optional[str] = Field(default=None)
    changelog: Optional[str] = Field(default=None)
    
    @validator('tags')
    def validate_tags(cls, v):
        if v:
            # Normalize tags to lowercase and remove duplicates
            return list(set(tag.lower().strip() for tag in v if tag.strip()))
        return v


class PluginMetadata(BaseModel):
    """Extended plugin metadata for marketplace listing"""
    
    manifest: PluginManifest
    
    # Marketplace Statistics
    download_count: int = Field(default=0, ge=0)
    rating_average: Optional[float] = Field(default=None, ge=0, le=5)
    rating_count: int = Field(default=0, ge=0)
    review_count: int = Field(default=0, ge=0)
    
    # Timestamps
    published_at: datetime
    updated_at: datetime
    last_download_at: Optional[datetime] = Field(default=None)
    
    # Status Information
    status: PluginStatus = Field(default=PluginStatus.AVAILABLE)
    featured: bool = Field(default=False)
    editor_choice: bool = Field(default=False)
    
    # Compatibility
    tested_libral_versions: List[str] = Field(default_factory=list)
    compatibility_score: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Security Information
    security_scan_passed: bool = Field(default=False)
    security_scan_date: Optional[datetime] = Field(default=None)
    vulnerability_count: int = Field(default=0, ge=0)


class PluginInfo(BaseModel):
    """Complete plugin information for API responses"""
    
    metadata: PluginMetadata
    
    # Installation Information
    download_url: str
    download_size: int = Field(ge=0, description="Download size in bytes")
    checksum_sha256: str
    
    # Revenue Sharing (for paid plugins)
    revenue_share_developer: Optional[float] = Field(default=None, ge=0, le=1)
    revenue_share_platform: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Plugin Screenshots and Media
    screenshots: List[str] = Field(default_factory=list, max_items=5)
    icon_url: Optional[str] = Field(default=None)
    
    @validator('revenue_share_developer', 'revenue_share_platform')
    def validate_revenue_shares(cls, v, values):
        if v is not None and 'revenue_share_developer' in values and 'revenue_share_platform' in values:
            dev_share = values.get('revenue_share_developer', 0)
            platform_share = values.get('revenue_share_platform', 0)
            if dev_share + platform_share != 1.0:
                raise ValueError('Revenue shares must sum to 1.0')
        return v


# Request/Response Schemas
class PluginSearchRequest(BaseModel):
    """Plugin search request"""
    
    query: Optional[str] = Field(default=None, max_length=100, description="Search query")
    category: Optional[PluginCategory] = Field(default=None)
    tags: List[str] = Field(default_factory=list, max_items=5)
    
    # Filters
    pricing_model: Optional[PluginPricingModel] = Field(default=None)
    price_max: Optional[Decimal] = Field(default=None, ge=0)
    trusted_only: bool = Field(default=False)
    featured_only: bool = Field(default=False)
    
    # Sorting and Pagination
    sort_by: str = Field(default="relevance", regex="^(relevance|downloads|rating|updated|name|price)$")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class PluginSearchResponse(BaseModel):
    """Plugin search response"""
    
    plugins: List[PluginInfo]
    total_count: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    has_more: bool
    
    # Search Metadata
    query: Optional[str]
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    search_time_ms: int = Field(ge=0)


class PluginInstallRequest(BaseModel):
    """Plugin installation request"""
    
    plugin_id: str = Field(..., description="Plugin marketplace ID")
    version: Optional[str] = Field(default=None, description="Specific version to install")
    
    # Installation Options
    auto_enable: bool = Field(default=True)
    install_dependencies: bool = Field(default=True)
    accept_permissions: bool = Field(default=False, description="Accept all requested permissions")
    
    # User Context
    user_id: Optional[str] = Field(default=None, description="Installing user ID")
    installation_context: Dict[str, Any] = Field(default_factory=dict)


class PluginInstallResponse(BaseModel):
    """Plugin installation response"""
    
    success: bool
    plugin_id: str
    installed_version: Optional[str] = Field(default=None)
    
    # Installation Details
    installation_path: Optional[str] = Field(default=None)
    dependencies_installed: List[str] = Field(default_factory=list)
    permissions_granted: List[str] = Field(default_factory=list)
    
    # Status Information
    enabled: bool = Field(default=False)
    restart_required: bool = Field(default=False)
    
    # Error Information
    error: Optional[str] = Field(default=None)
    warnings: List[str] = Field(default_factory=list)
    
    # Transaction Information (for paid plugins)
    transaction_id: Optional[str] = Field(default=None)
    amount_charged: Optional[Decimal] = Field(default=None, ge=0)
    
    request_id: str = Field(..., description="Unique request identifier")


class MarketplaceConfig(BaseModel):
    """Marketplace configuration"""
    
    # API Configuration
    marketplace_url: str = Field(default="https://marketplace.libral.app")
    api_key: Optional[str] = Field(default=None)
    
    # Plugin Directory
    plugins_directory: str = Field(default="./plugins")
    temp_directory: str = Field(default="./temp/plugins")
    
    # Security Settings
    require_gpg_signatures: bool = Field(default=True)
    trusted_publishers_only: bool = Field(default=False)
    security_scan_required: bool = Field(default=True)
    
    # Installation Settings
    auto_update_enabled: bool = Field(default=False)
    max_plugin_size_mb: int = Field(default=100, ge=1)
    installation_timeout_seconds: int = Field(default=300, ge=30)
    
    # Revenue Sharing
    default_platform_share: float = Field(default=0.3, ge=0, le=1)
    
    # Cache Settings
    cache_duration_hours: int = Field(default=24, ge=1)
    metadata_refresh_interval: int = Field(default=3600, ge=300, description="Seconds")


# Health and Status Schemas
class MarketplaceHealthResponse(BaseModel):
    """Marketplace module health check response"""
    
    status: str = Field(..., description="Module status")
    marketplace_url: str = Field(..., description="Marketplace API URL")
    plugins_installed: int = Field(ge=0)
    plugins_enabled: int = Field(ge=0)
    
    # Connectivity
    api_accessible: bool
    last_sync: Optional[datetime] = Field(default=None)
    
    # Storage Status
    plugins_directory: str
    available_disk_space_mb: Optional[int] = Field(default=None, ge=0)
    
    # Configuration Status
    gpg_verification_enabled: bool
    security_scanning_enabled: bool
    auto_updates_enabled: bool
    
    last_check: datetime = Field(..., description="Last health check timestamp")