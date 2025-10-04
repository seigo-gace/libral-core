"""
Plugin Marketplace Module - Week 2 Extension
Third-party module discovery, installation, and management system

Features:
- Plugin discovery and search
- Secure plugin installation with GPG verification
- Plugin dependency management
- Sandboxed execution environment
- Plugin lifecycle management
- Revenue sharing for plugin developers
"""

from .service import MarketplaceService
from .schemas import (
    PluginInfo,
    PluginSearchRequest,
    PluginSearchResponse,
    PluginInstallRequest,
    PluginInstallResponse,
    PluginMetadata,
    PluginManifest,
    MarketplaceConfig
)

__all__ = [
    "MarketplaceService",
    "PluginInfo", 
    "PluginSearchRequest",
    "PluginSearchResponse",
    "PluginInstallRequest",
    "PluginInstallResponse",
    "PluginMetadata",
    "PluginManifest",
    "MarketplaceConfig"
]