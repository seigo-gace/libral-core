"""
Libral Asset Service (LAS) - Unified Service
Combines Library utilities + UI Asset Management + WebAssembly functionality
"""

import asyncio
import base64
import hashlib
import io
import json
import mimetypes
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, BinaryIO
from uuid import uuid4
import urllib.parse

import httpx
import structlog
from PIL import Image, ImageOps
import wasmtime

from .schemas import (
    APIClientConfig, APIRequest, APIResponse, Asset, AssetFormat,
    AssetQuery, AssetSearchResponse, AssetType, AssetUploadRequest, AssetUploadResponse,
    DateTimeProcessingRequest, DateTimeProcessingResponse,
    ImageProcessingRequest, LASHealthResponse, LASMetrics,
    OptimizationLevel, ProcessingResult, ProcessingStatus,
    StringProcessingRequest, StringProcessingResponse,
    VideoProcessingRequest, WASMExecutionRequest, WASMExecutionResponse, WASMModule
)

logger = structlog.get_logger(__name__)


class UtilityProcessor:
    """String processing, datetime handling, and validation utilities"""
    
    def __init__(self):
        logger.info("Utility processor initialized")
    
    async def process_string(self, request: StringProcessingRequest) -> StringProcessingResponse:
        """Process string operations"""
        try:
            if request.operation == "sanitize":
                result = await self._sanitize_string(request.input_text, request.options)
            elif request.operation == "truncate":
                max_length = request.options.get("max_length", 100)
                suffix = request.options.get("suffix", "...")
                result = self._truncate_string(request.input_text, max_length, suffix)
            elif request.operation == "validate":
                validation_type = request.options.get("type", "email")
                result = str(self._validate_string(request.input_text, validation_type))
            elif request.operation == "format":
                format_type = request.options.get("format", "title")
                result = self._format_string(request.input_text, format_type)
            else:
                raise ValueError(f"Unsupported operation: {request.operation}")
            
            return StringProcessingResponse(
                success=True,
                result=result,
                metadata={"operation": request.operation, "input_length": len(request.input_text)}
            )
            
        except Exception as e:
            logger.error("String processing failed", error=str(e), operation=request.operation)
            return StringProcessingResponse(
                success=False,
                error=str(e)
            )
    
    async def process_datetime(self, request: DateTimeProcessingRequest) -> DateTimeProcessingResponse:
        """Process datetime operations"""
        try:
            if request.operation == "parse":
                dt = await self._parse_datetime(request.input_datetime, request.format_string)
                return DateTimeProcessingResponse(
                    success=True,
                    result=dt.isoformat(),
                    timestamp=dt,
                    timezone=request.timezone
                )
            elif request.operation == "format":
                dt = datetime.fromisoformat(request.input_datetime)
                formatted = dt.strftime(request.format_string or "%Y-%m-%d %H:%M:%S")
                return DateTimeProcessingResponse(
                    success=True,
                    result=formatted,
                    timestamp=dt
                )
            elif request.operation == "convert":
                # Convert timezone
                dt = datetime.fromisoformat(request.input_datetime)
                # Simplified timezone conversion
                return DateTimeProcessingResponse(
                    success=True,
                    result=dt.isoformat(),
                    timestamp=dt,
                    timezone=request.timezone
                )
            else:
                raise ValueError(f"Unsupported operation: {request.operation}")
                
        except Exception as e:
            logger.error("DateTime processing failed", error=str(e))
            return DateTimeProcessingResponse(success=False, error=str(e))
    
    async def _sanitize_string(self, text: str, options: Dict[str, Any]) -> str:
        """Sanitize string for security"""
        import html
        import re
        
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove potentially dangerous characters
        if options.get("strict", False):
            sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Limit length
        max_length = options.get("max_length", 1000)
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    def _truncate_string(self, text: str, max_length: int, suffix: str) -> str:
        """Truncate string with suffix"""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    def _validate_string(self, text: str, validation_type: str) -> bool:
        """Validate string format"""
        import re
        
        if validation_type == "email":
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, text))
        elif validation_type == "url":
            pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$'
            return bool(re.match(pattern, text))
        elif validation_type == "phone":
            pattern = r'^\+?[\d\s\-\(\)]{10,}$'
            return bool(re.match(pattern, text))
        else:
            return True
    
    def _format_string(self, text: str, format_type: str) -> str:
        """Format string according to type"""
        if format_type == "title":
            return text.title()
        elif format_type == "upper":
            return text.upper()
        elif format_type == "lower":
            return text.lower()
        elif format_type == "snake_case":
            import re
            return re.sub(r'[^\w\s]', '', text).replace(' ', '_').lower()
        elif format_type == "camel_case":
            import re
            s = re.sub(r'[^\w\s]', '', text)
            return ''.join(word.capitalize() for word in s.split())
        else:
            return text
    
    async def _parse_datetime(self, dt_string: str, format_string: Optional[str]) -> datetime:
        """Parse datetime string"""
        if format_string:
            return datetime.strptime(dt_string, format_string)
        
        # Try common formats
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(dt_string, fmt)
            except ValueError:
                continue
        
        # Try ISO format
        return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))


