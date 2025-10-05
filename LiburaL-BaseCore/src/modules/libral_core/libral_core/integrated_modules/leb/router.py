"""
Libral Event Bus (LEB) - FastAPI Router
Unified API endpoints for Communication Gateway + Event Management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .schemas import (
    BaseEvent, EventBatch, EventBusConfig, EventBusHealth,
    EventFilter, EventMetrics, EventPublishRequest, EventPublishResponse, 
    EventQuery, LEBError, Message, MessageSendRequest, MessageSendResponse,
    MessageTemplate, PersonalLogEntry, TopicConfiguration,
    WebhookEvent, WebhookRegistrationRequest
)
from .service import LibralEventBus

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2/eventbus", tags=["Libral Event Bus"])

# Initialize LEB service (in production, this would be dependency injected)
leb_service = LibralEventBus()

# Security
security = HTTPBearer()


# Dependency for getting current user from token
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from access token"""
    token = credentials.credentials
    
    # Simple token parsing (in production, would validate JWT)
    if not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    # Extract user from token (simplified)
    session_id = token.replace("access_token_", "")
    return f"user_{session_id}"  # Simplified user ID


# Health and Status Endpoints
@router.get("/health", response_model=EventBusHealth)
async def get_health():
    """Get LEB module health status"""
    return await leb_service.get_health()


@router.get("/metrics", response_model=EventMetrics)
async def get_metrics(
    period_hours: int = 24,
    user_id: str = Depends(get_current_user_id)
):
    """Get event processing metrics"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=period_hours)
    
    return await leb_service.get_metrics(start_time, end_time)


# Event Management Endpoints
@router.post("/events/publish", response_model=EventPublishResponse)
async def publish_event(
    request: EventPublishRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_id)
):
    """Publish event to the event bus"""
    try:
        # Set user context if not provided
        if not request.event.user_id:
            request.event.user_id = user_id
        
        logger.info("Event publish request", 
                   event_type=request.event.event_type,
                   source=request.event.source,
                   user_id=user_id)
        
        response = await leb_service.publish_event(request)
        
        if response.success:
            logger.info("Event published successfully", 
                       event_id=response.event_id,
                       user_id=user_id)
        else:
            logger.warning("Event publish failed", 
                          error=response.error,
                          user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Event publish endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Event publishing failed"
        )


@router.post("/events/batch", response_model=Dict[str, Any])
async def publish_event_batch(
    batch: EventBatch,
    user_id: str = Depends(get_current_user_id)
):
    """Publish multiple events in batch"""
    try:
        results = []
        successful_events = 0
        failed_events = 0
        
        for event in batch.events:
            # Set user context
            if not event.user_id:
                event.user_id = user_id
            
            request = EventPublishRequest(event=event)
            response = await leb_service.publish_event(request)
            
            results.append({
                "event_id": event.event_id,
                "success": response.success,
                "error": response.error
            })
            
            if response.success:
                successful_events += 1
            else:
                failed_events += 1
        
        logger.info("Event batch processed", 
                   total=len(batch.events),
                   successful=successful_events,
                   failed=failed_events,
                   user_id=user_id)
        
        return {
            "success": True,
            "batch_id": batch.batch_id,
            "total_events": len(batch.events),
            "successful_events": successful_events,
            "failed_events": failed_events,
            "results": results
        }
        
    except Exception as e:
        logger.error("Event batch publish error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch event publishing failed"
        )


@router.get("/events/query")
async def query_events(
    event_types: Optional[str] = None,
    sources: Optional[str] = None,
    priority: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id)
):
    """Query events with filtering"""
    try:
        # Parse filter parameters
        event_filter = EventFilter()
        if event_types:
            event_filter.event_types = event_types.split(",")
        if sources:
            event_filter.sources = sources.split(",")
        if priority:
            event_filter.priorities = [priority]
        
        # Add user filter for privacy
        event_filter.user_ids = [user_id]
        
        query = EventQuery(
            filter=event_filter,
            limit=min(limit, 1000),  # Cap at 1000
            offset=max(offset, 0)
        )
        
        results = await leb_service.query_events(query)
        
        logger.info("Event query executed", 
                   limit=limit,
                   offset=offset,
                   user_id=user_id)
        
        return results
        
    except Exception as e:
        logger.error("Event query error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Event query failed"
        )


# Message Delivery Endpoints
@router.post("/messages/send", response_model=MessageSendResponse)
async def send_message(
    request: MessageSendRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Send message via multiple protocols"""
    try:
        # Set user context
        if not request.message.user_id:
            request.message.user_id = user_id
        
        logger.info("Message send request", 
                   message_id=request.message.message_id,
                   recipients=len(request.message.recipients),
                   user_id=user_id)
        
        response = await leb_service.send_message(request)
        
        if response.success:
            logger.info("Message sent successfully", 
                       message_id=response.message_id,
                       user_id=user_id)
        else:
            logger.warning("Message send failed", 
                          message_id=response.message_id,
                          error=response.error,
                          user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Message send endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Message sending failed"
        )


