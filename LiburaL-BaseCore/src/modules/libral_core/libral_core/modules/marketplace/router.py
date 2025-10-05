"""
Plugin Marketplace FastAPI Router
RESTful endpoints for plugin discovery, installation, and management
"""

from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    MarketplaceConfig,
    MarketplaceHealthResponse,
    PluginInfo,
    PluginInstallRequest,
    PluginInstallResponse,
    PluginMetadata,
    PluginSearchRequest,
    PluginSearchResponse
)
from .service import MarketplaceService
from ..gpg.service import GPGService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/marketplace", tags=["Plugin Marketplace"])

# Global marketplace service instance
_marketplace_service: Optional[MarketplaceService] = None

def get_marketplace_service() -> MarketplaceService:
    """Get configured marketplace service instance"""
    global _marketplace_service
    
    if _marketplace_service is None:
        # Initialize marketplace configuration
        marketplace_config = MarketplaceConfig(
            marketplace_url="https://marketplace.libral.app",
            plugins_directory="./data/plugins",
            temp_directory="./tmp/marketplace",
            require_gpg_signatures=True,
            trusted_publishers_only=False,
            security_scan_required=True,
            auto_update_enabled=False,
            max_plugin_size_mb=100,
            installation_timeout_seconds=300,
            cache_duration_hours=24
        )
        
        # Initialize GPG service for plugin verification
        try:
            gpg_service = GPGService(
                gnupg_home=settings.gpg_home,
                system_key_id=settings.gpg_system_key_id,
                passphrase=settings.gpg_passphrase
            )
        except Exception as e:
            logger.warning("GPG service unavailable for plugin verification", error=str(e))
            gpg_service = None
        
        _marketplace_service = MarketplaceService(
            config=marketplace_config,
            gpg_service=gpg_service
        )
        
        logger.info("Marketplace service initialized")
    
    return _marketplace_service

@router.get("/health", response_model=MarketplaceHealthResponse)
async def health_check(
    service: MarketplaceService = Depends(get_marketplace_service)
) -> MarketplaceHealthResponse:
    """Check marketplace service health and connectivity"""
    return await service.health_check()

@router.get("/search", response_model=PluginSearchResponse)
async def search_plugins(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Plugin category"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    pricing: Optional[str] = Query(None, description="Pricing model filter"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    trusted_only: bool = Query(False, description="Show only trusted publishers"),
    featured_only: bool = Query(False, description="Show only featured plugins"),
    sort_by: str = Query("relevance", pattern="^(relevance|downloads|rating|updated|name|price)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Results per page"),
    service: MarketplaceService = Depends(get_marketplace_service)
) -> PluginSearchResponse:
    """
    Search for plugins in the marketplace
    
    - **q**: Search query for plugin name, description, or tags
    - **category**: Filter by plugin category (ai-agents, creative-tools, etc.)
    - **tags**: Filter by comma-separated tags
    - **pricing**: Filter by pricing model (free, one_time, subscription, etc.)
    - **price_max**: Maximum price filter for paid plugins
    - **trusted_only**: Show only plugins from verified publishers
    - **featured_only**: Show only featured/editor's choice plugins
    - **sort_by**: Sort results by relevance, downloads, rating, updated, name, or price
    - **sort_order**: Sort order (asc or desc)
    - **page**: Page number for pagination
    - **per_page**: Number of results per page (1-100)
    """
    try:
        # Convert query parameters to search request
        search_request = PluginSearchRequest(
            query=q,
            category=category,
            tags=tags.split(',') if tags else [],
            pricing_model=pricing,
            price_max=price_max,
            trusted_only=trusted_only,
            featured_only=featured_only,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )
        
        result = await service.search_plugins(search_request)
        
        logger.info("Plugin search completed",
                   query=q,
                   results_count=len(result.plugins),
                   total_count=result.total_count)
        
        return result
    except Exception as e:
        logger.error("Plugin search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Plugin search failed")

@router.get("/plugins/{plugin_id}", response_model=PluginInfo)
async def get_plugin_info(
    plugin_id: str,
    service: MarketplaceService = Depends(get_marketplace_service)
) -> PluginInfo:
    """
    Get detailed information about a specific plugin
    
    Returns comprehensive plugin metadata including:
    - Plugin manifest and technical details
    - Download statistics and user ratings
    - Pricing and revenue sharing information
    - Security scan results and compatibility data
    - Screenshots and media content
    """
    try:
        plugin_info = await service.get_plugin_info(plugin_id)
        
        if not plugin_info:
            raise HTTPException(status_code=404, detail=f"Plugin '{plugin_id}' not found")
        
        logger.info("Plugin info retrieved", plugin_id=plugin_id)
        return plugin_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to retrieve plugin info", plugin_id=plugin_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve plugin information")