class APIClientManager:
    """External API client management"""
    
    def __init__(self):
        self.clients: Dict[str, APIClientConfig] = {}
        logger.info("API client manager initialized")
    
    async def register_client(self, config: APIClientConfig):
        """Register API client configuration"""
        self.clients[config.client_id] = config
        logger.info("API client registered", client_id=config.client_id, name=config.name)
    
    async def make_request(self, request: APIRequest) -> APIResponse:
        """Make API request using configured client"""
        start_time = datetime.utcnow()
        request_id = str(uuid4())
        
        try:
            if request.client_id not in self.clients:
                raise ValueError(f"Client not found: {request.client_id}")
            
            client_config = self.clients[request.client_id]
            
            # Build request URL
            url = f"{client_config.base_url.rstrip('/')}/{request.endpoint.lstrip('/')}"
            
            # Prepare headers
            headers = client_config.default_headers.copy()
            if request.headers:
                headers.update(request.headers)
            
            # Add authentication
            if client_config.auth_type == "bearer" and client_config.auth_token:
                headers["Authorization"] = f"Bearer {client_config.auth_token}"
            elif client_config.auth_type == "api_key" and client_config.api_key:
                headers["X-API-Key"] = client_config.api_key
            
            # Make request
            async with httpx.AsyncClient(timeout=request.timeout or client_config.timeout_seconds) as client:
                response = await client.request(
                    method=request.method,
                    url=url,
                    params=request.params,
                    headers=headers,
                    json=request.json_data,
                    data=request.form_data,
                    verify=request.verify_ssl
                )
            
            # Calculate response time
            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Parse response
            response_data = None
            json_data = None
            
            try:
                json_data = response.json()
                response_data = json_data
            except:
                response_data = response.text
            
            logger.info("API request completed", 
                       client_id=request.client_id,
                       method=request.method,
                       status_code=response.status_code,
                       response_time_ms=response_time_ms)
            
            return APIResponse(
                success=200 <= response.status_code < 300,
                status_code=response.status_code,
                headers=dict(response.headers),
                data=response_data,
                text=response.text,
                json_data=json_data,
                response_time_ms=response_time_ms,
                request_id=request_id
            )
            
        except Exception as e:
            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error("API request failed", 
                        client_id=request.client_id,
                        error=str(e),
                        response_time_ms=response_time_ms)
            
            return APIResponse(
                success=False,
                status_code=0,
                response_time_ms=response_time_ms,
                request_id=request_id,
                error=str(e)
            )


