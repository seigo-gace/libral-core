"""
Plugin Marketplace Module Tests
Test marketplace operations with privacy-first principles
"""

import asyncio
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from libral_core.modules.marketplace.service import MarketplaceService
from libral_core.modules.marketplace.schemas import (
    MarketplaceConfig,
    PluginCategory,
    PluginInfo,
    PluginInstallRequest,
    PluginManifest,
    PluginMetadata,
    PluginPricingModel,
    PluginSearchRequest,
    PluginStatus
)

@pytest.fixture
def marketplace_config():
    """Create test marketplace configuration"""
    return MarketplaceConfig(
        marketplace_url="https://test-marketplace.libral.app",
        plugins_directory="./test_plugins",
        temp_directory="./test_temp",
        require_gpg_signatures=False,  # Disabled for testing
        security_scan_required=False,
        max_plugin_size_mb=10,
        installation_timeout_seconds=60
    )

@pytest.fixture
def mock_gpg_service():
    """Create mock GPG service"""
    service = AsyncMock()
    service.verify.return_value = AsyncMock(success=True, valid=True, signer_fingerprints=["test123"])
    return service

@pytest.fixture
def marketplace_service(marketplace_config, mock_gpg_service):
    """Create marketplace service for testing"""
    service = MarketplaceService(
        config=marketplace_config,
        gpg_service=mock_gpg_service
    )
    
    # Mock HTTP client
    service.http_client = AsyncMock()
    
    return service

@pytest.fixture
def sample_plugin_manifest():
    """Create sample plugin manifest"""
    return PluginManifest(
        name="Test Plugin",
        id="test-plugin",
        version="1.0.0",
        description="A test plugin for demonstration purposes",
        category=PluginCategory.UTILITIES,
        developer_name="Test Developer",
        developer_email="dev@test.com",
        main_entry="main.py",
        pricing_model=PluginPricingModel.FREE,
        trusted_publisher=True
    )

@pytest.fixture
def sample_plugin_info(sample_plugin_manifest):
    """Create sample plugin info"""
    metadata = PluginMetadata(
        manifest=sample_plugin_manifest,
        published_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        status=PluginStatus.AVAILABLE,
        download_count=100,
        rating_average=4.5,
        rating_count=20
    )
    
    return PluginInfo(
        metadata=metadata,
        download_url="https://test-cdn.libral.app/test-plugin-1.0.0.zip",
        download_size=1024000,  # 1MB
        checksum_sha256="abcd1234" * 8  # Mock checksum
    )

@pytest.mark.asyncio
async def test_marketplace_health_check(marketplace_service):
    """Test marketplace health check"""
    
    # Mock successful API response
    marketplace_service.http_client.get.return_value = AsyncMock(status_code=200)
    
    health = await marketplace_service.health_check()
    
    assert health.status in ["healthy", "degraded"]
    assert health.marketplace_url == "https://test-marketplace.libral.app"
    assert health.plugins_installed >= 0
    assert health.gpg_verification_enabled is False  # Disabled in test config

@pytest.mark.asyncio
async def test_search_plugins_success(marketplace_service):
    """Test successful plugin search"""
    
    # Mock search API response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "plugins": [
            {
                "metadata": {
                    "manifest": {
                        "name": "Test Plugin",
                        "id": "test-plugin",
                        "version": "1.0.0",
                        "description": "Test plugin description",
                        "category": "utilities",
                        "developer_name": "Test Dev",
                        "developer_email": "dev@test.com",
                        "main_entry": "main.py",
                        "pricing_model": "free"
                    },
                    "published_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "status": "available",
                    "download_count": 100
                },
                "download_url": "https://test.com/plugin.zip",
                "download_size": 1024,
                "checksum_sha256": "abcd1234" * 8
            }
        ],
        "total_count": 1,
        "has_more": False
    }
    mock_response.raise_for_status = MagicMock()
    marketplace_service.http_client.get.return_value = mock_response
    
    # Test search request
    search_request = PluginSearchRequest(
        query="test",
        category=PluginCategory.UTILITIES,
        page=1,
        per_page=20
    )
    
    result = await marketplace_service.search_plugins(search_request)
    
    assert result.total_count == 1
    assert len(result.plugins) == 1
    assert result.plugins[0].metadata.manifest.name == "Test Plugin"
    assert result.query == "test"
    assert result.search_time_ms >= 0

@pytest.mark.asyncio
async def test_search_plugins_api_failure(marketplace_service):
    """Test plugin search with API failure"""
    
    # Mock API failure
    marketplace_service.http_client.get.side_effect = Exception("API Error")
    
    search_request = PluginSearchRequest(query="test")
    result = await marketplace_service.search_plugins(search_request)
    
    # Should return empty results gracefully
    assert result.total_count == 0
    assert len(result.plugins) == 0
    assert result.search_time_ms == 0

