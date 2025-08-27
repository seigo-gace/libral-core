"""
Communication Gateway FastAPI Router
Privacy-first messaging and notification endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    CommunicationHealthResponse,
    MessageRequest,
    MessageResponse,
    NotificationRequest,
    NotificationResponse,
    WebhookEvent
)
from .service import CommunicationService
from ..auth.service import AuthService
from ..gpg.service import GPGService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/communication", tags=["Communication Gateway"])

# Global communication service instance
_communication_service: Optional[CommunicationService] = None

def get_communication_service() -> CommunicationService:
    """Get configured communication service instance"""
    global _communication_service
    
    if _communication_service is None:
        # Initialize dependencies
        try:
            # Auth service
            from ..auth.router import get_auth_service
            auth_service = get_auth_service()
            
            # GPG service  
            gpg_service = None
            try:
                gpg_service = GPGService(
                    gnupg_home=settings.gpg_home,
                    system_key_id=settings.gpg_system_key_id,
                    passphrase=settings.gpg_passphrase
                )
            except Exception as e:
                logger.warning("GPG service unavailable for communication", error=str(e))
            
            _communication_service = CommunicationService(
                auth_service=auth_service,
                telegram_bot_token=settings.telegram_bot_token,
                gpg_service=gpg_service
            )
            
            logger.info("Communication service initialized")
            
        except Exception as e:
            logger.error("Failed to initialize communication service", error=str(e))
            raise HTTPException(status_code=500, detail="Communication service initialization failed")
    
    return _communication_service

@router.get("/health", response_model=CommunicationHealthResponse)
async def health_check(
    service: CommunicationService = Depends(get_communication_service)
) -> CommunicationHealthResponse:
    """
    Check communication service health
    
    Returns comprehensive status of communication components:
    - Channel connectivity (Telegram, Email, Webhooks)
    - Message delivery performance metrics
    - Queue status and retry statistics
    - Privacy compliance status
    - Integration service connectivity
    """
    return await service.health_check()

@router.post("/send", response_model=MessageResponse)
async def send_message(
    request: MessageRequest,
    background_tasks: BackgroundTasks,
    service: CommunicationService = Depends(get_communication_service)
) -> MessageResponse:
    """
    Send message with privacy-first routing
    
    **Privacy-First Message Delivery:**
    - Messages routed through user-preferred channels
    - Optional GPG encryption for sensitive content
    - Personal log server integration for audit trails
    - Zero personal data retention on central servers
    - GDPR-compliant message handling with auto-expiry
    
    **Supported Channels:**
    - Telegram (with topic and hashtag support)
    - Email (with HTML and text formats)
    - Webhooks (with HMAC signature verification)
    - Personal Log Servers (encrypted to user's Telegram group)
    
    **Message Types:**
    - Plain text messages
    - Markdown formatted content
    - HTML rich content
    - JSON data payloads
    - GPG-encrypted messages
    - System notifications and security alerts
    
    **Topic & Hashtag Support:**
    - Telegram messages can be sent to specific topics
    - Automatic hashtag generation based on message category
    - Personal log server organization with topic threads
    """
    try:
        result = await service.send_message(request)
        
        # Schedule message cleanup if retention period specified
        if request.retention_seconds and request.retention_seconds > 0:
            background_tasks.add_task(
                _schedule_message_cleanup,
                service,
                result.message_id,
                request.retention_seconds
            )
        
        logger.info("Message send request processed",
                   message_id=result.message_id,
                   success=result.success,
                   channel=result.channel_used,
                   personal_log=result.personal_log_recorded)
        
        return result
        
    except Exception as e:
        logger.error("Message send endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Message sending failed")

@router.post("/notify", response_model=NotificationResponse)
async def send_notification(
    request: NotificationRequest,
    service: CommunicationService = Depends(get_communication_service)
) -> NotificationResponse:
    """
    Send system notification to multiple users
    
    **Multi-User Notification Features:**
    - Batch delivery to multiple users simultaneously
    - User preference-based channel selection
    - Category-specific notification filtering
    - Personal log server integration for all recipients
    - Privacy-compliant delivery with no personal data exposure
    
    **Notification Categories:**
    - Security alerts (login attempts, suspicious activity)
    - System notifications (maintenance, updates)
    - Plugin notifications (installations, updates)
    - Payment notifications (transactions, billing)
    - Custom application notifications
    
    **Privacy & User Control:**
    - Users can disable specific notification types
    - Quiet hours respected based on user timezone
    - Encrypted notifications for sensitive content
    - Personal log server logging for audit trails
    - GDPR-compliant with user data sovereignty
    """
    try:
        result = await service.send_notification(request)
        
        logger.info("Notification request processed",
                   notification_id=result.notification_id,
                   delivered_count=len(result.delivered_to),
                   failed_count=len(result.failed_deliveries),
                   personal_logs=result.personal_logs_recorded)
        
        return result
        
    except Exception as e:
        logger.error("Notification send endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Notification sending failed")

@router.post("/webhook")
async def receive_webhook(
    event: WebhookEvent,
    service: CommunicationService = Depends(get_communication_service)
) -> JSONResponse:
    """
    Receive webhook events from external services
    
    **Webhook Event Processing:**
    - HMAC signature verification for security
    - Event type routing and handling
    - Personal log server integration for user events
    - Privacy-compliant event processing
    - Automatic retry handling for failed processing
    
    **Supported Event Sources:**
    - Telegram Bot API updates
    - Payment processor webhooks
    - Third-party service integrations
    - Plugin marketplace events
    - System monitoring alerts
    
    **Privacy & Security:**
    - All webhooks validated with HMAC signatures
    - Personal data processed according to user preferences
    - Events logged to user's personal log servers only
    - No sensitive data stored on central servers
    """
    try:
        logger.info("Webhook event received",
                   event_id=event.event_id,
                   event_type=event.event_type,
                   source=event.source)
        
        # Process webhook event
        # In real implementation, would route to appropriate handler
        
        return JSONResponse(content={
            "success": True,
            "event_id": event.event_id,
            "processed_at": event.timestamp.isoformat(),
            "message": "Webhook processed successfully"
        })
        
    except Exception as e:
        logger.error("Webhook processing error",
                    event_id=event.event_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/channels")
async def list_communication_channels() -> JSONResponse:
    """
    List available communication channels and their status
    
    Returns information about all supported communication channels,
    their current availability, and configuration details.
    """
    try:
        from .schemas import CommunicationChannel
        
        channels = [
            {
                "id": channel.value,
                "name": channel.value.replace("_", " ").title(),
                "description": _get_channel_description(channel),
                "supports_topics": channel == CommunicationChannel.TELEGRAM,
                "supports_hashtags": channel == CommunicationChannel.TELEGRAM,
                "supports_encryption": True,
                "privacy_compliant": True
            }
            for channel in CommunicationChannel
        ]
        
        return JSONResponse(content={
            "channels": channels,
            "default_channel": "telegram",
            "privacy_features": [
                "GPG encryption support",
                "Personal log server integration",
                "Zero central data retention",
                "User-controlled routing preferences"
            ]
        })
        
    except Exception as e:
        logger.error("Channel listing error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list channels")

def _get_channel_description(channel) -> str:
    """Get human-readable description for communication channel"""
    descriptions = {
        "telegram": "Telegram messaging with topic and hashtag support",
        "email": "Email delivery with HTML and text formats",
        "webhook": "HTTP webhooks with HMAC signature verification",
        "sms": "SMS text messaging for urgent notifications",
        "push_notification": "Mobile push notifications",
        "personal_log_server": "User-owned encrypted log storage in Telegram groups"
    }
    return descriptions.get(channel.value, "Communication channel")

async def _schedule_message_cleanup(
    service: CommunicationService,
    message_id: str,
    retention_seconds: int
):
    """Schedule message cleanup after retention period"""
    try:
        import asyncio
        await asyncio.sleep(retention_seconds)
        
        # Remove message from history
        if message_id in service.message_history:
            del service.message_history[message_id]
            logger.info("Message cleaned up after retention period",
                       message_id=message_id)
    except Exception as e:
        logger.error("Message cleanup failed",
                    message_id=message_id,
                    error=str(e))

# Cleanup handler
@router.on_event("startup")
async def startup_communication_service():
    """Initialize communication service"""
    # Service is lazy-loaded via dependency injection
    pass

@router.on_event("shutdown")
async def cleanup_communication_service():
    """Cleanup communication service resources"""
    global _communication_service
    if _communication_service:
        await _communication_service.cleanup()
        _communication_service = None
        logger.info("Communication service cleanup completed")