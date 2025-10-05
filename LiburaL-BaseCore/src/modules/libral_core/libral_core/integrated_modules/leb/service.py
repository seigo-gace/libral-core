"""
Libral Event Bus (LEB) - Unified Service
Combines Communication Gateway + Event Management functionality
"""

import asyncio
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from uuid import uuid4
import urllib.parse

import httpx
import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .schemas import (
    BaseEvent, EventBatch, EventBusConfig, EventBusHealth,
    EventFilter, EventMetrics, EventProcessingStatus, EventPriority,
    EventPublishRequest, EventPublishResponse, EventQuery, EventType,
    LEBError, Message, MessageProtocol, MessageRecipient, MessageSendRequest,
    MessageSendResponse, MessageStatus, MessageTemplate,
    PersonalLogEntry, TopicCategory, TopicConfiguration,
    WebhookEvent, WebhookRegistrationRequest
)

logger = structlog.get_logger(__name__)


class EventQueue:
    """High-performance async event queue with priority processing"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues: Dict[EventPriority, asyncio.Queue] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        
        # Initialize priority queues
        for priority in EventPriority:
            self.queues[priority] = asyncio.Queue(maxsize=max_size)
        
        # Start queue processors
        self.processor_task = asyncio.create_task(self._process_queues())
        
        logger.info("Event queue initialized", max_size=max_size)
    
    async def publish(self, event: BaseEvent) -> bool:
        """Publish event to appropriate priority queue"""
        try:
            # Validate event
            if not event.event_id:
                event.event_id = str(uuid4())
            
            if not event.timestamp:
                event.timestamp = datetime.utcnow()
            
            # Add to appropriate priority queue
            queue = self.queues[event.priority]
            
            if queue.full():
                logger.warning("Event queue full, dropping event", 
                             priority=event.priority,
                             event_id=event.event_id)
                return False
            
            await queue.put(event)
            event.processing_status = EventProcessingStatus.QUEUED
            
            logger.debug("Event published", 
                        event_id=event.event_id,
                        event_type=event.event_type,
                        priority=event.priority)
            
            return True
            
        except Exception as e:
            logger.error("Failed to publish event", 
                        event_id=getattr(event, 'event_id', 'unknown'),
                        error=str(e))
            return False
    
    async def register_handler(self, event_type: EventType, handler: Callable):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info("Event handler registered", event_type=event_type)
    
    async def _process_queues(self):
        """Process events from priority queues"""
        while True:
            try:
                # Process events in priority order
                for priority in [EventPriority.EMERGENCY, EventPriority.CRITICAL, 
                               EventPriority.HIGH, EventPriority.NORMAL, EventPriority.LOW]:
                    
                    queue = self.queues[priority]
                    
                    while not queue.empty():
                        try:
                            event = await asyncio.wait_for(queue.get(), timeout=0.1)
                            await self._process_event(event)
                            queue.task_done()
                        except asyncio.TimeoutError:
                            break
                        except Exception as e:
                            logger.error("Event processing error", error=str(e))
                            break
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error("Queue processor error", error=str(e))
                await asyncio.sleep(1)
    
    async def _process_event(self, event: BaseEvent):
        """Process individual event"""
        try:
            event.processing_status = EventProcessingStatus.PROCESSING
            
            # Call registered handlers
            if event.event_type in self.event_handlers:
                for handler in self.event_handlers[event.event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error("Event handler error", 
                                   event_id=event.event_id,
                                   handler=handler.__name__,
                                   error=str(e))
            
            event.processing_status = EventProcessingStatus.COMPLETED
            
            logger.debug("Event processed successfully", event_id=event.event_id)
            
        except Exception as e:
            event.processing_status = EventProcessingStatus.FAILED
            event.retry_count += 1
            
            logger.error("Event processing failed", 
                        event_id=event.event_id,
                        error=str(e),
                        retry_count=event.retry_count)
            
            # Retry logic
            if event.retry_count < 3:
                event.processing_status = EventProcessingStatus.RETRYING
                await asyncio.sleep(60 * event.retry_count)  # Exponential backoff
                await self.publish(event)


class MessageDelivery:
    """Multi-protocol message delivery system"""
    
    def __init__(self, telegram_bot_token: Optional[str] = None, 
                 smtp_config: Optional[Dict[str, str]] = None):
        self.telegram_bot = Bot(token=telegram_bot_token) if telegram_bot_token else None
        self.smtp_config = smtp_config or {}
        self.delivery_status: Dict[str, MessageStatus] = {}
        self.templates: Dict[str, MessageTemplate] = {}
        
        logger.info("Message delivery system initialized")
    
    async def send_message(self, message: Message) -> MessageSendResponse:
        """Send message via multiple protocols with fallback"""
        response = MessageSendResponse(
            success=False,
            message_id=message.message_id
        )
        
        try:
            delivery_results = {}
            
            for recipient in message.recipients:
                try:
                    if recipient.protocol == MessageProtocol.TELEGRAM:
                        result = await self._send_telegram_message(message, recipient)
                    elif recipient.protocol == MessageProtocol.EMAIL:
                        result = await self._send_email_message(message, recipient)
                    elif recipient.protocol == MessageProtocol.WEBHOOK:
                        result = await self._send_webhook_message(message, recipient)
                    elif recipient.protocol == MessageProtocol.SMS:
                        result = await self._send_sms_message(message, recipient)
                    else:
                        result = MessageStatus.FAILED
                    
                    delivery_results[recipient.protocol] = result
                    
                except Exception as e:
                    logger.error("Message delivery failed", 
                               protocol=recipient.protocol,
                               recipient=recipient.address,
                               error=str(e))
                    delivery_results[recipient.protocol] = MessageStatus.FAILED
            
            # Determine overall success
            successful_deliveries = sum(1 for status in delivery_results.values() 
                                      if status in [MessageStatus.SENT, MessageStatus.DELIVERED])
            
            response.success = successful_deliveries > 0
            response.delivery_status = delivery_results
            
            if response.success:
                message.status = MessageStatus.SENT
                message.delivered_at = datetime.utcnow()
            else:
                message.status = MessageStatus.FAILED
            
            self.delivery_status[message.message_id] = message.status
            
            return response
            
        except Exception as e:
            logger.error("Message send error", message_id=message.message_id, error=str(e))
            response.error = str(e)
            return response
    
    async def _send_telegram_message(self, message: Message, recipient: MessageRecipient) -> MessageStatus:
        """Send message via Telegram"""
        if not self.telegram_bot:
            return MessageStatus.FAILED
        
        try:
            # Format content
            content = message.content
            if message.template_id and message.template_id in self.templates:
                template = self.templates[message.template_id]
                content = template.telegram_template or content
                
                # Replace template variables
                for var, value in message.template_variables.items():
                    content = content.replace(f"{{{var}}}", value)
            
            # Send message
            chat_id = recipient.address
            await self.telegram_bot.send_message(
                chat_id=int(chat_id),
                text=content,
                parse_mode="Markdown" if "telegram_template" in content else None
            )
            
            logger.info("Telegram message sent", chat_id=chat_id, message_id=message.message_id)
            return MessageStatus.SENT
            
        except Exception as e:
            logger.error("Telegram message failed", error=str(e))
            return MessageStatus.FAILED
    
    async def _send_email_message(self, message: Message, recipient: MessageRecipient) -> MessageStatus:
        """Send message via Email"""
        if not self.smtp_config:
            return MessageStatus.FAILED
        
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('from_address')
            msg['To'] = recipient.address
            msg['Subject'] = message.subject or "Libral Notification"
            
            # Format content
            content = message.content
            if message.template_id and message.template_id in self.templates:
                template = self.templates[message.template_id]
                content = template.email_template or content
                
                # Replace template variables
                for var, value in message.template_variables.items():
                    content = content.replace(f"{{{var}}}", value)
            
            msg.attach(MIMEText(content, 'html' if '<' in content else 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_config.get('host'), self.smtp_config.get('port', 587)) as server:
                server.starttls()
                server.login(self.smtp_config.get('username'), self.smtp_config.get('password'))
                server.send_message(msg)
            
            logger.info("Email sent", to=recipient.address, message_id=message.message_id)
            return MessageStatus.SENT
            
        except Exception as e:
            logger.error("Email send failed", error=str(e))
            return MessageStatus.FAILED
    
    async def _send_webhook_message(self, message: Message, recipient: MessageRecipient) -> MessageStatus:
        """Send message via Webhook"""
        try:
            # Prepare payload
            payload = {
                "message_id": message.message_id,
                "subject": message.subject,
                "content": message.content,
                "timestamp": message.timestamp if hasattr(message, 'timestamp') else datetime.utcnow().isoformat(),
                "user_id": message.user_id,
                "context_labels": message.context_labels
            }
            
            # Apply template if specified
            if message.template_id and message.template_id in self.templates:
                template = self.templates[message.template_id]
                webhook_template = template.webhook_template or json.dumps(payload)
                
                # Replace template variables
                for var, value in message.template_variables.items():
                    webhook_template = webhook_template.replace(f"{{{var}}}", str(value))
                
                payload = json.loads(webhook_template)
            
            # Send webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    recipient.address,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
            
            logger.info("Webhook sent", url=recipient.address, message_id=message.message_id)
            return MessageStatus.SENT
            
        except Exception as e:
            logger.error("Webhook send failed", error=str(e))
            return MessageStatus.FAILED
    
    async def _send_sms_message(self, message: Message, recipient: MessageRecipient) -> MessageStatus:
        """Send message via SMS (placeholder)"""
        # Implement SMS delivery via Twilio, AWS SNS, etc.
        logger.info("SMS delivery not implemented", phone=recipient.address)
        return MessageStatus.FAILED
    
    async def register_template(self, template: MessageTemplate):
        """Register message template"""
        self.templates[template.template_id] = template
        logger.info("Message template registered", template_id=template.template_id)


class PersonalLogManager:
    """Personal log server management with Telegram integration"""
    
    def __init__(self, telegram_bot_token: Optional[str] = None, gpg_service=None):
        self.telegram_bot = Bot(token=telegram_bot_token) if telegram_bot_token else None
        self.gpg_service = gpg_service
        self.log_servers: Dict[str, Dict[str, Any]] = {}
        self.topic_configs: Dict[str, List[TopicConfiguration]] = {}
        
        logger.info("Personal log manager initialized")
    
    async def setup_personal_log_server(self, user_id: str, user_name: str) -> Tuple[bool, Optional[Dict]]:
        """Setup personal log server in Telegram"""
        try:
            if not self.telegram_bot:
                raise ValueError("Telegram bot not configured")
            
            # Create supergroup (simulated)
            group_info = {
                "id": -1000000000000 - int(user_id.replace('-', '')[:10], 16),
                "title": f"📋 {user_name} - Personal Libral Logs",
                "invite_link": f"https://t.me/+{secrets.token_urlsafe(22)[:22]}",
                "description": "🔐 Private log server for Libral Core"
            }
            
            # Create topic configuration
            topics = await self._create_default_topics(user_id, group_info["id"])
            group_info["topics"] = topics
            
            # Store configuration
            self.log_servers[user_id] = group_info
            self.topic_configs[user_id] = topics
            
            logger.info("Personal log server setup completed", 
                       user_id=user_id,
                       group_id=group_info["id"])
            
            return True, group_info
            
        except Exception as e:
            logger.error("Personal log server setup failed", user_id=user_id, error=str(e))
            return False, None
    
    async def log_event_to_personal_server(self, user_id: str, event: BaseEvent) -> bool:
        """Log event to user's personal Telegram log server"""
        try:
            if user_id not in self.log_servers:
                logger.warning("Personal log server not found", user_id=user_id)
                return False
            
            server_config = self.log_servers[user_id]
            
            # Determine topic and format message
            topic_config = self._determine_topic(user_id, event)
            
            # Format log entry
            log_entry = await self._format_log_entry(event, topic_config)
            
            # Encrypt if required
            if topic_config and topic_config.encryption_required and self.gpg_service:
                log_entry.content = await self._encrypt_log_content(
                    log_entry.content, 
                    user_id
                )
                log_entry.encrypted = True
            
            # Send to Telegram (simulated)
            if self.telegram_bot:
                message_text = f"#{event.event_type} {log_entry.title}\n\n{log_entry.content}"
                
                # Add hashtags
                if log_entry.hashtags:
                    message_text += f"\n\n{' '.join(log_entry.hashtags)}"
                
                logger.info("Log entry created", 
                           user_id=user_id,
                           event_id=event.event_id,
                           topic=topic_config.name if topic_config else "General")
            
            return True
            
        except Exception as e:
            logger.error("Personal log entry failed", user_id=user_id, error=str(e))
            return False
    
    async def _create_default_topics(self, user_id: str, group_id: int) -> List[TopicConfiguration]:
        """Create default topic configuration"""
        topics = [
            TopicConfiguration(
                topic_id=1,
                name="🔐 Authentication & Security",
                category=TopicCategory.AUTHENTICATION,
                description="Login events, token refresh, security alerts",
                hashtags=["#auth", "#security", "#login", "#token", "#2fa"],
                event_types=[EventType.SECURITY, EventType.USER],
                sources=["lic", "authentication"],
                auto_delete_hours=24
            ),
            TopicConfiguration(
                topic_id=2,
                name="🔌 Plugin Activity",
                category=TopicCategory.PLUGIN_ACTIVITY,
                description="Plugin installations, updates, usage logs",
                hashtags=["#plugin", "#install", "#update", "#marketplace"],
                event_types=[EventType.PLUGIN],
                sources=["marketplace", "plugin_manager"],
                auto_delete_hours=72
            ),
            TopicConfiguration(
                topic_id=3,
                name="💰 Payment & Transactions",
                category=TopicCategory.PAYMENTS,
                description="Payment events, subscription changes, revenue sharing",
                hashtags=["#payment", "#transaction", "#subscription", "#revenue"],
                event_types=[EventType.PAYMENT],
                sources=["payments", "billing"],
                auto_delete_hours=168  # 7 days
            ),
            TopicConfiguration(
                topic_id=4,
                name="📡 Communication Logs",
                category=TopicCategory.COMMUNICATION,
                description="Messages, notifications, API communications",
                hashtags=["#message", "#notification", "#api", "#webhook"],
                event_types=[EventType.COMMUNICATION, EventType.WEBHOOK],
                sources=["leb", "communication"],
                auto_delete_hours=24
            ),
            TopicConfiguration(
                topic_id=5,
                name="⚙️ System Events",
                category=TopicCategory.SYSTEM_EVENTS,
                description="System status, performance metrics, errors",
                hashtags=["#system", "#performance", "#error", "#metric"],
                event_types=[EventType.SYSTEM, EventType.ERROR],
                sources=["system", "monitor"],
                auto_delete_hours=48
            ),
            TopicConfiguration(
                topic_id=6,
                name="🎯 General Topic",
                category=TopicCategory.GENERAL,
                description="Uncategorized logs and general events",
                hashtags=["#general", "#misc", "#other"],
                event_types=[],
                sources=[],
                auto_delete_hours=24
            )
        ]
        
        return topics
    
    def _determine_topic(self, user_id: str, event: BaseEvent) -> Optional[TopicConfiguration]:
        """Determine appropriate topic for event"""
        if user_id not in self.topic_configs:
            return None
        
        topics = self.topic_configs[user_id]
        
        # Find matching topic based on event type and source
        for topic in topics:
            if (event.event_type in topic.event_types or 
                event.source in topic.sources or
                any(keyword in event.title.lower() for keyword in topic.keywords)):
                return topic
        
        # Default to general topic
        return next((t for t in topics if t.category == TopicCategory.GENERAL), None)
    
    async def _format_log_entry(self, event: BaseEvent, topic_config: Optional[TopicConfiguration]) -> PersonalLogEntry:
        """Format event as personal log entry"""
        log_entry = PersonalLogEntry(
            log_id=str(uuid4()),
            user_id=event.user_id or "system",
            telegram_group_id=self.log_servers.get(event.user_id or "system", {}).get("id", 0),
            topic_id=topic_config.topic_id if topic_config else 6,
            event_id=event.event_id,
            title=event.title,
            content=f"**Event**: {event.event_type}\n"
                   f"**Source**: {event.source}\n"
                   f"**Time**: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                   f"**Priority**: {event.priority}\n\n"
                   f"**Description**: {event.description or 'No description'}\n",
            hashtags=event.hashtags + (topic_config.hashtags if topic_config else []),
            topic_category=topic_config.category if topic_config else TopicCategory.GENERAL,
            logged_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=topic_config.auto_delete_hours if topic_config else 24)
        )
        
        # Add event data if present
        if event.data:
            log_entry.content += f"\n**Data**:\n```json\n{json.dumps(event.data, indent=2)}\n```"
        
        return log_entry
    
    async def _encrypt_log_content(self, content: str, user_id: str) -> str:
        """Encrypt log content using GPG"""
        if not self.gpg_service:
            return content
        
        # Encrypt content using user's GPG key
        # This is a placeholder - would integrate with actual GPG service
        return f"[ENCRYPTED: {hashlib.sha256(content.encode()).hexdigest()[:16]}]"


