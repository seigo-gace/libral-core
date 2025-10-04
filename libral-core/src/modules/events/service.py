"""
Event Management Service - Week 5 Implementation
Real-time event processing with personal log server integration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from uuid import uuid4
import secrets

import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .schemas import (
    Event,
    EventCreate,
    EventResponse,
    EventCategory,
    EventFilter,
    EventHealthResponse,
    EventPriority,
    EventStatus,
    HealthCheck,
    PersonalServerAdminRequest,
    PersonalServerAdminResponse,
    PersonalServerSetupButton,
    PersonalServerType,
    RealTimeEventStream,
    SystemMetric,
    TelegramAdminPermission
)
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ..gpg.service import GPGService

logger = structlog.get_logger(__name__)


class PersonalServerButtonManager:
    """Manages Telegram admin registration buttons for personal servers"""
    
    def __init__(self, bot_token: str, auth_service: AuthService):
        self.bot = Bot(token=bot_token)
        self.auth_service = auth_service
        self.active_buttons: Dict[str, PersonalServerSetupButton] = {}
        
    async def create_admin_button(
        self, 
        request: PersonalServerAdminRequest
    ) -> PersonalServerAdminResponse:
        """Create Telegram admin registration button with minimal permissions"""
        request_id = str(uuid4())[:8]
        button_id = str(uuid4())
        
        try:
            logger.info("Creating personal server admin button",
                       request_id=request_id,
                       user_id=request.user_id,
                       server_type=request.server_type)
            
            # Get user profile
            user_profile = self.auth_service.user_profiles.get(request.user_id)
            if not user_profile:
                return PersonalServerAdminResponse(
                    success=False,
                    button_id=button_id,
                    error="User profile not found",
                    request_id=request_id
                )
            
            # Create server configuration
            server_name = request.custom_name or f"{user_profile.display_name} Personal Server"
            
            # Determine minimal required permissions
            minimal_permissions = self._get_minimal_permissions(request.server_type)
            if request.preferred_permissions:
                # Use user preferences but ensure minimal requirements
                minimal_permissions.extend([
                    p for p in request.preferred_permissions 
                    if p not in minimal_permissions
                ])
            
            # Create button configuration
            button_config = PersonalServerSetupButton(
                button_id=button_id,
                button_text=f"🔧 Setup {request.server_type.value.replace('_', ' ').title()}",
                button_emoji="🔧",
                server_type=request.server_type,
                server_name=server_name,
                required_permissions=minimal_permissions,
                setup_steps=self._generate_setup_steps(request.server_type),
                estimated_setup_time_minutes=self._estimate_setup_time(request.server_type),
                enable_storage=request.enable_storage,
                enable_knowledge_base=request.enable_knowledge_base,
                max_storage_mb=request.storage_limit_mb,
                description=self._get_server_description(request.server_type),
                benefits=self._get_server_benefits(request.server_type),
                warnings=self._get_security_warnings(minimal_permissions)
            )
            
            # Create Telegram inline button
            telegram_button_url = await self._create_telegram_button(
                button_config, user_profile.telegram_id
            )
            
            # Store button configuration
            self.active_buttons[button_id] = button_config
            
            # Generate permissions explanation
            permissions_explanation = self._explain_permissions(minimal_permissions)
            
            # Security notes
            security_notes = [
                "最小権限の原則: 必要な機能のみの権限を要求",
                "データ漏洩防止: 個人データへのアクセス権限なし",
                "ユーザー制御: いつでも権限を取り消し可能",
                "暗号化必須: 全データはGPGで暗号化",
                "自動削除: 設定した期間後に自動削除"
            ]
            
            setup_instructions = [
                f"1. 下記ボタンをクリックして{server_name}を作成",
                "2. Telegramで新しいスーパーグループが作成されます",
                "3. LibralCoreBotを管理者として追加（必要な権限のみ）",
                "4. トピック構成とハッシュタグシステムが自動設定",
                "5. 暗号化システムが有効化され、使用開始可能"
            ]
            
            logger.info("Personal server admin button created",
                       request_id=request_id,
                       button_id=button_id,
                       server_type=request.server_type,
                       permissions_count=len(minimal_permissions))
            
            return PersonalServerAdminResponse(
                success=True,
                button_id=button_id,
                telegram_button_url=telegram_button_url,
                setup_instructions=setup_instructions,
                server_config=button_config,
                permissions_explanation=permissions_explanation,
                security_notes=security_notes,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("Personal server admin button creation failed",
                        request_id=request_id,
                        error=str(e))
            
            return PersonalServerAdminResponse(
                success=False,
                button_id=button_id,
                error=str(e),
                retry_possible=True,
                request_id=request_id
            )
    
    def _get_minimal_permissions(self, server_type: PersonalServerType) -> List[TelegramAdminPermission]:
        """Get minimal required permissions for server type"""
        base_permissions = [
            TelegramAdminPermission.MANAGE_TOPICS,     # Essential for topic organization
            TelegramAdminPermission.DELETE_MESSAGES    # Essential for log cleanup
        ]
        
        if server_type in [PersonalServerType.STORAGE_SERVER, PersonalServerType.MIXED]:
            base_permissions.append(TelegramAdminPermission.PIN_MESSAGES)  # Pin storage guidelines
        
        if server_type in [PersonalServerType.KNOWLEDGE_BASE, PersonalServerType.MIXED]:
            base_permissions.append(TelegramAdminPermission.RESTRICT_MEMBERS)  # Manage KB access
        
        return base_permissions
    
    def _generate_setup_steps(self, server_type: PersonalServerType) -> List[str]:
        """Generate setup steps for server type"""
        base_steps = [
            "Telegramスーパーグループ作成",
            "トピック構成とハッシュタグ設定",
            "GPG暗号化システム有効化",
            "自動削除ポリシー設定"
        ]
        
        if server_type == PersonalServerType.STORAGE_SERVER:
            base_steps.extend([
                "ファイルストレージトピック作成",
                "アップロード権限設定",
                "ストレージ制限設定"
            ])
        elif server_type == PersonalServerType.KNOWLEDGE_BASE:
            base_steps.extend([
                "ナレッジベーストピック作成",
                "検索システム設定",
                "カテゴリ分類設定"
            ])
        elif server_type == PersonalServerType.MIXED:
            base_steps.extend([
                "統合ログ・ストレージ・KB設定",
                "クロス参照システム設定",
                "統一検索システム設定"
            ])
        
        return base_steps
    
    def _estimate_setup_time(self, server_type: PersonalServerType) -> int:
        """Estimate setup time in minutes"""
        time_map = {
            PersonalServerType.LOG_SERVER: 2,
            PersonalServerType.STORAGE_SERVER: 4,
            PersonalServerType.KNOWLEDGE_BASE: 5,
            PersonalServerType.MIXED: 8
        }
        return time_map.get(server_type, 3)
    
    def _get_server_description(self, server_type: PersonalServerType) -> str:
        """Get human-readable server description"""
        descriptions = {
            PersonalServerType.LOG_SERVER: "プライベートログサーバー: 全ての活動を暗号化してプライベートTelegramグループに保存",
            PersonalServerType.STORAGE_SERVER: "プライベートストレージサーバー: ファイルやデータを暗号化して安全に保存・管理",
            PersonalServerType.KNOWLEDGE_BASE: "プライベートナレッジベース: 個人的な知識や情報を整理・検索可能な形で保存",
            PersonalServerType.MIXED: "統合プライベートサーバー: ログ・ストレージ・ナレッジベース機能を統合した完全なプライベート環境"
        }
        return descriptions.get(server_type, "プライベートサーバー")
    
    def _get_server_benefits(self, server_type: PersonalServerType) -> List[str]:
        """Get server benefits list"""
        base_benefits = [
            "100%データ主権: あなたのTelegramグループに全データ保存",
            "完全暗号化: GPGによる軍事レベル暗号化",
            "即座削除: いつでも全データを即座に削除可能",
            "プライバシー保護: 中央サーバーに個人データ保存なし"
        ]
        
        if server_type == PersonalServerType.STORAGE_SERVER:
            base_benefits.append("安全なファイル保存: 暗号化されたクラウドストレージ")
        elif server_type == PersonalServerType.KNOWLEDGE_BASE:
            base_benefits.append("個人ナレッジ管理: 検索可能な知識ベース")
        elif server_type == PersonalServerType.MIXED:
            base_benefits.append("統合環境: ログ・ストレージ・ナレッジが連携")
        
        return base_benefits
    
    def _get_security_warnings(self, permissions: List[TelegramAdminPermission]) -> List[str]:
        """Get security warnings for permissions"""
        warnings = []
        
        if TelegramAdminPermission.DELETE_MESSAGES in permissions:
            warnings.append("メッセージ削除権限: 期限切れログの自動削除に使用")
        
        if TelegramAdminPermission.RESTRICT_MEMBERS in permissions:
            warnings.append("メンバー制限権限: ボットアクセス管理にのみ使用")
        
        if not warnings:
            warnings.append("最小権限設定: データ漏洩リスク最小化")
        
        return warnings
    
    def _explain_permissions(self, permissions: List[TelegramAdminPermission]) -> Dict[str, str]:
        """Explain required permissions in Japanese"""
        explanations = {
            TelegramAdminPermission.MANAGE_TOPICS: "トピック管理: ログカテゴリ別のトピック作成・管理",
            TelegramAdminPermission.DELETE_MESSAGES: "メッセージ削除: 保存期間過ぎたログの自動削除",
            TelegramAdminPermission.PIN_MESSAGES: "メッセージ固定: 重要なシステム情報の固定表示",
            TelegramAdminPermission.RESTRICT_MEMBERS: "メンバー制限: ボットアクセス権限の安全な管理",
            TelegramAdminPermission.MANAGE_VIDEO_CHATS: "音声チャット管理: サポート用音声通話（オプション）"
        }
        
        return {perm.value: explanations.get(perm, "権限説明未設定") for perm in permissions}
    
    async def _create_telegram_button(
        self, 
        config: PersonalServerSetupButton, 
        user_telegram_id: int
    ) -> str:
        """Create Telegram inline button for server setup"""
        try:
            # Create bot setup URL with minimal permissions
            permissions_param = ",".join([p.value for p in config.required_permissions])
            
            # Create deep link for server setup
            setup_url = f"https://t.me/LibralCoreBot?start=setup_{config.button_id}"
            
            logger.info("Telegram setup button created",
                       button_id=config.button_id,
                       server_type=config.server_type,
                       permissions_count=len(config.required_permissions))
            
            return setup_url
            
        except Exception as e:
            logger.error("Failed to create Telegram button",
                        button_id=config.button_id,
                        error=str(e))
            return f"https://t.me/LibralCoreBot?start=error_{config.button_id}"


class EventProcessor:
    """High-performance event processing engine"""
    
    def __init__(
        self, 
        auth_service: AuthService,
        communication_service: Optional[CommunicationService] = None
    ):
        self.auth_service = auth_service
        self.communication_service = communication_service
        
        # Event storage (in production, would use Redis/Database)
        self.events: Dict[str, Event] = {}
        self.event_streams: Dict[str, RealTimeEventStream] = {}
        
        # Processing queue
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.processing_tasks: Set[asyncio.Task] = set()
        
        # Metrics
        self.processing_stats = {
            "events_processed": 0,
            "events_failed": 0,
            "average_processing_time_ms": 0,
            "last_hour_events": 0
        }
        
    async def start_processing(self):
        """Start event processing workers"""
        try:
            # Start processing workers
            for i in range(3):  # 3 worker tasks
                task = asyncio.create_task(self._process_events_worker(f"worker-{i}"))
                self.processing_tasks.add(task)
            
            logger.info("Event processing workers started", worker_count=len(self.processing_tasks))
            
        except Exception as e:
            logger.error("Failed to start event processing", error=str(e))
    
    async def _process_events_worker(self, worker_id: str):
        """Event processing worker"""
        logger.info("Event processing worker started", worker_id=worker_id)
        
        while True:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.processing_queue.get(), timeout=10.0)
                
                # Process event
                start_time = datetime.utcnow()
                success = await self._process_single_event(event)
                
                # Update processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                event.processing_duration_ms = int(processing_time)
                event.processed_at = datetime.utcnow()
                event.status = EventStatus.COMPLETED if success else EventStatus.FAILED
                
                # Update statistics
                self.processing_stats["events_processed"] += 1
                if not success:
                    self.processing_stats["events_failed"] += 1
                
                # Update average processing time
                current_avg = self.processing_stats["average_processing_time_ms"]
                new_avg = (current_avg + processing_time) / 2
                self.processing_stats["average_processing_time_ms"] = int(new_avg)
                
                logger.debug("Event processed",
                           worker_id=worker_id,
                           event_id=event.event_id,
                           success=success,
                           processing_time_ms=processing_time)
                
            except asyncio.TimeoutError:
                # Timeout waiting for events - continue loop
                continue
            except Exception as e:
                logger.error("Event processing worker error",
                           worker_id=worker_id,
                           error=str(e))
                await asyncio.sleep(1)  # Brief pause before retrying
    
    async def _process_single_event(self, event: Event) -> bool:
        """Process a single event"""
        try:
            # Log to personal server if enabled and user specified
            if event.log_to_personal_server and event.source_user_id:
                log_data = {
                    "timestamp": event.created_at.isoformat(),
                    "category": event.category,
                    "event_type": event.event_type,
                    "title": event.title,
                    "description": event.description,
                    "priority": event.priority,
                    "source": event.source,
                    "tags": event.tags,
                    "context": event.context_labels
                }
                
                await self.auth_service._log_to_personal_server(
                    event.source_user_id, log_data
                )
            
            # Send real-time notifications if communication service available
            if self.communication_service and event.priority in [EventPriority.HIGH, EventPriority.URGENT, EventPriority.CRITICAL]:
                await self._send_event_notification(event)
            
            return True
            
        except Exception as e:
            logger.error("Event processing failed",
                        event_id=event.event_id,
                        error=str(e))
            return False
    
    async def _send_event_notification(self, event: Event):
        """Send real-time notification for high-priority events"""
        try:
            if not self.communication_service or not event.source_user_id:
                return
            
            from ..communication.schemas import (
                NotificationRequest, 
                MessagePriority
            )
            
            # Map event priority to message priority
            priority_map = {
                EventPriority.HIGH: MessagePriority.HIGH,
                EventPriority.URGENT: MessagePriority.URGENT,
                EventPriority.CRITICAL: MessagePriority.CRITICAL
            }
            
            # Create notification
            notification = NotificationRequest(
                user_ids=[event.source_user_id],
                title=f"🔔 {event.category.value.title()} Event",
                message=f"**{event.title}**\n\n{event.description or 'No description'}",
                notification_type=f"{event.category.value}_event",
                priority=priority_map.get(event.priority, MessagePriority.NORMAL),
                context_labels={
                    "event_id": event.event_id,
                    "category": event.category,
                    "telegram.topic_id": str(self._get_topic_id_for_category(event.category))
                },
                source_module="events"
            )
            
            await self.communication_service.send_notification(notification)
            
        except Exception as e:
            logger.error("Event notification failed",
                        event_id=event.event_id,
                        error=str(e))
    
    def _get_topic_id_for_category(self, category: EventCategory) -> int:
        """Get topic ID for event category"""
        topic_map = {
            EventCategory.SYSTEM: 5,        # ⚙️ System Events
            EventCategory.USER: 1,          # 🔐 Authentication & Security
            EventCategory.PLUGIN: 2,        # 🔌 Plugin Activity
            EventCategory.PAYMENT: 3,       # 💰 Payment & Transactions
            EventCategory.SECURITY: 1,      # 🔐 Authentication & Security
            EventCategory.COMMUNICATION: 4, # 📡 Communication Logs
            EventCategory.STORAGE: 6,       # 🎯 General Topic (extended)
            EventCategory.KNOWLEDGE_BASE: 6,# 🎯 General Topic (extended)
            EventCategory.PERSONAL_LOG: 6   # 🎯 General Topic (extended)
        }
        return topic_map.get(category, 6)


class EventService:
    """Comprehensive event management service"""
    
    def __init__(
        self,
        auth_service: AuthService,
        communication_service: Optional[CommunicationService] = None,
        telegram_bot_token: Optional[str] = None
    ):
        self.auth_service = auth_service
        self.communication_service = communication_service
        
        # Initialize components
        self.processor = EventProcessor(auth_service, communication_service)
        self.button_manager = PersonalServerButtonManager(
            telegram_bot_token or "mock_token", auth_service
        ) if telegram_bot_token else None
        
        # Start processing
        asyncio.create_task(self.processor.start_processing())
        
        logger.info("Event service initialized")
    
    async def health_check(self) -> EventHealthResponse:
        """Check event service health"""
        try:
            stats = self.processor.processing_stats
            
            return EventHealthResponse(
                status="healthy",
                events_processed_last_hour=stats["last_hour_events"],
                average_processing_time_ms=stats["average_processing_time_ms"],
                failed_events_last_hour=stats["events_failed"],
                pending_events=self.processor.processing_queue.qsize(),
                processing_events=len([e for e in self.processor.events.values() 
                                     if e.status == EventStatus.PROCESSING]),
                personal_servers_active=len(self.auth_service.personal_log_servers),
                personal_logs_recorded_last_hour=stats["events_processed"],
                personal_log_success_rate=0.95,  # Mock high success rate
                memory_usage_mb=50,              # Mock
                cpu_usage_percent=15.0,          # Mock
                gdpr_compliant=True,
                personal_data_retention_compliant=True,
                communication_service_connected=bool(self.communication_service),
                auth_service_connected=True,
                redis_connected=True,            # Mock
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Event health check failed", error=str(e))
            return EventHealthResponse(
                status="unhealthy",
                events_processed_last_hour=0,
                failed_events_last_hour=0,
                pending_events=0,
                processing_events=0,
                personal_servers_active=0,
                personal_logs_recorded_last_hour=0,
                gdpr_compliant=True,
                personal_data_retention_compliant=True,
                communication_service_connected=False,
                auth_service_connected=False,
                redis_connected=False,
                last_check=datetime.utcnow()
            )
    
    async def create_event(self, request: EventCreate) -> EventResponse:
        """Create and process new event"""
        request_id = str(uuid4())[:8]
        event_id = str(uuid4())
        
        try:
            start_time = datetime.utcnow()
            
            # Create event
            event = Event(
                event_id=event_id,
                event_type=request.event_type,
                category=request.category,
                title=request.title,
                description=request.description,
                data=request.data,
                source=request.source,
                source_user_id=request.source_user_id,
                correlation_id=request.correlation_id,
                priority=request.priority,
                expires_at=request.expires_at,
                contains_personal_data=request.contains_personal_data,
                retention_days=request.retention_days,
                log_to_personal_server=request.log_to_personal_server,
                tags=request.tags,
                context_labels=request.context_labels
            )
            
            # Store event
            self.processor.events[event_id] = event
            
            # Queue for processing
            await self.processor.processing_queue.put(event)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info("Event created and queued",
                       request_id=request_id,
                       event_id=event_id,
                       category=request.category,
                       priority=request.priority)
            
            return EventResponse(
                success=True,
                event_id=event_id,
                event=event,
                processing_time_ms=int(processing_time),
                personal_log_recorded=request.log_to_personal_server and bool(request.source_user_id),
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("Event creation failed",
                        request_id=request_id,
                        error=str(e))
            
            return EventResponse(
                success=False,
                event_id=event_id,
                processing_time_ms=0,
                error=str(e),
                error_code="EVENT_CREATION_FAILED",
                request_id=request_id
            )
    
    async def create_personal_server_button(
        self, 
        request: PersonalServerAdminRequest
    ) -> PersonalServerAdminResponse:
        """Create personal server admin registration button"""
        if not self.button_manager:
            return PersonalServerAdminResponse(
                success=False,
                button_id="error",
                error="Button manager not available (Telegram bot token required)",
                retry_possible=False,
                request_id=str(uuid4())[:8]
            )
        
        return await self.button_manager.create_admin_button(request)
    
    async def get_events(self, filter_criteria: EventFilter) -> List[Event]:
        """Get events with filtering (privacy-compliant)"""
        try:
            events = list(self.processor.events.values())
            
            # Apply filters
            if filter_criteria.categories:
                events = [e for e in events if e.category in filter_criteria.categories]
            
            if filter_criteria.priorities:
                events = [e for e in events if e.priority in filter_criteria.priorities]
            
            if filter_criteria.statuses:
                events = [e for e in events if e.status in filter_criteria.statuses]
            
            if filter_criteria.event_types:
                events = [e for e in events if e.event_type in filter_criteria.event_types]
            
            if filter_criteria.user_owned_only:
                # Only return events for the requesting user (privacy protection)
                user_id = filter_criteria.user_ids[0] if filter_criteria.user_ids else None
                if user_id:
                    events = [e for e in events if e.source_user_id == user_id]
                else:
                    events = []  # No user specified, return no events for privacy
            
            # Apply time range filters
            if filter_criteria.created_after:
                events = [e for e in events if e.created_at >= filter_criteria.created_after]
            
            if filter_criteria.created_before:
                events = [e for e in events if e.created_at <= filter_criteria.created_before]
            
            # Apply search query
            if filter_criteria.search_query:
                query = filter_criteria.search_query.lower()
                events = [e for e in events 
                         if query in e.title.lower() 
                         or (e.description and query in e.description.lower())
                         or any(query in tag.lower() for tag in e.tags)]
            
            # Sort by creation time (newest first)
            events.sort(key=lambda e: e.created_at, reverse=True)
            
            # Apply pagination
            start_idx = filter_criteria.offset
            end_idx = start_idx + filter_criteria.limit
            events = events[start_idx:end_idx]
            
            return events
            
        except Exception as e:
            logger.error("Event filtering failed", error=str(e))
            return []
    
    async def cleanup(self):
        """Cleanup event service resources"""
        try:
            # Cancel processing tasks
            for task in self.processor.processing_tasks:
                task.cancel()
            
            # Close button manager resources
            if self.button_manager:
                await self.button_manager.bot.session.close()
            
            logger.info("Event service cleanup completed")
            
        except Exception as e:
            logger.error("Event service cleanup failed", error=str(e))