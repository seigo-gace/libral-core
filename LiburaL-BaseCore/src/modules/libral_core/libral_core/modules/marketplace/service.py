"""
Plugin Marketplace Service
Manages plugin discovery, installation, and lifecycle with privacy-first principles
"""

import asyncio
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

import httpx
import structlog
from packaging import version

from .schemas import (
    MarketplaceConfig,
    MarketplaceHealthResponse,
    PluginInfo,
    PluginInstallRequest,
    PluginInstallResponse,
    PluginManifest,
    PluginMetadata,
    PluginSearchRequest,
    PluginSearchResponse,
    PluginStatus
)
from ..gpg.service import GPGService
from ..gpg.schemas import VerifyRequest

logger = structlog.get_logger(__name__)


class PluginSandbox:
    """Secure plugin execution sandbox"""
    
    def __init__(self, plugin_path: str, allowed_permissions: List[str]):
        self.plugin_path = Path(plugin_path)
        self.allowed_permissions = set(allowed_permissions)
        self.restricted_imports = {
            'os.system', 'subprocess', 'eval', 'exec', 'open',
            '__import__', 'importlib', 'sys.exit'
        }
    
    def validate_plugin_safety(self, manifest: PluginManifest) -> Tuple[bool, List[str]]:
        """Validate plugin safety and permissions"""
        warnings = []
        
        # Check requested permissions
        for permission in manifest.permissions:
            if permission.name not in self.allowed_permissions:
                if permission.required:
                    return False, [f"Required permission '{permission.name}' not allowed"]
                else:
                    warnings.append(f"Optional permission '{permission.name}' will be denied")
        
        # Basic code analysis for restricted patterns
        try:
            main_file = self.plugin_path / manifest.main_entry
            if main_file.exists():
                content = main_file.read_text()
                
                for restricted in self.restricted_imports:
                    if restricted in content:
                        warnings.append(f"Potentially unsafe code pattern detected: {restricted}")
                        
        except Exception as e:
            warnings.append(f"Could not analyze plugin code: {e}")
        
        return True, warnings


