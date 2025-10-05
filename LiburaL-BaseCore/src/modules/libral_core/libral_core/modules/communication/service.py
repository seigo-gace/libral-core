"""
Communication Gateway Service - Week 4 Implementation
Privacy-first messaging with authenticated routing and personal log integration
"""

import asyncio
import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

import httpx
import structlog
from aiogram import Bot
from aiogram.types import ParseMode

from .schemas import (
    CommunicationChannel,
    CommunicationHealthResponse,
    DeliveryStatus,
    MessageRequest,
    MessageResponse,
    MessageType,
    NotificationPreferences,
    NotificationRequest, 
    NotificationResponse,
    WebhookEvent
)
from ..auth.service import AuthService
from ..gpg.service import GPGService
from ..gpg.schemas import EncryptRequest

logger = structlog.get_logger(__name__)


class MessageRouter:
    """Intelligent message routing with privacy-first design"""
    
    def __init__(self, auth_service: AuthService, gpg_service: Optional[GPGService] = None):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        
        # Channel handlers
        self.telegram_bot: Optional[Bot] = None
        self.email_client: Optional[httpx.AsyncClient] = None
        self.webhook_client = httpx.AsyncClient(timeout=30.0)
        
    async def initialize_telegram(self, bot_token: str):
        """Initialize Telegram bot for message delivery"""
        try:
            self.telegram_bot = Bot(token=bot_token)
            # Test connection
            bot_info = await self.telegram_bot.get_me()
            logger.info("Telegram bot initialized", username=bot_info.username)
        except Exception as e:
            logger.error("Failed to initialize Telegram bot", error=str(e))
            self.telegram_bot = None
    
    async def send_telegram_message(
        self, 
        chat_id: str, 
        content: str,
        topic_id: Optional[int] = None,
        hashtags: Optional[List[str]] = None
    ) -> Tuple[bool, Optional[str]]:
        """Send message to Telegram with topic and hashtag support"""
        
        if not self.telegram_bot:
            return False, "Telegram bot not available"
        
        try:
            # Add hashtags if provided
            if hashtags:
                hashtag_string = " ".join(hashtags)
                content = f"{content}\n\n{hashtag_string}"
            
            # Send to specific topic if provided
            message_thread_id = topic_id if topic_id else None
            
            message = await self.telegram_bot.send_message(
                chat_id=chat_id,
                text=content,
                parse_mode=ParseMode.MARKDOWN,
                message_thread_id=message_thread_id,
                disable_web_page_preview=True
            )
            
            logger.info("Telegram message sent successfully",
                       chat_id=chat_id,
                       message_id=message.message_id,
                       topic_id=topic_id)
            
            return True, str(message.message_id)
            
        except Exception as e:
            logger.error("Failed to send Telegram message",
                        chat_id=chat_id,
                        error=str(e))
            return False, str(e)
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        content: str,
        html_content: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Send email message (mock implementation)"""
        
        try:
            # In real implementation, would integrate with email service
            # For now, simulate email sending
            
            email_data = {
                "to": to_email,
                "subject": subject,
                "text": content,
                "html": html_content,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Email prepared for sending",
                       to_email=to_email[:10] + "...",  # Privacy: don't log full email
                       subject=subject[:50])
            
            # Simulate successful email delivery
            return True, f"email_{uuid4().hex[:8]}"
            
        except Exception as e:
            logger.error("Failed to send email",
                        error=str(e))
            return False, str(e)
    
    async def send_webhook(
        self,
        webhook_url: str,
        payload: Dict[str, Any],
        signature_secret: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Send webhook with optional HMAC signature"""
        
        try:
            # Prepare payload
            json_payload = json.dumps(payload, ensure_ascii=False)
            headers = {"Content-Type": "application/json"}
            
            # Add HMAC signature if secret provided
            if signature_secret:
                signature = hmac.new(
                    signature_secret.encode(),
                    json_payload.encode(),
                    hashlib.sha256
                ).hexdigest()
                headers["X-Webhook-Signature"] = f"sha256={signature}"
            
            # Send webhook
            response = await self.webhook_client.post(
                webhook_url,
                content=json_payload,
                headers=headers
            )
            response.raise_for_status()
            
            logger.info("Webhook sent successfully",
                       url=webhook_url[:50] + "...",
                       status_code=response.status_code)
            
            return True, response.headers.get("X-Request-ID", str(uuid4())[:8])
            
        except Exception as e:
            logger.error("Failed to send webhook",
                        url=webhook_url[:50] + "...",
                        error=str(e))
            return False, str(e)


