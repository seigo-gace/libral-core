"""
Libral Asset Service (LAS) - FastAPI Router
Unified API endpoints for Library utilities + Asset Management + WebAssembly
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import io

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks, File, UploadFile, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
import structlog

from .schemas import (
    APIClientConfig, APIRequest, APIResponse, Asset, AssetQuery, AssetSearchResponse,
    AssetUploadRequest, AssetUploadResponse, DateTimeProcessingRequest, DateTimeProcessingResponse,
    ImageProcessingRequest, LASHealthResponse, LASMetrics,
    ProcessingResult, StringProcessingRequest, StringProcessingResponse,
    VideoProcessingRequest, WASMExecutionRequest, WASMExecutionResponse, WASMModule
)
from .service import LibralAssetService

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2/assets", tags=["Libral Asset Service"])

# Initialize LAS service
las_service = LibralAssetService()

# Security
security = HTTPBearer()


# Dependency for authenticated requests
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from access token"""
    token = credentials.credentials
    
    if not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    session_id = token.replace("access_token_", "")
    return f"user_{session_id}"


# Health and Status Endpoints
@router.get("/health", response_model=LASHealthResponse)
async def get_health():
    """Get LAS module health status"""
    return await las_service.get_health()


@router.get("/metrics", response_model=LASMetrics)
async def get_metrics(
    period_hours: int = 24,
    user_id: str = Depends(get_current_user_id)
):
    """Get LAS module metrics"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=period_hours)
    
    return await las_service.get_metrics(start_time, end_time)


# Utility Processing Endpoints
@router.post("/utils/string", response_model=StringProcessingResponse)
async def process_string(
    request: StringProcessingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Process string operations (sanitize, truncate, validate, format)"""
    try:
        response = await las_service.utility_processor.process_string(request)
        
        las_service.metrics["string_operations"] += 1
        
        logger.info("String operation completed", 
                   operation=request.operation,
                   success=response.success,
                   user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("String processing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="String processing failed"
        )


@router.post("/utils/datetime", response_model=DateTimeProcessingResponse)
async def process_datetime(
    request: DateTimeProcessingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Process datetime operations (parse, format, convert, validate)"""
    try:
        response = await las_service.utility_processor.process_datetime(request)
        
        las_service.metrics["datetime_operations"] += 1
        
        logger.info("DateTime operation completed", 
                   operation=request.operation,
                   success=response.success,
                   user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("DateTime processing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DateTime processing failed"
        )


# API Client Management Endpoints
@router.post("/api-clients/register")
async def register_api_client(
    config: APIClientConfig,
    user_id: str = Depends(get_current_user_id)
):
    """Register external API client configuration"""
    try:
        await las_service.api_client_manager.register_client(config)
        
        logger.info("API client registered", 
                   client_id=config.client_id,
                   name=config.name,
                   user_id=user_id)
        
        return {
            "success": True,
            "client_id": config.client_id,
            "message": "API client registered successfully"
        }
        
    except Exception as e:
        logger.error("API client registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API client registration failed"
        )


@router.post("/api-clients/request", response_model=APIResponse)
async def make_api_request(
    request: APIRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Make request to external API"""
    try:
        response = await las_service.api_client_manager.make_request(request)
        
        las_service.metrics["api_requests"] += 1
        
        logger.info("API request completed", 
                   client_id=request.client_id,
                   method=request.method,
                   success=response.success,
                   user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("API request error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API request failed"
        )


@router.get("/api-clients")
async def list_api_clients(
    user_id: str = Depends(get_current_user_id)
):
    """List registered API clients"""
    try:
        clients = []
        for client_id, config in las_service.api_client_manager.clients.items():
            clients.append({
                "client_id": client_id,
                "name": config.name,
                "base_url": config.base_url,
                "auth_type": config.auth_type,
                "timeout_seconds": config.timeout_seconds
            })
        
        return {
            "success": True,
            "clients": clients,
            "total_count": len(clients)
        }
        
    except Exception as e:
        logger.error("API client listing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API client listing failed"
        )


# Asset Management Endpoints
@router.post("/upload", response_model=AssetUploadResponse)
async def upload_asset(
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    asset_type: str = Form(...),
    access_level: str = Form("private"),
    auto_optimize: bool = Form(True),
    tags: str = Form(""),
    user_id: str = Depends(get_current_user_id)
):
    """Upload asset file"""
    try:
        from .schemas import AssetType, AccessLevel, OptimizationLevel
        
        # Parse form data
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
        
        upload_request = AssetUploadRequest(
            name=name,
            description=description,
            asset_type=AssetType(asset_type),
            access_level=AccessLevel(access_level),
            auto_optimize=auto_optimize,
            tags=tag_list
        )
        
        # Read file data
        file_data = await file.read()
        
        response = await las_service.asset_manager.upload_asset(upload_request, file_data)
        
        if response.success:
            las_service.metrics["assets_uploaded"] += 1
            
            logger.info("Asset uploaded", 
                       asset_id=response.asset_id,
                       name=name,
                       size=len(file_data),
                       user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Asset upload error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset upload failed"
        )


@router.get("/search", response_model=AssetSearchResponse)
async def search_assets(
    asset_types: Optional[str] = None,
    formats: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    user_id: str = Depends(get_current_user_id)
):
    """Search assets with filtering"""
    try:
        from .schemas import AssetType, AssetFormat
        
        # Parse query parameters
        query = AssetQuery(
            asset_types=[AssetType(t.strip()) for t in asset_types.split(",")] if asset_types else None,
            formats=[AssetFormat(f.strip()) for f in formats.split(",")] if formats else None,
            tags=tags.split(",") if tags else None,
            owner_id=user_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        response = await las_service.asset_manager.search_assets(query)
        
        logger.info("Asset search completed", 
                   found=len(response.assets),
                   total=response.total_count,
                   user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Asset search error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset search failed"
        )


@router.get("/{asset_id}")
async def get_asset(
    asset_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get asset details"""
    try:
        if asset_id in las_service.asset_manager.assets:
            asset = las_service.asset_manager.assets[asset_id]
            
            # Check access permissions
            if (asset.access_level.value != "public" and 
                asset.owner_id != user_id and
                user_id not in asset.allowed_users):
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to asset"
                )
            
            return {
                "success": True,
                "asset": asset.dict()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Asset retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Asset retrieval failed"
        )


# File Processing Endpoints
@router.post("/process/image", response_model=ProcessingResult)
async def process_image(
    request: ImageProcessingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Process image with specified operations"""
    try:
        result = await las_service.file_processor.process_image(request)
        
        if result.success:
            las_service.metrics["images_processed"] += 1
            
            logger.info("Image processed", 
                       asset_id=request.asset_id,
                       operations=len(request.operations),
                       user_id=user_id)
        
        return result
        
    except Exception as e:
        logger.error("Image processing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image processing failed"
        )


@router.post("/process/video", response_model=ProcessingResult)
async def process_video(
    request: VideoProcessingRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Process video with specified operations"""
    try:
        result = await las_service.file_processor.process_video(request)
        
        if result.success:
            las_service.metrics["videos_processed"] += 1
            
            logger.info("Video processed", 
                       asset_id=request.asset_id,
                       operations=len(request.operations),
                       user_id=user_id)
        
        return result
        
    except Exception as e:
        logger.error("Video processing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Video processing failed"
        )


# WebAssembly Runtime Endpoints
@router.post("/wasm/register")
async def register_wasm_module(
    module: WASMModule,
    user_id: str = Depends(get_current_user_id)
):
    """Register WebAssembly module"""
    try:
        await las_service.wasm_runtime.register_module(module)
        
        logger.info("WASM module registered", 
                   module_id=module.module_id,
                   name=module.name,
                   user_id=user_id)
        
        return {
            "success": True,
            "module_id": module.module_id,
            "message": "WASM module registered successfully"
        }
        
    except Exception as e:
        logger.error("WASM module registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WASM module registration failed"
        )


@router.post("/wasm/execute", response_model=WASMExecutionResponse)
async def execute_wasm_function(
    request: WASMExecutionRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Execute WebAssembly function"""
    try:
        # Set user context
        request.user_id = user_id
        
        response = await las_service.wasm_runtime.execute_function(request)
        
        if response.success:
            las_service.metrics["wasm_executions"] += 1
            
            logger.info("WASM function executed", 
                       module_id=request.module_id,
                       function=request.function_name,
                       execution_time=response.execution_time_ms,
                       user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("WASM execution error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WASM execution failed"
        )


@router.get("/wasm/modules")
async def list_wasm_modules(
    user_id: str = Depends(get_current_user_id)
):
    """List registered WebAssembly modules"""
    try:
        modules = []
        for module_id, module in las_service.wasm_runtime.modules.items():
            if user_id in module.allowed_users or not module.allowed_users:
                modules.append({
                    "module_id": module_id,
                    "name": module.name,
                    "description": module.description,
                    "version": module.version,
                    "memory_pages": module.memory_pages,
                    "created_at": module.created_at.isoformat()
                })
        
        return {
            "success": True,
            "modules": modules,
            "total_count": len(modules)
        }
        
    except Exception as e:
        logger.error("WASM modules listing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="WASM modules listing failed"
        )


# Admin and Debug Endpoints
@router.get("/admin/stats")
async def get_detailed_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed LAS statistics"""
    try:
        return {
            "success": True,
            "statistics": {
                **las_service.metrics,
                "api_clients": len(las_service.api_client_manager.clients),
                "total_assets": len(las_service.asset_manager.assets),
                "wasm_modules": len(las_service.wasm_runtime.modules),
                "compiled_wasm_modules": len(las_service.wasm_runtime.compiled_modules)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Detailed stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statistics retrieval failed"
        )


@router.get("/admin/system-info")
async def get_system_info(
    user_id: str = Depends(get_current_user_id)
):
    """Get system information and capabilities"""
    try:
        return {
            "success": True,
            "system_info": {
                "utility_processor": {
                    "status": "active",
                    "operations": ["sanitize", "truncate", "validate", "format"],
                    "datetime_formats": ["ISO", "custom", "timezone_conversion"]
                },
                "api_client_manager": {
                    "status": "active", 
                    "registered_clients": len(las_service.api_client_manager.clients),
                    "auth_types": ["bearer", "api_key", "basic", "oauth2"]
                },
                "file_processor": {
                    "status": "active",
                    "supported_formats": ["JPEG", "PNG", "WebP", "MP4", "WebM"],
                    "processing_operations": ["resize", "crop", "rotate", "optimize"]
                },
                "wasm_runtime": {
                    "status": "active",
                    "loaded_modules": len(las_service.wasm_runtime.modules),
                    "supported_types": ["i32", "i64", "f32", "f64"]
                },
                "asset_manager": {
                    "status": "active",
                    "total_assets": len(las_service.asset_manager.assets),
                    "asset_types": ["image", "video", "audio", "document", "wasm"]
                }
            },
            "version": "2.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("System info error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System info retrieval failed"
        )