class MarketplaceService:
    """Core plugin marketplace service with security and privacy focus"""
    
    def __init__(
        self,
        config: MarketplaceConfig,
        gpg_service: Optional[GPGService] = None
    ):
        self.config = config
        self.gpg_service = gpg_service
        
        # Initialize directories
        self.plugins_dir = Path(config.plugins_directory)
        self.temp_dir = Path(config.temp_directory)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Plugin registry (in-memory for development, should use database in production)
        self.installed_plugins: Dict[str, PluginMetadata] = {}
        self.plugin_cache: Dict[str, Tuple[datetime, PluginInfo]] = {}
        
        # HTTP client for marketplace API
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Libral-Core-Marketplace/1.0",
                "X-API-Key": config.api_key or ""
            }
        )
        
        logger.info("Marketplace service initialized",
                   plugins_dir=str(self.plugins_dir),
                   marketplace_url=config.marketplace_url)
    
    async def health_check(self) -> MarketplaceHealthResponse:
        """Check marketplace service health and connectivity"""
        
        try:
            # Test marketplace API connectivity
            api_accessible = False
            try:
                response = await self.http_client.get(
                    f"{self.config.marketplace_url}/health",
                    timeout=5.0
                )
                api_accessible = response.status_code == 200
            except Exception:
                api_accessible = False
            
            # Count installed plugins
            installed_count = len(self.installed_plugins)
            enabled_count = sum(
                1 for plugin in self.installed_plugins.values()
                if plugin.status == PluginStatus.INSTALLED
            )
            
            # Check disk space
            available_space = None
            try:
                stat = os.statvfs(str(self.plugins_dir))
                available_space = (stat.f_bavail * stat.f_frsize) // (1024 * 1024)  # MB
            except Exception:
                pass
            
            return MarketplaceHealthResponse(
                status="healthy" if api_accessible else "degraded",
                marketplace_url=self.config.marketplace_url,
                plugins_installed=installed_count,
                plugins_enabled=enabled_count,
                api_accessible=api_accessible,
                last_sync=datetime.utcnow(),
                plugins_directory=str(self.plugins_dir),
                available_disk_space_mb=available_space,
                gpg_verification_enabled=self.config.require_gpg_signatures,
                security_scanning_enabled=self.config.security_scan_required,
                auto_updates_enabled=self.config.auto_update_enabled,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Marketplace health check failed", error=str(e))
            return MarketplaceHealthResponse(
                status="unhealthy",
                marketplace_url=self.config.marketplace_url,
                plugins_installed=0,
                plugins_enabled=0,
                api_accessible=False,
                plugins_directory=str(self.plugins_dir),
                gpg_verification_enabled=self.config.require_gpg_signatures,
                security_scanning_enabled=self.config.security_scan_required,
                auto_updates_enabled=self.config.auto_update_enabled,
                last_check=datetime.utcnow()
            )
    
    async def search_plugins(self, request: PluginSearchRequest) -> PluginSearchResponse:
        """Search for plugins in the marketplace"""
        request_id = str(uuid4())[:8]
        start_time = datetime.utcnow()
        
        try:
            # Build search parameters
            params = {
                "page": request.page,
                "per_page": request.per_page,
                "sort_by": request.sort_by,
                "sort_order": request.sort_order
            }
            
            if request.query:
                params["q"] = request.query
            if request.category:
                params["category"] = request.category
            if request.tags:
                params["tags"] = ",".join(request.tags)
            if request.pricing_model:
                params["pricing"] = request.pricing_model
            if request.price_max is not None:
                params["price_max"] = float(request.price_max)
            if request.trusted_only:
                params["trusted_only"] = "true"
            if request.featured_only:
                params["featured_only"] = "true"
            
            # Make API request
            response = await self.http_client.get(
                f"{self.config.marketplace_url}/api/v1/plugins/search",
                params=params
            )
            response.raise_for_status()
            
            search_data = response.json()
            
            # Parse plugin information
            plugins = [
                PluginInfo(**plugin_data) 
                for plugin_data in search_data.get("plugins", [])
            ]
            
            search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info("Plugin search completed",
                       request_id=request_id,
                       query=request.query,
                       results_count=len(plugins),
                       search_time_ms=int(search_time))
            
            return PluginSearchResponse(
                plugins=plugins,
                total_count=search_data.get("total_count", len(plugins)),
                page=request.page,
                per_page=request.per_page,
                has_more=search_data.get("has_more", False),
                query=request.query,
                filters_applied={
                    "category": request.category,
                    "tags": request.tags,
                    "pricing_model": request.pricing_model,
                    "trusted_only": request.trusted_only,
                    "featured_only": request.featured_only
                },
                search_time_ms=int(search_time)
            )
            
        except httpx.HTTPError as e:
            logger.error("Marketplace API request failed",
                        request_id=request_id,
                        error=str(e))
            
            # Return empty results on API failure
            return PluginSearchResponse(
                plugins=[],
                total_count=0,
                page=request.page,
                per_page=request.per_page,
                has_more=False,
                query=request.query,
                filters_applied={},
                search_time_ms=0
            )
        except Exception as e:
            logger.error("Plugin search failed",
                        request_id=request_id,
                        error=str(e))
            raise
    
    async def get_plugin_info(self, plugin_id: str) -> Optional[PluginInfo]:
        """Get detailed plugin information"""
        
        # Check cache first
        if plugin_id in self.plugin_cache:
            cached_time, plugin_info = self.plugin_cache[plugin_id]
            cache_age = datetime.utcnow() - cached_time
            
            if cache_age < timedelta(hours=self.config.cache_duration_hours):
                logger.debug("Plugin info served from cache", plugin_id=plugin_id)
                return plugin_info
        
        try:
            response = await self.http_client.get(
                f"{self.config.marketplace_url}/api/v1/plugins/{plugin_id}"
            )
            response.raise_for_status()
            
            plugin_data = response.json()
            plugin_info = PluginInfo(**plugin_data)
            
            # Cache the result
            self.plugin_cache[plugin_id] = (datetime.utcnow(), plugin_info)
            
            logger.info("Plugin info retrieved", plugin_id=plugin_id)
            return plugin_info
            
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning("Plugin not found", plugin_id=plugin_id)
                return None
            logger.error("Failed to get plugin info",
                        plugin_id=plugin_id,
                        error=str(e))
            raise
        except Exception as e:
            logger.error("Plugin info retrieval failed",
                        plugin_id=plugin_id,
                        error=str(e))
            raise
    
    async def _verify_plugin_signature(self, plugin_path: Path, signature: str) -> bool:
        """Verify plugin GPG signature"""
        
        if not self.gpg_service or not self.config.require_gpg_signatures:
            logger.warning("GPG signature verification skipped")
            return True
        
        try:
            # Read plugin archive for verification
            plugin_data = plugin_path.read_bytes()
            
            # Verify signature
            verify_request = VerifyRequest(
                signed_data=signature,
                original_data=plugin_data.hex()
            )
            
            result = await self.gpg_service.verify(verify_request)
            
            if not result.success or not result.valid:
                logger.error("Plugin signature verification failed",
                           error=result.error,
                           plugin_path=str(plugin_path))
                return False
            
            logger.info("Plugin signature verified successfully",
                       signer=result.signer_fingerprints)
            return True
            
        except Exception as e:
            logger.error("Plugin signature verification error",
                        plugin_path=str(plugin_path),
                        error=str(e))
            return False
    
    async def _download_plugin(self, plugin_info: PluginInfo) -> Path:
        """Download plugin to temporary directory"""
        
        temp_file = self.temp_dir / f"{plugin_info.metadata.manifest.id}_{uuid4().hex[:8]}.zip"
        
        try:
            # Download plugin
            async with self.http_client.stream("GET", plugin_info.download_url) as response:
                response.raise_for_status()
                
                # Verify content length
                content_length = response.headers.get("content-length")
                if content_length:
                    size_mb = int(content_length) / (1024 * 1024)
                    if size_mb > self.config.max_plugin_size_mb:
                        raise ValueError(f"Plugin too large: {size_mb:.1f}MB > {self.config.max_plugin_size_mb}MB")
                
                # Download with progress tracking
                downloaded = 0
                hasher = hashlib.sha256()
                
                with open(temp_file, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        f.write(chunk)
                        hasher.update(chunk)
                        downloaded += len(chunk)
                        
                        # Size check during download
                        if downloaded > self.config.max_plugin_size_mb * 1024 * 1024:
                            raise ValueError("Plugin size exceeds maximum allowed")
            
            # Verify checksum
            actual_checksum = hasher.hexdigest()
            if actual_checksum != plugin_info.checksum_sha256:
                raise ValueError(f"Checksum mismatch: expected {plugin_info.checksum_sha256}, got {actual_checksum}")
            
            logger.info("Plugin downloaded successfully",
                       plugin_id=plugin_info.metadata.manifest.id,
                       size_bytes=downloaded,
                       temp_file=str(temp_file))
            
            return temp_file
            
        except Exception as e:
            # Cleanup on error
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    async def install_plugin(self, request: PluginInstallRequest) -> PluginInstallResponse:
        """Install a plugin from the marketplace"""
        request_id = str(uuid4())[:8]
        
        try:
            logger.info("Starting plugin installation",
                       request_id=request_id,
                       plugin_id=request.plugin_id,
                       version=request.version)
            
            # Get plugin information
            plugin_info = await self.get_plugin_info(request.plugin_id)
            if not plugin_info:
                return PluginInstallResponse(
                    success=False,
                    plugin_id=request.plugin_id,
                    error=f"Plugin '{request.plugin_id}' not found in marketplace",
                    request_id=request_id
                )
            
            # Version check
            manifest = plugin_info.metadata.manifest
            if request.version and manifest.version != request.version:
                return PluginInstallResponse(
                    success=False,
                    plugin_id=request.plugin_id,
                    error=f"Version {request.version} not available, current version is {manifest.version}",
                    request_id=request_id
                )
            
            # Check if already installed
            if request.plugin_id in self.installed_plugins:
                installed_version = self.installed_plugins[request.plugin_id].manifest.version
                if version.parse(manifest.version) <= version.parse(installed_version):
                    return PluginInstallResponse(
                        success=False,
                        plugin_id=request.plugin_id,
                        error=f"Plugin already installed with version {installed_version}",
                        request_id=request_id
                    )
            
            # Download plugin
            temp_plugin_file = await self._download_plugin(plugin_info)
            warnings = []
            
            try:
                # Verify GPG signature if required
                if plugin_info.metadata.manifest.gpg_signature:
                    if not await self._verify_plugin_signature(
                        temp_plugin_file, 
                        plugin_info.metadata.manifest.gpg_signature
                    ):
                        if self.config.require_gpg_signatures:
                            return PluginInstallResponse(
                                success=False,
                                plugin_id=request.plugin_id,
                                error="GPG signature verification failed",
                                request_id=request_id
                            )
                        else:
                            warnings.append("GPG signature verification failed but proceeding")
                
                # Extract plugin
                plugin_install_dir = self.plugins_dir / request.plugin_id
                if plugin_install_dir.exists():
                    shutil.rmtree(plugin_install_dir)
                
                plugin_install_dir.mkdir(parents=True)
                
                with zipfile.ZipFile(temp_plugin_file, 'r') as zip_file:
                    # Security check: prevent path traversal
                    for member in zip_file.namelist():
                        if member.startswith('/') or '..' in member:
                            raise ValueError(f"Unsafe path in plugin archive: {member}")
                    
                    zip_file.extractall(plugin_install_dir)
                
                # Validate manifest
                manifest_path = plugin_install_dir / "manifest.json"
                if not manifest_path.exists():
                    raise ValueError("Plugin manifest.json not found")
                
                manifest_data = json.loads(manifest_path.read_text())
                validated_manifest = PluginManifest(**manifest_data)
                
                # Security sandbox validation
                sandbox = PluginSandbox(
                    plugin_install_dir,
                    ["file_access", "network_access", "database_access"]  # Default allowed permissions
                )
                
                safe, sandbox_warnings = sandbox.validate_plugin_safety(validated_manifest)
                if not safe:
                    return PluginInstallResponse(
                        success=False,
                        plugin_id=request.plugin_id,
                        error="Plugin failed security validation",
                        warnings=sandbox_warnings,
                        request_id=request_id
                    )
                
                warnings.extend(sandbox_warnings)
                
                # Install dependencies if requested
                dependencies_installed = []
                if request.install_dependencies:
                    for dep in validated_manifest.dependencies:
                        if not dep.optional and dep.marketplace_id:
                            # Recursive dependency installation
                            dep_request = PluginInstallRequest(
                                plugin_id=dep.marketplace_id,
                                auto_enable=False,
                                install_dependencies=True,
                                accept_permissions=request.accept_permissions
                            )
                            dep_result = await self.install_plugin(dep_request)
                            if dep_result.success:
                                dependencies_installed.append(dep.name)
                            elif not dep.optional:
                                return PluginInstallResponse(
                                    success=False,
                                    plugin_id=request.plugin_id,
                                    error=f"Failed to install required dependency: {dep.name}",
                                    request_id=request_id
                                )
                
                # Update plugin registry
                plugin_metadata = PluginMetadata(
                    manifest=validated_manifest,
                    published_at=plugin_info.metadata.published_at,
                    updated_at=datetime.utcnow(),
                    status=PluginStatus.INSTALLED if request.auto_enable else PluginStatus.DISABLED
                )
                
                self.installed_plugins[request.plugin_id] = plugin_metadata
                
                logger.info("Plugin installation completed successfully",
                           request_id=request_id,
                           plugin_id=request.plugin_id,
                           version=validated_manifest.version,
                           installation_path=str(plugin_install_dir))
                
                return PluginInstallResponse(
                    success=True,
                    plugin_id=request.plugin_id,
                    installed_version=validated_manifest.version,
                    installation_path=str(plugin_install_dir),
                    dependencies_installed=dependencies_installed,
                    permissions_granted=[p.name for p in validated_manifest.permissions if request.accept_permissions],
                    enabled=request.auto_enable,
                    restart_required=True,  # Most plugins require restart
                    warnings=warnings,
                    request_id=request_id
                )
                
            finally:
                # Cleanup temporary file
                if temp_plugin_file.exists():
                    temp_plugin_file.unlink()
                    
        except Exception as e:
            logger.error("Plugin installation failed",
                        request_id=request_id,
                        plugin_id=request.plugin_id,
                        error=str(e))
            
            return PluginInstallResponse(
                success=False,
                plugin_id=request.plugin_id,
                error=f"Installation failed: {str(e)}",
                request_id=request_id
            )
    
    async def uninstall_plugin(self, plugin_id: str) -> Dict[str, any]:
        """Uninstall a plugin"""
        request_id = str(uuid4())[:8]
        
        try:
            if plugin_id not in self.installed_plugins:
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_id}' is not installed",
                    "request_id": request_id
                }
            
            # Remove plugin files
            plugin_dir = self.plugins_dir / plugin_id
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            
            # Remove from registry
            del self.installed_plugins[plugin_id]
            
            logger.info("Plugin uninstalled successfully",
                       request_id=request_id,
                       plugin_id=plugin_id)
            
            return {
                "success": True,
                "plugin_id": plugin_id,
                "request_id": request_id
            }
            
        except Exception as e:
            logger.error("Plugin uninstallation failed",
                        request_id=request_id,
                        plugin_id=plugin_id,
                        error=str(e))
            
            return {
                "success": False,
                "plugin_id": plugin_id,
                "error": str(e),
                "request_id": request_id
            }
    
    async def list_installed_plugins(self) -> List[PluginMetadata]:
        """List all installed plugins"""
        return list(self.installed_plugins.values())
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable an installed plugin"""
        if plugin_id in self.installed_plugins:
            self.installed_plugins[plugin_id].status = PluginStatus.INSTALLED
            logger.info("Plugin enabled", plugin_id=plugin_id)
            return True
        return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable an installed plugin"""
        if plugin_id in self.installed_plugins:
            self.installed_plugins[plugin_id].status = PluginStatus.DISABLED
            logger.info("Plugin disabled", plugin_id=plugin_id)
            return True
        return False
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()
        logger.info("Marketplace service cleanup completed")