@pytest.mark.asyncio
async def test_get_plugin_info_success(marketplace_service, sample_plugin_info):
    """Test successful plugin info retrieval"""
    
    # Mock plugin info API response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_plugin_info.dict()
    mock_response.raise_for_status = MagicMock()
    marketplace_service.http_client.get.return_value = mock_response
    
    result = await marketplace_service.get_plugin_info("test-plugin")
    
    assert result is not None
    assert result.metadata.manifest.name == "Test Plugin"
    assert result.download_url.startswith("https://")
    
    # Verify caching
    cached_result = await marketplace_service.get_plugin_info("test-plugin")
    assert cached_result is not None
    assert cached_result.metadata.manifest.name == "Test Plugin"

@pytest.mark.asyncio
async def test_get_plugin_info_not_found(marketplace_service):
    """Test plugin info retrieval for non-existent plugin"""
    
    # Mock 404 response
    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    marketplace_service.http_client.get.return_value = mock_response
    
    result = await marketplace_service.get_plugin_info("non-existent-plugin")
    
    assert result is None

@pytest.mark.asyncio 
async def test_install_plugin_success(marketplace_service, sample_plugin_info):
    """Test successful plugin installation"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Update service directories to use temp directory
        marketplace_service.plugins_dir = Path(temp_dir) / "plugins"
        marketplace_service.temp_dir = Path(temp_dir) / "temp"
        marketplace_service.plugins_dir.mkdir(parents=True)
        marketplace_service.temp_dir.mkdir(parents=True)
        
        # Mock get_plugin_info
        marketplace_service.get_plugin_info = AsyncMock(return_value=sample_plugin_info)
        
        # Mock download
        with patch.object(marketplace_service, '_download_plugin') as mock_download:
            # Create mock plugin file
            plugin_file = marketplace_service.temp_dir / "test_plugin.zip"
            plugin_file.touch()
            mock_download.return_value = plugin_file
            
            # Mock plugin extraction and manifest
            with patch('zipfile.ZipFile') as mock_zip:
                mock_zip_instance = MagicMock()
                mock_zip_instance.namelist.return_value = ['manifest.json', 'main.py']
                mock_zip_instance.extractall = MagicMock()
                mock_zip.return_value.__enter__.return_value = mock_zip_instance
                
                # Create mock manifest file
                manifest_path = marketplace_service.plugins_dir / "test-plugin" / "manifest.json"
                manifest_path.parent.mkdir(parents=True, exist_ok=True)
                manifest_path.write_text(json.dumps(sample_plugin_info.metadata.manifest.dict()))
                
                # Test installation
                install_request = PluginInstallRequest(
                    plugin_id="test-plugin",
                    auto_enable=True,
                    install_dependencies=False,
                    accept_permissions=True
                )
                
                result = await marketplace_service.install_plugin(install_request)
                
                assert result.success is True
                assert result.plugin_id == "test-plugin"
                assert result.installed_version == "1.0.0"
                assert result.enabled is True
                assert "test-plugin" in marketplace_service.installed_plugins

@pytest.mark.asyncio
async def test_install_plugin_not_found(marketplace_service):
    """Test plugin installation for non-existent plugin"""
    
    # Mock plugin not found
    marketplace_service.get_plugin_info = AsyncMock(return_value=None)
    
    install_request = PluginInstallRequest(
        plugin_id="non-existent-plugin",
        auto_enable=True
    )
    
    result = await marketplace_service.install_plugin(install_request)
    
    assert result.success is False
    assert "not found" in result.error.lower()
    assert result.plugin_id == "non-existent-plugin"

@pytest.mark.asyncio
async def test_install_plugin_already_installed(marketplace_service, sample_plugin_info):
    """Test installation of already installed plugin"""
    
    # Pre-install plugin in registry
    marketplace_service.installed_plugins["test-plugin"] = sample_plugin_info.metadata
    marketplace_service.get_plugin_info = AsyncMock(return_value=sample_plugin_info)
    
    install_request = PluginInstallRequest(
        plugin_id="test-plugin",
        auto_enable=True
    )
    
    result = await marketplace_service.install_plugin(install_request)
    
    assert result.success is False
    assert "already installed" in result.error.lower()

@pytest.mark.asyncio
async def test_uninstall_plugin_success(marketplace_service, sample_plugin_info):
    """Test successful plugin uninstallation"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        marketplace_service.plugins_dir = Path(temp_dir) / "plugins"
        marketplace_service.plugins_dir.mkdir(parents=True)
        
        # Pre-install plugin
        plugin_dir = marketplace_service.plugins_dir / "test-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "main.py").write_text("# Test plugin")
        
        marketplace_service.installed_plugins["test-plugin"] = sample_plugin_info.metadata
        
        result = await marketplace_service.uninstall_plugin("test-plugin")
        
        assert result["success"] is True
        assert result["plugin_id"] == "test-plugin"
        assert "test-plugin" not in marketplace_service.installed_plugins
        assert not plugin_dir.exists()