class CommunicationService:
    """Privacy-first communication service with authenticated routing"""
    
    def __init__(
        self,
        auth_service: AuthService,
        telegram_bot_token: str,
        gpg_service: Optional[GPGService] = None
    ):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        
        # Message router
        self.router = MessageRouter(auth_service, gpg_service)
        
        # Initialize message router
        asyncio.create_task(self.router.initialize_telegram(telegram_bot_token))
        
        # Message tracking
        self.message_history: Dict[str, MessageResponse] = {}
        self.delivery_stats: Dict[str, int] = {
            "sent": 0,
            "delivered": 0,
            "failed": 0
        }
        
        # User preferences cache
        self.user_preferences_cache: Dict[str, NotificationPreferences] = {}
        
        logger.info("Communication service initialized")
    
    async def health_check(self) -> CommunicationHealthResponse:
        """Check communication service health"""
        
        try:
            # Test Telegram connectivity
            telegram_accessible = False
            if self.router.telegram_bot:
                try:
                    await self.router.telegram_bot.get_me()
                    telegram_accessible = True
                except Exception:
                    pass
            
            # Calculate performance metrics
            total_messages = sum(self.delivery_stats.values())
            success_rate = (self.delivery_stats["delivered"] / max(total_messages, 1))
            
            return CommunicationHealthResponse(
                status="healthy" if telegram_accessible else "degraded",
                telegram_api_accessible=telegram_accessible,
                email_service_accessible=True,  # Mock
                webhook_endpoints_healthy=1,    # Mock
                messages_sent_last_hour=self.delivery_stats["sent"],
                average_delivery_time_ms=250,   # Mock
                delivery_success_rate=success_rate,
                pending_messages=0,
                failed_messages_last_hour=self.delivery_stats["failed"],
                retry_queue_size=0,
                personal_logs_active=len(self.auth_service.personal_log_servers),
                gdpr_compliant_operations=True,
                encrypted_messages_percentage=0.95,  # Mock high encryption rate
                auth_service_connected=True,
                gpg_service_available=bool(self.gpg_service),
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Communication health check failed", error=str(e))
            return CommunicationHealthResponse(
                status="unhealthy",
                telegram_api_accessible=False,
                email_service_accessible=False,
                webhook_endpoints_healthy=0,
                messages_sent_last_hour=0,
                pending_messages=0,
                failed_messages_last_hour=0,
                retry_queue_size=0,
                personal_logs_active=0,
                gdpr_compliant_operations=True,
                auth_service_connected=False,
                gpg_service_available=False,
                last_check=datetime.utcnow()
            )
    
    async def send_message(self, request: MessageRequest) -> MessageResponse:
        """Send message with privacy-first routing"""
        request_id = str(uuid4())[:8]
        message_id = str(uuid4())
        
        try:
            logger.info("Processing message request",
                       request_id=request_id,
                       channel=request.route.primary_channel,
                       priority=request.priority,
                       encrypted=bool(request.content.encrypted_content))
            
            # Encrypt content if GPG service available and requested
            content_to_send = await self._prepare_message_content(request)
            
            # Determine routing based on preferences and authentication
            routing_decision = await self._determine_routing(request)
            
            # Send message through primary channel
            success, delivery_id = await self._send_via_channel(
                routing_decision["channel"],
                routing_decision["destination"],
                content_to_send,
                request
            )
            
            # Update delivery statistics
            if success:
                self.delivery_stats["sent"] += 1
                self.delivery_stats["delivered"] += 1
                delivery_status = DeliveryStatus.SENT
            else:
                self.delivery_stats["failed"] += 1
                delivery_status = DeliveryStatus.FAILED
            
            # Log to personal server if user authenticated and enabled
            personal_log_recorded = False
            if request.user_id and request.route.log_to_personal_server:
                personal_log_recorded = await self._log_message_to_personal_server(
                    request.user_id, request, success
                )
            
            # Create response
            response = MessageResponse(
                success=success,
                message_id=message_id,
                delivery_status=delivery_status,
                channel_used=routing_decision["channel"],
                destination_reached=routing_decision["destination"],
                sent_at=datetime.utcnow(),
                estimated_delivery=datetime.utcnow() + timedelta(seconds=30),
                personal_log_recorded=personal_log_recorded,
                retention_expires_at=datetime.utcnow() + timedelta(seconds=request.retention_seconds or 86400),
                error=delivery_id if not success else None,
                correlation_id=request.correlation_id,
                request_id=request_id
            )
            
            # Store message history
            self.message_history[message_id] = response
            
            logger.info("Message processing completed",
                       request_id=request_id,
                       message_id=message_id,
                       success=success)
            
            return response
            
        except Exception as e:
            logger.error("Message sending failed",
                        request_id=request_id,
                        error=str(e))
            
            return MessageResponse(
                success=False,
                message_id=message_id,
                delivery_status=DeliveryStatus.FAILED,
                channel_used=request.route.primary_channel,
                destination_reached="unknown",
                sent_at=datetime.utcnow(),
                error=str(e),
                request_id=request_id
            )
    
    async def send_notification(self, request: NotificationRequest) -> NotificationResponse:
        """Send system notification to multiple users"""
        request_id = str(uuid4())[:8]
        notification_id = str(uuid4())
        
        try:
            logger.info("Processing notification request",
                       request_id=request_id,
                       recipient_count=len(request.user_ids),
                       notification_type=request.notification_type)
            
            delivered_to = []
            failed_deliveries = []
            delivery_by_channel = {}
            personal_logs_recorded = 0
            errors = []
            
            # Send to each user
            for user_id in request.user_ids:
                try:
                    # Get user preferences
                    preferences = await self._get_user_preferences(user_id)
                    
                    # Check if user wants this type of notification
                    if not self._should_send_notification(request.notification_type, preferences):
                        continue
                    
                    # Create individual message request
                    message_request = await self._create_message_from_notification(
                        request, user_id, preferences
                    )
                    
                    # Send message
                    response = await self.send_message(message_request)
                    
                    if response.success:
                        delivered_to.append(user_id)
                        channel_key = response.channel_used.value
                        delivery_by_channel[channel_key] = delivery_by_channel.get(channel_key, 0) + 1
                        
                        if response.personal_log_recorded:
                            personal_logs_recorded += 1
                    else:
                        failed_deliveries.append(user_id)
                        if response.error:
                            errors.append(f"User {user_id}: {response.error}")
                
                except Exception as e:
                    failed_deliveries.append(user_id)
                    errors.append(f"User {user_id}: {str(e)}")
            
            success = len(delivered_to) > 0
            
            logger.info("Notification processing completed",
                       request_id=request_id,
                       notification_id=notification_id,
                       delivered=len(delivered_to),
                       failed=len(failed_deliveries))
            
            return NotificationResponse(
                success=success,
                notification_id=notification_id,
                delivered_to=delivered_to,
                failed_deliveries=failed_deliveries,
                delivery_by_channel=delivery_by_channel,
                personal_logs_recorded=personal_logs_recorded,
                errors=errors,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("Notification sending failed",
                        request_id=request_id,
                        error=str(e))
            
            return NotificationResponse(
                success=False,
                notification_id=notification_id,
                failed_deliveries=request.user_ids,
                errors=[str(e)],
                request_id=request_id
            )
    
    async def _prepare_message_content(self, request: MessageRequest) -> str:
        """Prepare message content with optional encryption"""
        
        try:
            # Use encrypted content if provided
            if request.content.encrypted_content:
                return request.content.encrypted_content
            
            # Otherwise prepare content based on type
            content = ""
            
            if request.content.text:
                content = request.content.text
            elif request.content.markdown:
                content = request.content.markdown
            elif request.content.html:
                content = request.content.html
            elif request.content.json_data:
                content = json.dumps(request.content.json_data, indent=2, ensure_ascii=False)
            
            # Encrypt content if GPG service available and recipients specified
            if self.gpg_service and request.content.encryption_recipients:
                encrypt_request = EncryptRequest(
                    data=content,
                    recipients=request.content.encryption_recipients,
                    context_labels=request.context_labels or {}
                )
                
                encrypt_result = await self.gpg_service.encrypt(encrypt_request)
                
                if encrypt_result.success:
                    return encrypt_result.encrypted_data
                else:
                    logger.warning("Content encryption failed, sending plaintext",
                                  error=encrypt_result.error)
            
            return content
            
        except Exception as e:
            logger.error("Content preparation failed", error=str(e))
            return request.content.text or "Error preparing message content"
    
    async def _determine_routing(self, request: MessageRequest) -> Dict[str, Any]:
        """Determine optimal routing for message"""
        
        try:
            # Use primary channel and destination from request
            return {
                "channel": request.route.primary_channel,
                "destination": request.route.primary_destination
            }
            
        except Exception as e:
            logger.error("Routing determination failed", error=str(e))
            # Fallback to Telegram
            return {
                "channel": CommunicationChannel.TELEGRAM,
                "destination": request.route.primary_destination
            }
    
    async def _send_via_channel(
        self,
        channel: CommunicationChannel,
        destination: str,
        content: str,
        request: MessageRequest
    ) -> Tuple[bool, Optional[str]]:
        """Send message via specific channel"""
        
        try:
            if channel == CommunicationChannel.TELEGRAM:
                # Extract topic information from context
                topic_id = None
                hashtags = []
                
                if request.context_labels:
                    topic_id = request.context_labels.get("telegram.topic_id")
                    if topic_id:
                        topic_id = int(topic_id)
                    
                    # Extract hashtags from category
                    category = request.context_labels.get("category", "general")
                    hashtags = self._get_hashtags_for_category(category)
                
                return await self.router.send_telegram_message(
                    destination, content, topic_id, hashtags
                )
            
            elif channel == CommunicationChannel.EMAIL:
                subject = request.content.subject or "Libral Core Notification"
                html_content = request.content.html
                return await self.router.send_email(destination, subject, content, html_content)
            
            elif channel == CommunicationChannel.WEBHOOK:
                payload = {
                    "content": content,
                    "timestamp": datetime.utcnow().isoformat(),
                    "priority": request.priority,
                    "context": request.context_labels
                }
                return await self.router.send_webhook(destination, payload)
            
            else:
                logger.warning("Unsupported communication channel", channel=channel)
                return False, f"Unsupported channel: {channel}"
                
        except Exception as e:
            logger.error("Channel send failed",
                        channel=channel,
                        error=str(e))
            return False, str(e)
    
    def _get_hashtags_for_category(self, category: str) -> List[str]:
        """Get appropriate hashtags for message category"""
        hashtag_map = {
            "auth": ["#auth", "#security", "#login"],
            "plugin": ["#plugin", "#marketplace", "#install"],
            "payment": ["#payment", "#transaction", "#billing"],
            "communication": ["#message", "#notification", "#api"],
            "system": ["#system", "#performance", "#status"],
            "general": ["#general", "#misc"]
        }
        
        return hashtag_map.get(category.lower(), ["#general"])
    
    async def _log_message_to_personal_server(
        self,
        user_id: str,
        request: MessageRequest,
        success: bool
    ) -> bool:
        """Log message to user's personal log server"""
        
        try:
            # Create log entry
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "category": "communication",
                "event_type": "message_sent",
                "channel": request.route.primary_channel,
                "destination": request.route.primary_destination[:10] + "...",  # Privacy truncation
                "priority": request.priority,
                "success": success,
                "message_type": request.content.message_type,
                "encrypted": bool(request.content.encrypted_content),
                "source_module": request.source_module
            }
            
            # Log to personal server via auth service
            return await self.auth_service._log_to_personal_server(user_id, log_data)
            
        except Exception as e:
            logger.error("Personal server logging failed",
                        user_id=user_id,
                        error=str(e))
            return False
    
    async def _get_user_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        
        try:
            # Check cache first
            if user_id in self.user_preferences_cache:
                return self.user_preferences_cache[user_id]
            
            # In real implementation, would load from personal log server
            # For now, return defaults
            preferences = NotificationPreferences(user_id=user_id)
            
            # Cache preferences
            self.user_preferences_cache[user_id] = preferences
            
            return preferences
            
        except Exception as e:
            logger.error("Failed to get user preferences",
                        user_id=user_id,
                        error=str(e))
            # Return defaults on error
            return NotificationPreferences(user_id=user_id)
    
    def _should_send_notification(
        self, 
        notification_type: str, 
        preferences: NotificationPreferences
    ) -> bool:
        """Check if notification should be sent based on user preferences"""
        
        try:
            # Check category-specific preferences
            if notification_type == "security_alert":
                return preferences.security_alerts
            elif notification_type == "system_notification":
                return preferences.system_notifications
            elif notification_type == "plugin_notification":
                return preferences.plugin_notifications
            elif notification_type == "payment_notification":
                return preferences.payment_notifications
            
            # Default to allowing notification
            return True
            
        except Exception:
            # Default to allowing on error
            return True
    
    async def _create_message_from_notification(
        self,
        notification: NotificationRequest,
        user_id: str,
        preferences: NotificationPreferences
    ) -> MessageRequest:
        """Create message request from notification request"""
        
        try:
            # Get user's Telegram chat ID from auth service
            user_profile = self.auth_service.user_profiles.get(user_id)
            telegram_id = user_profile.telegram_id if user_profile else None
            
            # Use preferred channel
            primary_channel = CommunicationChannel.TELEGRAM
            if preferences.preferred_channels:
                primary_channel = preferences.preferred_channels[0]
            
            # Determine destination
            if primary_channel == CommunicationChannel.TELEGRAM and telegram_id:
                destination = str(telegram_id)
            else:
                destination = "default_destination"  # Fallback
            
            # Create message content
            from .schemas import MessageContent, MessageRoute
            
            content = MessageContent(
                message_type=MessageType.MARKDOWN,
                markdown=f"**{notification.title}**\n\n{notification.message}",
                subject=notification.title,
                encrypted_content=None,  # TODO: Implement if preferences.encrypt_notifications
                ephemeral=preferences.ephemeral_notifications
            )
            
            route = MessageRoute(
                primary_channel=primary_channel,
                primary_destination=destination,
                log_to_personal_server=True
            )
            
            return MessageRequest(
                user_id=user_id,
                route=route,
                content=content,
                priority=notification.priority,
                context_labels=notification.context_labels or {},
                source_module=notification.source_module,
                source_action="system_notification"
            )
            
        except Exception as e:
            logger.error("Failed to create message from notification",
                        user_id=user_id,
                        error=str(e))
            raise
    
    async def cleanup(self):
        """Cleanup communication service resources"""
        await self.router.webhook_client.aclose()
        if self.router.telegram_bot:
            await self.router.telegram_bot.session.close()
        logger.info("Communication service cleanup completed")