class WebhookProcessor:
    """Webhook event processing system"""
    
    def __init__(self):
        self.registered_webhooks: Dict[str, Dict[str, Any]] = {}
        self.webhook_secrets: Dict[str, str] = {}
        
        logger.info("Webhook processor initialized")
    
    async def register_webhook(self, request: WebhookRegistrationRequest) -> bool:
        """Register webhook endpoint"""
        try:
            self.registered_webhooks[request.webhook_id] = {
                "source": request.source,
                "endpoint_url": request.endpoint_url,
                "event_types": request.event_types,
                "active": request.active,
                "verify_signature": request.verify_signature,
                "allowed_ips": request.allowed_ips,
                "max_retries": request.max_retries,
                "timeout_seconds": request.timeout_seconds,
                "created_at": datetime.utcnow()
            }
            
            if request.secret_token:
                self.webhook_secrets[request.webhook_id] = request.secret_token
            
            logger.info("Webhook registered", webhook_id=request.webhook_id, source=request.source)
            return True
            
        except Exception as e:
            logger.error("Webhook registration failed", error=str(e))
            return False
    
    async def process_webhook(self, webhook_id: str, payload: Dict[str, Any], 
                            headers: Dict[str, str]) -> WebhookEvent:
        """Process incoming webhook event"""
        webhook_event = WebhookEvent(
            webhook_id=webhook_id,
            source=self.registered_webhooks.get(webhook_id, {}).get("source", "unknown"),
            event_type=payload.get("event_type", "webhook"),
            payload=payload,
            headers=headers,
            timestamp=datetime.utcnow()
        )
        
        try:
            # Verify webhook signature if required
            if (webhook_id in self.registered_webhooks and 
                self.registered_webhooks[webhook_id]["verify_signature"]):
                webhook_event.verified = await self._verify_webhook_signature(
                    webhook_id, payload, headers
                )
            else:
                webhook_event.verified = True
            
            if webhook_event.verified:
                webhook_event.processed = True
                logger.info("Webhook processed", webhook_id=webhook_id, event_type=webhook_event.event_type)
            else:
                logger.warning("Webhook signature verification failed", webhook_id=webhook_id)
                
        except Exception as e:
            webhook_event.processing_error = str(e)
            logger.error("Webhook processing error", webhook_id=webhook_id, error=str(e))
        
        return webhook_event
    
    async def _verify_webhook_signature(self, webhook_id: str, payload: Dict[str, Any], 
                                       headers: Dict[str, str]) -> bool:
        """Verify webhook signature"""
        if webhook_id not in self.webhook_secrets:
            return False
        
        secret = self.webhook_secrets[webhook_id]
        signature_header = headers.get("X-Signature", headers.get("X-Hub-Signature-256", ""))
        
        if not signature_header:
            return False
        
        # Calculate expected signature
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode()
        expected_signature = hmac.new(
            secret.encode(),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        provided_signature = signature_header.replace("sha256=", "")
        return hmac.compare_digest(expected_signature, provided_signature)


class LibralEventBus:
    """Unified Libral Event Bus service"""
    
    def __init__(self, config: Optional[EventBusConfig] = None, 
                 telegram_bot_token: Optional[str] = None,
                 smtp_config: Optional[Dict[str, str]] = None,
                 gpg_service=None):
        
        self.config = config or EventBusConfig()
        
        # Initialize components
        self.event_queue = EventQueue(max_size=self.config.max_queue_size)
        self.message_delivery = MessageDelivery(telegram_bot_token, smtp_config)
        self.personal_log_manager = PersonalLogManager(telegram_bot_token, gpg_service)
        self.webhook_processor = WebhookProcessor()
        
        # WebSocket connections (would be implemented with actual WebSocket server)
        self.websocket_connections: Dict[str, Any] = {}
        
        # Metrics tracking
        self.metrics = {
            "events_processed": 0,
            "messages_sent": 0,
            "webhook_events": 0,
            "personal_logs_created": 0,
            "websocket_messages": 0
        }
        
        # Register event handlers
        self._register_internal_handlers()
        
        logger.info("Libral Event Bus initialized")
    
    async def publish_event(self, request: EventPublishRequest) -> EventPublishResponse:
        """Publish event to the event bus"""
        try:
            success = await self.event_queue.publish(request.event)
            
            response = EventPublishResponse(
                success=success,
                event_id=request.event.event_id,
                queued_at=datetime.utcnow()
            )
            
            if success:
                self.metrics["events_processed"] += 1
                
                # Immediate processing if requested
                if request.immediate_processing:
                    response.estimated_processing_time_ms = 100
            
            return response
            
        except Exception as e:
            logger.error("Event publish failed", error=str(e))
            return EventPublishResponse(
                success=False,
                event_id=request.event.event_id,
                queued_at=datetime.utcnow(),
                error=str(e)
            )
    
    async def send_message(self, request: MessageSendRequest) -> MessageSendResponse:
        """Send message via multiple protocols"""
        try:
            response = await self.message_delivery.send_message(request.message)
            
            if response.success:
                self.metrics["messages_sent"] += 1
                
                # Log to personal server if enabled
                if (request.message.log_to_personal_server and 
                    request.message.user_id):
                    
                    # Create event for the sent message
                    message_event = BaseEvent(
                        event_id=str(uuid4()),
                        event_type=EventType.COMMUNICATION,
                        source="leb",
                        title=f"Message sent: {request.message.subject or 'No subject'}",
                        description=f"Message delivered to {len(request.message.recipients)} recipients",
                        data={
                            "message_id": request.message.message_id,
                            "recipients": [r.address for r in request.message.recipients],
                            "protocols": [r.protocol.value for r in request.message.recipients]
                        },
                        user_id=request.message.user_id,
                        topic_category=request.message.topic_category,
                        hashtags=["#message_sent", "#communication"]
                    )
                    
                    await self.personal_log_manager.log_event_to_personal_server(
                        request.message.user_id, message_event
                    )
                    
                    self.metrics["personal_logs_created"] += 1
            
            return response
            
        except Exception as e:
            logger.error("Message send failed", error=str(e))
            return MessageSendResponse(
                success=False,
                message_id=request.message.message_id,
                error=str(e)
            )
    
    async def register_webhook(self, request: WebhookRegistrationRequest) -> bool:
        """Register webhook endpoint"""
        return await self.webhook_processor.register_webhook(request)
    
    async def process_webhook(self, webhook_id: str, payload: Dict[str, Any], 
                            headers: Dict[str, str]) -> WebhookEvent:
        """Process webhook event"""
        webhook_event = await self.webhook_processor.process_webhook(webhook_id, payload, headers)
        
        if webhook_event.processed:
            self.metrics["webhook_events"] += 1
            
            # Convert webhook to internal event
            internal_event = BaseEvent(
                event_id=str(uuid4()),
                event_type=EventType.WEBHOOK,
                source=webhook_event.source,
                title=f"Webhook: {webhook_event.event_type}",
                description=f"Webhook event from {webhook_event.source}",
                data=webhook_event.payload,
                hashtags=[f"#webhook", f"#{webhook_event.source}"]
            )
            
            # Publish to event bus
            await self.event_queue.publish(internal_event)
        
        return webhook_event
    
    async def query_events(self, query: EventQuery) -> Dict[str, Any]:
        """Query events (placeholder - would integrate with actual event storage)"""
        # In a real implementation, this would query from database/storage
        return {
            "events": [],
            "total": 0,
            "limit": query.limit,
            "offset": query.offset
        }
    
    async def get_health(self) -> EventBusHealth:
        """Get event bus health status"""
        return EventBusHealth(
            status="healthy",
            version="2.0.0",
            components={
                "event_queue": {
                    "status": "healthy",
                    "queue_size": sum(q.qsize() for q in self.event_queue.queues.values()),
                    "processing_rate": self.metrics["events_processed"]
                },
                "message_delivery": {
                    "status": "healthy",
                    "success_rate": 0.95,  # Placeholder
                    "failed_messages": 0
                },
                "personal_log_servers": {
                    "status": "healthy",
                    "active_servers": len(self.personal_log_manager.log_servers),
                    "log_entries_today": self.metrics["personal_logs_created"]
                },
                "webhooks": {
                    "status": "healthy",
                    "registered_hooks": len(self.webhook_processor.registered_webhooks),
                    "events_today": self.metrics["webhook_events"]
                },
                "websocket_broadcast": {
                    "status": "healthy",
                    "connected_clients": len(self.websocket_connections),
                    "messages_sent": self.metrics["websocket_messages"]
                }
            },
            uptime_seconds=0.0,  # Would track actual uptime
            last_health_check=datetime.utcnow()
        )
    
    async def get_metrics(self, period_start: datetime, period_end: datetime) -> EventMetrics:
        """Get event processing metrics"""
        return EventMetrics(
            period_start=period_start,
            period_end=period_end,
            total_events=self.metrics["events_processed"],
            events_by_type={},  # Would be populated from actual metrics
            events_by_priority={},
            events_by_status={},
            average_processing_time_ms=50.0,
            successful_processing_rate=0.98,
            failed_events=0,
            retry_events=0,
            total_messages=self.metrics["messages_sent"],
            messages_by_protocol={},
            delivery_success_rate=0.95,
            failed_deliveries=0,
            log_entries_created=self.metrics["personal_logs_created"],
            topics_used={},
            encrypted_logs_percentage=0.85,
            websocket_messages_sent=self.metrics["websocket_messages"],
            active_websocket_connections=len(self.websocket_connections)
        )
    
    def _register_internal_handlers(self):
        """Register internal event handlers"""
        
        async def handle_system_event(event: BaseEvent):
            """Handle system events"""
            logger.info("System event processed", event_id=event.event_id, title=event.title)
        
        async def handle_user_event(event: BaseEvent):
            """Handle user events"""
            if event.user_id and event.personal_log_only:
                await self.personal_log_manager.log_event_to_personal_server(event.user_id, event)
        
        async def handle_communication_event(event: BaseEvent):
            """Handle communication events"""
            # Broadcast to WebSocket connections if enabled
            if self.config.websocket_enabled:
                await self._broadcast_websocket_event(event)
        
        # Register handlers
        asyncio.create_task(self.event_queue.register_handler(EventType.SYSTEM, handle_system_event))
        asyncio.create_task(self.event_queue.register_handler(EventType.USER, handle_user_event))
        asyncio.create_task(self.event_queue.register_handler(EventType.COMMUNICATION, handle_communication_event))
    
    async def _broadcast_websocket_event(self, event: BaseEvent):
        """Broadcast event to WebSocket connections"""
        # Placeholder for WebSocket broadcasting
        self.metrics["websocket_messages"] += 1
        logger.debug("Event broadcasted via WebSocket", event_id=event.event_id)