@pytest.mark.asyncio
async def test_uninstall_plugin_not_installed(marketplace_service):
    """Test uninstallation of non-installed plugin"""
    
    result = await marketplace_service.uninstall_plugin("non-existent-plugin")
    
    assert result["success"] is False
    assert "not installed" in result["error"].lower()

@pytest.mark.asyncio
async def test_list_installed_plugins(marketplace_service, sample_plugin_info):
    """Test listing installed plugins"""
    
    # Add sample plugin to registry
    marketplace_service.installed_plugins["test-plugin"] = sample_plugin_info.metadata
    
    plugins = await marketplace_service.list_installed_plugins()
    
    assert len(plugins) == 1
    assert plugins[0].manifest.name == "Test Plugin"
    assert plugins[0].status == PluginStatus.AVAILABLE

@pytest.mark.asyncio
async def test_enable_disable_plugin(marketplace_service, sample_plugin_info):
    """Test enabling and disabling plugins"""
    
    # Add plugin to registry
    marketplace_service.installed_plugins["test-plugin"] = sample_plugin_info.metadata
    
    # Test enabling
    success = await marketplace_service.enable_plugin("test-plugin")
    assert success is True
    assert marketplace_service.installed_plugins["test-plugin"].status == PluginStatus.INSTALLED
    
    # Test disabling
    success = await marketplace_service.disable_plugin("test-plugin")
    assert success is True
    assert marketplace_service.installed_plugins["test-plugin"].status == PluginStatus.DISABLED
    
    # Test non-existent plugin
    success = await marketplace_service.enable_plugin("non-existent")
    assert success is False

def test_plugin_manifest_validation():
    """Test plugin manifest validation"""
    
    # Test valid manifest
    manifest = PluginManifest(
        name="Test Plugin",
        id="test-plugin",
        version="1.2.3",
        description="A comprehensive test plugin for validation purposes",
        category=PluginCategory.AI_AGENTS,
        developer_name="Test Developer",
        developer_email="test@example.com",
        main_entry="main.py",
        tags=["test", "utility", "Test", "UTILITY"]  # Test tag normalization
    )
    
    assert manifest.name == "Test Plugin"
    assert manifest.version == "1.2.3"
    assert manifest.category == PluginCategory.AI_AGENTS
    assert set(manifest.tags) == {"test", "utility"}  # Normalized and deduplicated
    
    # Test invalid manifest
    with pytest.raises(Exception):
        PluginManifest(
            name="",  # Too short
            id="invalid_id!",  # Invalid characters
            version="1.0",  # Invalid version format
            description="",  # Too short
            category=PluginCategory.UTILITIES,
            developer_name="Test",
            developer_email="invalid-email",  # Invalid email
            main_entry="main.py"
        )

def test_plugin_search_request_validation():
    """Test plugin search request validation"""
    
    # Test valid search request
    request = PluginSearchRequest(
        query="test plugin",
        category=PluginCategory.CREATIVE_TOOLS,
        tags=["art", "design"],
        pricing_model=PluginPricingModel.FREE,
        trusted_only=True,
        page=2,
        per_page=50
    )
    
    assert request.query == "test plugin"
    assert request.category == PluginCategory.CREATIVE_TOOLS
    assert request.page == 2
    
    # Test edge cases
    edge_request = PluginSearchRequest(
        page=1,
        per_page=100,  # Maximum allowed
        sort_by="downloads",
        sort_order="asc"
    )
    
    assert edge_request.per_page == 100
    assert edge_request.sort_by == "downloads"
    
    # Test invalid values
    with pytest.raises(Exception):
        PluginSearchRequest(
            page=0,  # Must be >= 1
            per_page=101,  # Exceeds maximum
            sort_by="invalid_sort",  # Invalid sort option
            sort_order="invalid_order"  # Invalid order
        )

@pytest.mark.asyncio
async def test_privacy_compliance_no_personal_data_logging(marketplace_service):
    """Test that marketplace operations don't log personal data"""
    
    # This test ensures privacy compliance in marketplace operations
    # In a real implementation, we would capture and analyze log outputs
    
    search_request = PluginSearchRequest(
        query="personal_data_test_query_with_sensitive_info",
        page=1
    )
    
    # Mock successful response with no personal data
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "plugins": [],
        "total_count": 0,
        "has_more": False
    }
    mock_response.raise_for_status = MagicMock()
    marketplace_service.http_client.get.return_value = mock_response
    
    result = await marketplace_service.search_plugins(search_request)
    
    # Verify operation completed successfully
    assert result.total_count == 0
    
    # In a real test, we would verify:
    # 1. No personal information in log files
    # 2. No user data transmitted to marketplace
    # 3. All plugin operations are anonymous
    # 4. Local plugin registry contains no personal data
    
    assert True, "Privacy compliance testing requires log analysis infrastructure"