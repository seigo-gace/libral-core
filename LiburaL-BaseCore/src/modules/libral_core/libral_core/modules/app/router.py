"""
Libral APP Module - FastAPI Router
Application management API endpoints
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .schemas import (
    App, AppAnalytics, AppCreate, AppHealth, AppModuleHealth,
    AppOperationResponse, AppStatus, AppUpdate
)
from .service import LibralApp

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/apps", tags=["Libral APP Management"])

# Initialize APP service (will be properly initialized in app.py)
app_service: Optional[LibralApp] = None

# Security
security = HTTPBearer()


def get_app_service() -> LibralApp:
    """Get APP service instance"""
    if app_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="APP service not initialized"
        )
    return app_service


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
@router.get("/health", response_model=AppModuleHealth)
async def get_health(service: LibralApp = Depends(get_app_service)):
    """Get APP module health status"""
    return await service.get_health()


@router.get("/stats")
async def get_stats(
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Get APP module statistics"""
    return {
        "success": True,
        "statistics": service.stats,
        "timestamp": datetime.utcnow().isoformat()
    }


# Application CRUD Endpoints
@router.post("/create", response_model=App, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: AppCreate,
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Create new application"""
    try:
        logger.info("Creating application", name=app_data.name, owner=app_data.owner_id)
        
        # Verify owner matches authenticated user
        if app_data.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create application for different user"
            )
        
        app = await service.create_app(app_data)
        
        logger.info("Application created successfully", app_id=app.app_id)
        return app
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Application creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )


@router.get("/{app_id}", response_model=App)
async def get_application(
    app_id: str,
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Get application by ID"""
    try:
        app = await service.get_app(app_id)
        
        if not app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Check permission (simplified - owner check only)
        if app.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return app
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get application", app_id=app_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application"
        )


@router.put("/{app_id}", response_model=App)
async def update_application(
    app_id: str,
    update_data: AppUpdate,
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Update application"""
    try:
        # Check if app exists and user has permission
        existing_app = await service.get_app(app_id)
        
        if not existing_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        if existing_app.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        updated_app = await service.update_app(app_id, update_data)
        
        if not updated_app:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Update failed"
            )
        
        logger.info("Application updated", app_id=app_id)
        return updated_app
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Application update failed", app_id=app_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application"
        )


@router.delete("/{app_id}", response_model=AppOperationResponse)
async def delete_application(
    app_id: str,
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Delete application"""
    try:
        # Check if app exists and user has permission
        existing_app = await service.get_app(app_id)
        
        if not existing_app:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        if existing_app.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        success = await service.delete_app(app_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Deletion failed"
            )
        
        logger.info("Application deleted", app_id=app_id)
        
        return AppOperationResponse(
            success=True,
            message="Application deleted successfully",
            app_id=app_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Application deletion failed", app_id=app_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        )


@router.get("/", response_model=Dict[str, Any])
async def list_applications(
    status: Optional[AppStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """List applications for current user"""
    try:
        result = await service.list_apps(
            owner_id=user_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        logger.info("Applications listed", 
                   user_id=user_id,
                   count=len(result["apps"]),
                   total=result["total"])
        
        return result
        
    except Exception as e:
        logger.error("Application listing failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list applications"
        )


# Simplified endpoints for quick operations
@router.post("/quick/create")
async def quick_create_app(
    data: Dict[str, Any],
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Quick create application with minimal data"""
    try:
        from .schemas import AppType
        
        app_data = AppCreate(
            name=data.get("name", "New Application"),
            description=data.get("description"),
            app_type=AppType(data.get("app_type", "web")),
            owner_id=user_id,
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            settings=data.get("settings", {})
        )
        
        app = await service.create_app(app_data)
        
        return {
            "success": True,
            "app_id": app.app_id,
            "name": app.name,
            "status": app.status.value,
            "created_at": app.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error("Quick create failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create application"
        )


@router.get("/quick/my-apps")
async def quick_list_my_apps(
    service: LibralApp = Depends(get_app_service),
    user_id: str = Depends(get_current_user_id)
):
    """Quick list of user's applications"""
    try:
        result = await service.list_apps(owner_id=user_id, page=1, page_size=10)
        
        return {
            "success": True,
            "apps": [
                {
                    "app_id": app.app_id,
                    "name": app.name,
                    "type": app.app_type.value,
                    "status": app.status.value,
                    "created_at": app.created_at.isoformat()
                }
                for app in result["apps"]
            ],
            "total": result["total"]
        }
        
    except Exception as e:
        logger.error("Quick list failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list applications"
        )