@router.post("/plugins/{plugin_id}/install", response_model=PluginInstallResponse)
async def install_plugin(
    plugin_id: str,
    request: PluginInstallRequest,
    service: MarketplaceService = Depends(get_marketplace_service)
) -> PluginInstallResponse:
    """
    Install a plugin from the marketplace
    
    **Security Features:**
    - GPG signature verification for plugin authenticity
    - Sandboxed execution environment with permission validation
    - Dependency resolution and security scanning
    - Checksum verification for download integrity
    - Plugin code analysis for unsafe patterns
    
    **Installation Process:**
    1. Download plugin from marketplace
    2. Verify GPG signature and checksum
    3. Extract to secure sandbox environment
    4. Validate manifest and permissions
    5. Install dependencies if requested
    6. Register plugin in local registry
    7. Enable plugin if auto_enable is true
    
    **Privacy Compliance:**
    - No personal data is transmitted to marketplace
    - Plugin installations are logged locally only
    - User consent required for sensitive permissions
    """
    try:
        # Set the plugin_id from URL parameter
        request.plugin_id = plugin_id
        
        result = await service.install_plugin(request)
        
        # Log installation outcome (no sensitive data)
        logger.info("Plugin installation completed",
                   plugin_id=plugin_id,
                   success=result.success,
                   version=result.installed_version,
                   warnings_count=len(result.warnings))
        
        return result
        
    except Exception as e:
        logger.error("Plugin installation error", plugin_id=plugin_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Plugin installation failed: {str(e)}")

@router.delete("/plugins/{plugin_id}")
async def uninstall_plugin(
    plugin_id: str,
    service: MarketplaceService = Depends(get_marketplace_service)
) -> JSONResponse:
    """
    Uninstall a plugin and remove all associated files
    
    **Uninstallation Process:**
    1. Verify plugin is currently installed
    2. Disable plugin if currently active
    3. Remove plugin files and directories
    4. Clean up plugin registry entries
    5. Log uninstallation for audit trail
    
    **Data Cleanup:**
    - All plugin files are permanently removed
    - Plugin configuration data is cleared
    - No personal data is retained after uninstall
    """
    try:
        result = await service.uninstall_plugin(plugin_id)
        
        if result["success"]:
            logger.info("Plugin uninstalled successfully", plugin_id=plugin_id)
            return JSONResponse(
                content=result,
                status_code=200
            )
        else:
            logger.warning("Plugin uninstallation failed", 
                         plugin_id=plugin_id, 
                         error=result.get("error"))
            return JSONResponse(
                content=result,
                status_code=400
            )
            
    except Exception as e:
        logger.error("Plugin uninstallation error", plugin_id=plugin_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Plugin uninstallation failed: {str(e)}")

@router.get("/plugins/installed", response_model=List[PluginMetadata])
async def list_installed_plugins(
    service: MarketplaceService = Depends(get_marketplace_service)
) -> List[PluginMetadata]:
    """
    List all currently installed plugins
    
    Returns metadata for all plugins installed on this Libral Core instance,
    including installation status, version information, and configuration details.
    
    **Privacy Note:** Only locally installed plugins are shown. No data is
    transmitted to external services for this operation.
    """
    try:
        plugins = await service.list_installed_plugins()
        
        logger.info("Listed installed plugins", count=len(plugins))
        return plugins
        
    except Exception as e:
        logger.error("Failed to list installed plugins", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve installed plugins")

@router.post("/plugins/{plugin_id}/enable")
async def enable_plugin(
    plugin_id: str,
    service: MarketplaceService = Depends(get_marketplace_service)
) -> JSONResponse:
    """
    Enable an installed plugin
    
    Activates a previously installed but disabled plugin. The plugin will
    become available for use after the next system restart.
    """
    try:
        success = await service.enable_plugin(plugin_id)
        
        if success:
            logger.info("Plugin enabled", plugin_id=plugin_id)
            return JSONResponse(
                content={
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "enabled",
                    "restart_required": True
                }
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "plugin_id": plugin_id,
                    "error": "Plugin not found or not installed"
                },
                status_code=404
            )
            
    except Exception as e:
        logger.error("Failed to enable plugin", plugin_id=plugin_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to enable plugin: {str(e)}")

@router.post("/plugins/{plugin_id}/disable")
async def disable_plugin(
    plugin_id: str,
    service: MarketplaceService = Depends(get_marketplace_service)
) -> JSONResponse:
    """
    Disable an installed plugin
    
    Deactivates a currently enabled plugin. The plugin will remain installed
    but will not be loaded after the next system restart.
    """
    try:
        success = await service.disable_plugin(plugin_id)
        
        if success:
            logger.info("Plugin disabled", plugin_id=plugin_id)
            return JSONResponse(
                content={
                    "success": True,
                    "plugin_id": plugin_id,
                    "status": "disabled",
                    "restart_required": True
                }
            )
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "plugin_id": plugin_id,
                    "error": "Plugin not found or not installed"
                },
                status_code=404
            )
            
    except Exception as e:
        logger.error("Failed to disable plugin", plugin_id=plugin_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to disable plugin: {str(e)}")

@router.get("/categories")
async def list_plugin_categories() -> JSONResponse:
    """
    Get list of available plugin categories
    
    Returns all plugin categories available in the marketplace for filtering
    and organization purposes.
    """
    try:
        from .schemas import PluginCategory
        
        categories = [
            {
                "id": category.value,
                "name": category.value.replace("-", " ").title(),
                "description": _get_category_description(category)
            }
            for category in PluginCategory
        ]
        
        return JSONResponse(content={"categories": categories})
        
    except Exception as e:
        logger.error("Failed to list plugin categories", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve plugin categories")

def _get_category_description(category) -> str:
    """Get human-readable description for plugin category"""
    descriptions = {
        "ai-agents": "AI-powered assistants and automation tools",
        "creative-tools": "Content creation and artistic tools",
        "productivity": "Workflow optimization and task management",
        "integrations": "Third-party service integrations",
        "utilities": "System utilities and helper tools",
        "security": "Security and privacy enhancement tools",
        "communication": "Messaging and collaboration tools",
        "analytics": "Data analysis and reporting tools",
        "experimental": "Experimental and beta features"
    }
    return descriptions.get(category.value, "Miscellaneous plugins")

# Cleanup handler
@router.on_event("shutdown")
async def cleanup_marketplace():
    """Cleanup marketplace resources on shutdown"""
    global _marketplace_service
    if _marketplace_service:
        await _marketplace_service.cleanup()
        _marketplace_service = None
        logger.info("Marketplace service cleanup completed")