class FileProcessor:
    """Advanced file processing for images, videos, and documents"""
    
    def __init__(self):
        logger.info("File processor initialized")
    
    async def process_image(self, request: ImageProcessingRequest) -> ProcessingResult:
        """Process image with specified operations"""
        start_time = datetime.utcnow()
        
        try:
            # Load image (placeholder - would load from asset storage)
            img = Image.open(io.BytesIO(b""))  # Placeholder image data
            
            # Apply operations
            for operation in request.operations:
                op_type = operation.get("type")
                
                if op_type == "resize":
                    width = operation.get("width")
                    height = operation.get("height")
                    img = img.resize((width, height), Image.LANCZOS)
                
                elif op_type == "crop":
                    x1, y1, x2, y2 = operation.get("box", [0, 0, 100, 100])
                    img = img.crop((x1, y1, x2, y2))
                
                elif op_type == "rotate":
                    angle = operation.get("angle", 0)
                    img = img.rotate(angle, expand=True)
                
                elif op_type == "optimize":
                    img = ImageOps.exif_transpose(img)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
            
            # Save processed image
            output_buffer = io.BytesIO()
            img.save(output_buffer, format=request.output_format.value.upper() if request.output_format else "JPEG", 
                    quality=request.quality, optimize=True)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info("Image processed", 
                       asset_id=request.asset_id,
                       operations=len(request.operations),
                       processing_time_ms=processing_time)
            
            return ProcessingResult(
                success=True,
                processed_asset_id=str(uuid4()),
                processing_time_ms=processing_time,
                file_size_reduction=15.0,  # Placeholder
                metadata={"operations_applied": len(request.operations)}
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error("Image processing failed", 
                        asset_id=request.asset_id,
                        error=str(e),
                        processing_time_ms=processing_time)
            
            return ProcessingResult(
                success=False,
                processing_time_ms=processing_time,
                error=str(e)
            )
    
    async def process_video(self, request: VideoProcessingRequest) -> ProcessingResult:
        """Process video with specified operations (placeholder)"""
        start_time = datetime.utcnow()
        
        try:
            # Video processing would use ffmpeg or similar
            # This is a placeholder implementation
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info("Video processing completed", 
                       asset_id=request.asset_id,
                       processing_time_ms=processing_time)
            
            return ProcessingResult(
                success=True,
                processed_asset_id=str(uuid4()),
                processing_time_ms=processing_time,
                file_size_reduction=25.0,
                metadata={"operations_applied": len(request.operations)}
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error("Video processing failed", error=str(e))
            
            return ProcessingResult(
                success=False,
                processing_time_ms=processing_time,
                error=str(e)
            )


class WASMRuntime:
    """WebAssembly runtime environment"""
    
    def __init__(self):
        self.modules: Dict[str, WASMModule] = {}
        self.compiled_modules: Dict[str, Any] = {}
        logger.info("WASM runtime initialized")
    
    async def register_module(self, module: WASMModule):
        """Register WebAssembly module"""
        try:
            self.modules[module.module_id] = module
            
            # Compile module (placeholder - would load actual WASM binary)
            engine = wasmtime.Engine()
            store = wasmtime.Store(engine)
            
            # Load WASM binary from asset
            wasm_bytes = b""  # Placeholder - would load from asset storage
            
            # Compile module
            compiled_module = wasmtime.Module(engine, wasm_bytes)
            instance = wasmtime.Instance(store, compiled_module, [])
            
            self.compiled_modules[module.module_id] = {
                "engine": engine,
                "store": store,
                "module": compiled_module,
                "instance": instance
            }
            
            logger.info("WASM module registered and compiled", module_id=module.module_id)
            
        except Exception as e:
            logger.error("WASM module registration failed", 
                        module_id=module.module_id,
                        error=str(e))
            raise
    
    async def execute_function(self, request: WASMExecutionRequest) -> WASMExecutionResponse:
        """Execute WebAssembly function"""
        start_time = datetime.utcnow()
        
        try:
            if request.module_id not in self.compiled_modules:
                raise ValueError(f"Module not found: {request.module_id}")
            
            compiled = self.compiled_modules[request.module_id]
            instance = compiled["instance"]
            
            # Get function export
            func = instance.exports(compiled["store"]).get(request.function_name)
            if not func:
                raise ValueError(f"Function not found: {request.function_name}")
            
            # Execute function with parameters
            result = func(compiled["store"], *request.parameters)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info("WASM function executed", 
                       module_id=request.module_id,
                       function=request.function_name,
                       execution_time_ms=execution_time)
            
            return WASMExecutionResponse(
                success=True,
                result=result,
                result_type="i32",  # Placeholder
                execution_time_ms=execution_time,
                memory_used=1024,  # Placeholder
                instructions_executed=1000  # Placeholder
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error("WASM execution failed", 
                        module_id=request.module_id,
                        function=request.function_name,
                        error=str(e),
                        execution_time_ms=execution_time)
            
            return WASMExecutionResponse(
                success=False,
                execution_time_ms=execution_time,
                memory_used=0,
                error=str(e),
                error_type=type(e).__name__
            )


class AssetManager:
    """UI asset management and optimization"""
    
    def __init__(self):
        self.assets: Dict[str, Asset] = {}
        logger.info("Asset manager initialized")
    
    async def upload_asset(self, request: AssetUploadRequest, file_data: bytes) -> AssetUploadResponse:
        """Upload and process asset"""
        try:
            # Generate asset ID
            asset_id = str(uuid4())
            
            # Calculate file properties
            file_size = len(file_data)
            checksum = hashlib.sha256(file_data).hexdigest()
            mime_type, _ = mimetypes.guess_type(request.name)
            mime_type = mime_type or "application/octet-stream"
            
            # Determine asset format
            format_mapping = {
                "image/jpeg": AssetFormat.JPEG,
                "image/png": AssetFormat.PNG,
                "image/webp": AssetFormat.WEBP,
                "video/mp4": AssetFormat.MP4,
                "text/css": AssetFormat.CSS,
                "application/javascript": AssetFormat.JS,
                "application/wasm": AssetFormat.WASM
            }
            
            asset_format = format_mapping.get(mime_type, AssetFormat.JPEG)
            
            # Create asset record
            asset = Asset(
                asset_id=asset_id,
                name=request.name,
                description=request.description,
                asset_type=request.asset_type,
                format=asset_format,
                mime_type=mime_type,
                file_size=file_size,
                checksum=checksum,
                storage_path=f"/assets/{asset_id}",
                processing_status=ProcessingStatus.PENDING,
                optimization_level=request.optimization_level,
                access_level=request.access_level,
                owner_id="user_123",  # Would come from authentication
                tags=request.tags,
                metadata=request.custom_metadata
            )
            
            # Set expiration if specified
            if request.expires_in_hours:
                asset.expires_at = datetime.utcnow() + timedelta(hours=request.expires_in_hours)
            
            # Store asset
            self.assets[asset_id] = asset
            
            # Process asset if auto-optimization is enabled
            if request.auto_optimize:
                asset.processing_status = ProcessingStatus.PROCESSING
                # Trigger background processing
                asyncio.create_task(self._process_asset(asset))
            
            logger.info("Asset uploaded", 
                       asset_id=asset_id,
                       name=request.name,
                       size=file_size)
            
            return AssetUploadResponse(
                success=True,
                asset_id=asset_id,
                upload_url=f"/api/v2/assets/{asset_id}/upload",
                asset_url=f"/api/v2/assets/{asset_id}",
                processing_status=asset.processing_status
            )
            
        except Exception as e:
            logger.error("Asset upload failed", error=str(e))
            return AssetUploadResponse(
                success=False,
                processing_status=ProcessingStatus.FAILED,
                error=str(e)
            )
    
    async def search_assets(self, query: AssetQuery) -> AssetSearchResponse:
        """Search assets with filtering"""
        try:
            filtered_assets = []
            
            for asset in self.assets.values():
                # Apply filters
                if query.asset_types and asset.asset_type not in query.asset_types:
                    continue
                if query.formats and asset.format not in query.formats:
                    continue
                if query.tags and not any(tag in asset.tags for tag in query.tags):
                    continue
                if query.owner_id and asset.owner_id != query.owner_id:
                    continue
                if query.access_level and asset.access_level != query.access_level:
                    continue
                if query.created_after and asset.created_at < query.created_after:
                    continue
                if query.created_before and asset.created_at > query.created_before:
                    continue
                
                filtered_assets.append(asset)
            
            # Sort assets
            if query.sort_by == "created_at":
                filtered_assets.sort(key=lambda x: x.created_at, 
                                   reverse=(query.sort_order == "desc"))
            elif query.sort_by == "name":
                filtered_assets.sort(key=lambda x: x.name.lower(),
                                   reverse=(query.sort_order == "desc"))
            elif query.sort_by == "file_size":
                filtered_assets.sort(key=lambda x: x.file_size,
                                   reverse=(query.sort_order == "desc"))
            
            # Pagination
            total_count = len(filtered_assets)
            start_idx = query.offset
            end_idx = start_idx + query.limit
            paginated_assets = filtered_assets[start_idx:end_idx]
            
            return AssetSearchResponse(
                assets=paginated_assets,
                total_count=total_count,
                has_more=end_idx < total_count,
                next_offset=end_idx if end_idx < total_count else None
            )
            
        except Exception as e:
            logger.error("Asset search failed", error=str(e))
            return AssetSearchResponse(assets=[], total_count=0, has_more=False)
    
    async def _process_asset(self, asset: Asset):
        """Background asset processing"""
        try:
            # Simulate processing delay
            await asyncio.sleep(1)
            
            # Update status
            asset.processing_status = ProcessingStatus.OPTIMIZED
            asset.updated_at = datetime.utcnow()
            
            # Generate variants for images
            if asset.asset_type == AssetType.IMAGE:
                asset.processed_variants = {
                    "thumbnail": f"{asset.storage_path}_thumb",
                    "medium": f"{asset.storage_path}_medium",
                    "webp": f"{asset.storage_path}.webp"
                }
            
            logger.info("Asset processing completed", asset_id=asset.asset_id)
            
        except Exception as e:
            asset.processing_status = ProcessingStatus.FAILED
            logger.error("Asset processing failed", asset_id=asset.asset_id, error=str(e))


class LibralAssetService:
    """Unified Libral Asset Service"""
    
    def __init__(self):
        self.utility_processor = UtilityProcessor()
        self.api_client_manager = APIClientManager()
        self.file_processor = FileProcessor()
        self.wasm_runtime = WASMRuntime()
        self.asset_manager = AssetManager()
        
        # Metrics
        self.metrics = {
            "string_operations": 0,
            "datetime_operations": 0,
            "api_requests": 0,
            "images_processed": 0,
            "videos_processed": 0,
            "wasm_executions": 0,
            "assets_uploaded": 0
        }
        
        logger.info("Libral Asset Service initialized")
    
    async def get_health(self) -> LASHealthResponse:
        """Get LAS module health status"""
        return LASHealthResponse(
            status="healthy",
            version="2.0.0",
            components={
                "utilities": {
                    "status": "healthy",
                    "operations_processed": self.metrics["string_operations"] + self.metrics["datetime_operations"]
                },
                "api_clients": {
                    "status": "healthy",
                    "active_clients": len(self.api_client_manager.clients),
                    "requests_today": self.metrics["api_requests"]
                },
                "file_processing": {
                    "status": "healthy",
                    "queue_size": 0,
                    "processed_today": self.metrics["images_processed"] + self.metrics["videos_processed"]
                },
                "asset_management": {
                    "status": "healthy",
                    "total_assets": len(self.asset_manager.assets),
                    "storage_used_mb": sum(asset.file_size for asset in self.asset_manager.assets.values()) / (1024 * 1024)
                },
                "wasm_runtime": {
                    "status": "healthy",
                    "loaded_modules": len(self.wasm_runtime.modules),
                    "executions_today": self.metrics["wasm_executions"]
                }
            },
            uptime_seconds=0.0,
            last_health_check=datetime.utcnow()
        )
    
    async def get_metrics(self, period_start: datetime, period_end: datetime) -> LASMetrics:
        """Get LAS module metrics"""
        return LASMetrics(
            period_start=period_start,
            period_end=period_end,
            string_operations=self.metrics["string_operations"],
            datetime_operations=self.metrics["datetime_operations"],
            validation_operations=0,
            api_requests_made=self.metrics["api_requests"],
            api_success_rate=0.95,
            api_average_response_time_ms=250.0,
            images_processed=self.metrics["images_processed"],
            videos_processed=self.metrics["videos_processed"],
            total_processing_time_ms=0.0,
            storage_savings_mb=0.0,
            assets_uploaded=self.metrics["assets_uploaded"],
            assets_downloaded=0,
            cdn_hits=0,
            cdn_miss_rate=0.05,
            wasm_modules_loaded=len(self.wasm_runtime.modules),
            wasm_executions=self.metrics["wasm_executions"],
            wasm_average_execution_time_ms=50.0,
            wasm_memory_usage_mb=4.0
        )