@router.post("/messages/templates/register")
async def register_message_template(
    template: MessageTemplate,
    user_id: str = Depends(get_current_user_id)
):
    """Register message template"""
    try:
        await leb_service.message_delivery.register_template(template)
        
        logger.info("Message template registered", 
                   template_id=template.template_id,
                   user_id=user_id)
        
        return {
            "success": True,
            "template_id": template.template_id,
            "message": "Template registered successfully"
        }
        
    except Exception as e:
        logger.error("Template registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template registration failed"
        )


@router.get("/messages/templates/{template_id}")
async def get_message_template(
    template_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get message template"""
    try:
        template = leb_service.message_delivery.templates.get(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        return {
            "success": True,
            "template": template.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Template retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Template retrieval failed"
        )


# Personal Log Server Endpoints
@router.post("/personal-log/setup")
async def setup_personal_log_server(
    user_name: str,
    user_id: str = Depends(get_current_user_id)
):
    """Setup personal log server for user"""
    try:
        success, server_config = await leb_service.personal_log_manager.setup_personal_log_server(
            user_id, user_name
        )
        
        if success:
            logger.info("Personal log server setup completed", user_id=user_id)
            
            return {
                "success": True,
                "server_config": server_config,
                "message": "Personal log server setup completed"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Personal log server setup failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Personal log server setup error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Setup failed"
        )


@router.get("/personal-log/status")
async def get_personal_log_server_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get personal log server status"""
    try:
        if user_id in leb_service.personal_log_manager.log_servers:
            server_config = leb_service.personal_log_manager.log_servers[user_id]
            
            return {
                "success": True,
                "status": "active",
                "server_config": server_config
            }
        else:
            return {
                "success": False,
                "status": "not_configured",
                "message": "Personal log server not setup"
            }
        
    except Exception as e:
        logger.error("Personal log server status error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status check failed"
        )


@router.get("/personal-log/topics")
async def get_personal_log_topics(
    user_id: str = Depends(get_current_user_id)
):
    """Get personal log server topic configuration"""
    try:
        if user_id in leb_service.personal_log_manager.topic_configs:
            topics = leb_service.personal_log_manager.topic_configs[user_id]
            
            return {
                "success": True,
                "topics": [topic.dict() for topic in topics]
            }
        else:
            return {
                "success": False,
                "message": "No topic configuration found"
            }
        
    except Exception as e:
        logger.error("Topic configuration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Topic configuration retrieval failed"
        )


# Webhook Management Endpoints
@router.post("/webhooks/register")
async def register_webhook(
    request: WebhookRegistrationRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Register webhook endpoint"""
    try:
        success = await leb_service.register_webhook(request)
        
        if success:
            logger.info("Webhook registered", 
                       webhook_id=request.webhook_id,
                       source=request.source,
                       user_id=user_id)
            
            return {
                "success": True,
                "webhook_id": request.webhook_id,
                "message": "Webhook registered successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Webhook registration failed"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/webhooks/{webhook_id}/process")
async def process_webhook(
    webhook_id: str,
    payload: Dict[str, Any],
    request: Request
):
    """Process incoming webhook (public endpoint)"""
    try:
        # Extract headers
        headers = dict(request.headers)
        
        webhook_event = await leb_service.process_webhook(webhook_id, payload, headers)
        
        logger.info("Webhook processed", 
                   webhook_id=webhook_id,
                   source=webhook_event.source,
                   verified=webhook_event.verified)
        
        return {
            "success": webhook_event.processed,
            "webhook_id": webhook_id,
            "event_type": webhook_event.event_type,
            "verified": webhook_event.verified,
            "processing_error": webhook_event.processing_error
        }
        
    except Exception as e:
        logger.error("Webhook processing error", error=str(e), webhook_id=webhook_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.get("/webhooks/list")
async def list_webhooks(
    user_id: str = Depends(get_current_user_id)
):
    """List registered webhooks"""
    try:
        webhooks = []
        for webhook_id, config in leb_service.webhook_processor.registered_webhooks.items():
            webhooks.append({
                "webhook_id": webhook_id,
                "source": config["source"],
                "endpoint_url": config["endpoint_url"],
                "active": config["active"],
                "event_types": config["event_types"],
                "created_at": config["created_at"].isoformat()
            })
        
        return {
            "success": True,
            "webhooks": webhooks,
            "total_count": len(webhooks)
        }
        
    except Exception as e:
        logger.error("Webhook list error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook list retrieval failed"
        )


# WebSocket and Real-time Endpoints
@router.get("/realtime/status")
async def get_realtime_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get real-time connection status"""
    try:
        return {
            "success": True,
            "websocket_enabled": leb_service.config.websocket_enabled,
            "connected_clients": len(leb_service.websocket_connections),
            "broadcast_system_events": leb_service.config.broadcast_system_events,
            "broadcast_user_events": leb_service.config.broadcast_user_events
        }
        
    except Exception as e:
        logger.error("Real-time status error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Status check failed"
        )


# Configuration Endpoints
@router.get("/config")
async def get_config(
    user_id: str = Depends(get_current_user_id)
):
    """Get event bus configuration"""
    return {
        "success": True,
        "config": leb_service.config.dict()
    }


@router.put("/config")
async def update_config(
    config_updates: Dict[str, Any],
    user_id: str = Depends(get_current_user_id)
):
    """Update event bus configuration"""
    try:
        # Validate and apply configuration updates
        valid_fields = [
            "max_queue_size", "max_retry_attempts", "retry_delay_seconds",
            "default_message_ttl_hours", "personal_log_encryption",
            "websocket_enabled", "broadcast_system_events"
        ]
        
        applied_updates = {}
        for field, value in config_updates.items():
            if field in valid_fields:
                setattr(leb_service.config, field, value)
                applied_updates[field] = value
        
        logger.info("Configuration updated", 
                   updates=applied_updates,
                   user_id=user_id)
        
        return {
            "success": True,
            "applied_updates": applied_updates,
            "message": "Configuration updated successfully"
        }
        
    except Exception as e:
        logger.error("Configuration update error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration update failed"
        )


# Admin and Debug Endpoints
@router.get("/admin/queue-status")
async def get_queue_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get event queue status (admin only)"""
    try:
        queue_status = {}
        for priority, queue in leb_service.event_queue.queues.items():
            queue_status[priority.value] = {
                "size": queue.qsize(),
                "max_size": queue.maxsize,
                "utilization": queue.qsize() / queue.maxsize if queue.maxsize > 0 else 0
            }
        
        return {
            "success": True,
            "queue_status": queue_status,
            "processing_tasks": len(leb_service.event_queue.processing_tasks),
            "registered_handlers": {
                event_type.value: len(handlers) 
                for event_type, handlers in leb_service.event_queue.event_handlers.items()
            }
        }
        
    except Exception as e:
        logger.error("Queue status error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Queue status retrieval failed"
        )


@router.get("/admin/stats")
async def get_detailed_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed LEB statistics"""
    try:
        return {
            "success": True,
            "statistics": {
                **leb_service.metrics,
                "event_handlers": len(leb_service.event_queue.event_handlers),
                "message_templates": len(leb_service.message_delivery.templates),
                "personal_log_servers": len(leb_service.personal_log_manager.log_servers),
                "registered_webhooks": len(leb_service.webhook_processor.registered_webhooks),
                "websocket_connections": len(leb_service.websocket_connections)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Detailed stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statistics retrieval failed"
        )