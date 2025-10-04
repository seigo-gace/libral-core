"""
Event Management FastAPI Router
Real-time event processing and personal server management endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    Event,
    EventCreate,
    EventFilter,
    EventHealthResponse,
    EventResponse,
    PersonalServerAdminRequest,
    PersonalServerAdminResponse,
    SystemMetric
)
from .service import EventService
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/events", tags=["Event Management"])

# Global event service instance
_event_service: Optional[EventService] = None

def get_event_service() -> EventService:
    """Get configured event service instance"""
    global _event_service
    
    if _event_service is None:
        try:
            # Initialize dependencies
            from ..auth.router import get_auth_service
            from ..communication.router import get_communication_service
            
            auth_service = get_auth_service()
            
            # Communication service (optional)
            communication_service = None
            try:
                communication_service = get_communication_service()
            except Exception as e:
                logger.warning("Communication service unavailable for events", error=str(e))
            
            _event_service = EventService(
                auth_service=auth_service,
                communication_service=communication_service,
                telegram_bot_token=settings.telegram_bot_token
            )
            
            logger.info("Event service initialized")
            
        except Exception as e:
            logger.error("Failed to initialize event service", error=str(e))
            raise HTTPException(status_code=500, detail="Event service initialization failed")
    
    return _event_service

@router.get("/health", response_model=EventHealthResponse)
async def health_check(
    service: EventService = Depends(get_event_service)
) -> EventHealthResponse:
    """
    Check event management service health
    
    Returns comprehensive status of event processing:
    - Event processing performance metrics
    - Queue status and backlog information
    - Personal log server integration status
    - System resource utilization
    - Privacy compliance verification
    """
    return await service.health_check()

@router.post("/create", response_model=EventResponse)
async def create_event(
    request: EventCreate,
    background_tasks: BackgroundTasks,
    service: EventService = Depends(get_event_service)
) -> EventResponse:
    """
    Create and process new event
    
    **Real-Time Event Processing:**
    - Events processed asynchronously for high performance
    - Automatic categorization and priority handling
    - Personal log server integration for user events
    - Privacy-compliant event storage with auto-expiry
    
    **Event Categories:**
    - System events (server status, performance metrics)
    - User events (authentication, preferences)
    - Plugin events (installations, updates, usage)
    - Payment events (transactions, subscriptions)
    - Security events (alerts, suspicious activity)
    - Communication events (messages, notifications)
    - Storage events (file operations, capacity)
    - Knowledge base events (content updates, searches)
    
    **Privacy Features:**
    - Personal data flagging and protection
    - User-controlled retention periods (1-365 days)
    - Personal log server integration for audit trails
    - GDPR-compliant event processing
    """
    try:
        result = await service.create_event(request)
        
        # Schedule event cleanup if expiry specified
        if request.expires_at:
            background_tasks.add_task(
                _schedule_event_cleanup,
                service,
                result.event_id,
                request.expires_at
            )
        
        logger.info("Event create request processed",
                   event_id=result.event_id,
                   success=result.success,
                   category=request.category,
                   personal_log=result.personal_log_recorded)
        
        return result
        
    except Exception as e:
        logger.error("Event create endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Event creation failed")

@router.post("/personal-server/button", response_model=PersonalServerAdminResponse)
async def create_personal_server_button(
    request: PersonalServerAdminRequest,
    service: EventService = Depends(get_event_service)
) -> PersonalServerAdminResponse:
    """
    Create personal server admin registration button
    
    **革新的な個人サーバー管理システム:**
    - ワンクリックでTelegramスーパーグループ作成
    - 最小権限でのボット管理者登録
    - データ漏洩防止の完全セキュリティ
    - ユーザー100%データ制御
    
    **サーバータイプ:**
    - **ログサーバー**: プライベートアクティビティログ
    - **ストレージサーバー**: 暗号化ファイルストレージ
    - **ナレッジベース**: 個人知識管理システム
    - **統合サーバー**: 全機能統合型
    
    **最小権限の原則:**
    - トピック管理: ログカテゴリ別組織化
    - メッセージ削除: 期限切れログ自動削除
    - メッセージ固定: 重要情報の表示
    - メンバー制限: ボットアクセス安全管理
    
    **セキュリティ特徴:**
    - GPG暗号化: 軍事レベルの暗号化
    - 自動削除: ユーザー設定期間後削除
    - データ主権: ユーザーのTelegramに100%保存
    - 即座取り消し: いつでも権限取り消し可能
    
    **使用例:**
    ```python
    # ログサーバー + ストレージ + ナレッジベース統合
    request = PersonalServerAdminRequest(
        user_id="user123",
        server_type=PersonalServerType.MIXED,
        enable_storage=True,
        enable_knowledge_base=True,
        storage_limit_mb=1000,
        encryption_required=True
    )
    ```
    """
    try:
        result = await service.create_personal_server_button(request)
        
        logger.info("Personal server button request processed",
                   button_id=result.button_id,
                   success=result.success,
                   server_type=request.server_type,
                   enable_storage=request.enable_storage,
                   enable_kb=request.enable_knowledge_base)
        
        return result
        
    except Exception as e:
        logger.error("Personal server button endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Personal server button creation failed")

@router.get("/list", response_model=List[Event])
async def list_events(
    categories: Optional[str] = None,
    priorities: Optional[str] = None,
    user_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    service: EventService = Depends(get_event_service)
) -> List[Event]:
    """
    List events with filtering (privacy-compliant)
    
    **プライバシー重視のイベント検索:**
    - ユーザーは自分のイベントのみ表示
    - 個人データ保護フィルタリング
    - カテゴリ・優先度での絞り込み
    - 全文検索（タイトル・説明・タグ）
    
    **フィルタリング例:**
    - categories: "system,user,plugin" - カンマ区切りカテゴリ
    - priorities: "high,urgent,critical" - 高優先度のみ
    - search: "auth login" - 認証・ログイン関連
    
    **プライバシー保護:**
    - user_id必須: 指定ユーザーのイベントのみ
    - 個人データ除外: 機密情報フィルタリング
    - 保存期間制限: 期限切れイベント自動除外
    """
    try:
        from .schemas import EventCategory, EventPriority
        
        # Parse comma-separated values
        category_list = []
        if categories:
            try:
                category_list = [EventCategory(cat.strip()) for cat in categories.split(",")]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid category: {e}")
        
        priority_list = []
        if priorities:
            try:
                priority_list = [EventPriority(pri.strip()) for pri in priorities.split(",")]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {e}")
        
        # Create filter
        event_filter = EventFilter(
            categories=category_list,
            priorities=priority_list,
            user_ids=[user_id] if user_id else [],
            search_query=search,
            limit=min(limit, 500),  # Cap at 500 for performance
            offset=max(offset, 0),
            user_owned_only=True    # Privacy: only user's own events
        )
        
        events = await service.get_events(event_filter)
        
        logger.info("Event list request processed",
                   result_count=len(events),
                   categories=len(category_list),
                   user_id=user_id,
                   search_query=bool(search))
        
        return events
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Event list endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Event listing failed")

@router.get("/categories")
async def list_event_categories() -> JSONResponse:
    """
    List available event categories
    
    Returns all supported event categories with descriptions
    and examples for user guidance.
    """
    try:
        from .schemas import EventCategory
        
        categories = [
            {
                "id": category.value,
                "name": category.value.replace("_", " ").title(),
                "description": _get_category_description(category),
                "examples": _get_category_examples(category),
                "icon": _get_category_icon(category),
                "personal_log_topic": _get_category_topic(category)
            }
            for category in EventCategory
        ]
        
        return JSONResponse(content={
            "categories": categories,
            "total_categories": len(categories),
            "privacy_features": [
                "個人ログサーバー統合",
                "カテゴリ別トピック整理",
                "ハッシュタグ自動生成",
                "暗号化イベントストレージ"
            ]
        })
        
    except Exception as e:
        logger.error("Event categories endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list event categories")

@router.get("/metrics/system")
async def get_system_metrics(
    service: EventService = Depends(get_event_service)
) -> List[SystemMetric]:
    """
    Get current system metrics
    
    **リアルタイムシステムメトリクス:**
    - イベント処理パフォーマンス
    - 個人ログサーバー統計
    - システムリソース使用状況
    - プライバシー準拠状況
    """
    try:
        health = await service.health_check()
        
        # Create system metrics from health data
        metrics = [
            SystemMetric(
                metric_id="events_processed_hour",
                metric_name="Events Processed (Last Hour)",
                metric_type="counter",
                value=health.events_processed_last_hour,
                unit="events",
                source="event_processor",
                component="event_management"
            ),
            SystemMetric(
                metric_id="avg_processing_time",
                metric_name="Average Processing Time",
                metric_type="gauge",
                value=health.average_processing_time_ms or 0,
                unit="ms",
                source="event_processor", 
                component="event_management"
            ),
            SystemMetric(
                metric_id="personal_servers_active",
                metric_name="Active Personal Log Servers",
                metric_type="gauge",
                value=health.personal_servers_active,
                unit="servers",
                source="personal_log_manager",
                component="event_management"
            ),
            SystemMetric(
                metric_id="pending_events",
                metric_name="Pending Events",
                metric_type="gauge",
                value=health.pending_events,
                unit="events",
                source="event_queue",
                component="event_management"
            )
        ]
        
        logger.info("System metrics request processed", metrics_count=len(metrics))
        
        return metrics
        
    except Exception as e:
        logger.error("System metrics endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

def _get_category_description(category) -> str:
    """Get human-readable category description"""
    descriptions = {
        "system": "システムイベント - サーバー状態、パフォーマンス、メンテナンス",
        "user": "ユーザーイベント - 認証、設定変更、個人アクティビティ",
        "plugin": "プラグインイベント - インストール、更新、使用状況",
        "payment": "支払いイベント - 取引、サブスクリプション、課金",
        "security": "セキュリティイベント - アラート、不審な活動、認証",
        "communication": "通信イベント - メッセージ、通知、API通信",
        "storage": "ストレージイベント - ファイル操作、容量、バックアップ", 
        "knowledge_base": "ナレッジベースイベント - コンテンツ更新、検索、分類",
        "personal_log": "個人ログイベント - プライベートログ管理、設定"
    }
    return descriptions.get(category.value, "イベントカテゴリ")

def _get_category_examples(category) -> List[str]:
    """Get category examples"""
    examples_map = {
        "system": ["サーバー再起動", "パフォーマンス低下", "メンテナンス開始"],
        "user": ["ログイン成功", "設定変更", "2FA有効化"],
        "plugin": ["プラグインインストール", "バージョンアップデート", "エラー発生"],
        "payment": ["決済完了", "サブスクリプション更新", "返金処理"],
        "security": ["不正ログイン試行", "セキュリティアラート", "権限変更"],
        "communication": ["メッセージ送信", "通知配信", "API呼び出し"],
        "storage": ["ファイルアップロード", "容量警告", "バックアップ完了"],
        "knowledge_base": ["記事追加", "検索実行", "カテゴリ変更"],
        "personal_log": ["ログ設定変更", "保存期間更新", "暗号化有効化"]
    }
    return examples_map.get(category.value, ["一般的なイベント"])

def _get_category_icon(category) -> str:
    """Get category icon emoji"""
    icons = {
        "system": "⚙️",
        "user": "👤", 
        "plugin": "🔌",
        "payment": "💰",
        "security": "🔒",
        "communication": "📡",
        "storage": "💾",
        "knowledge_base": "📚",
        "personal_log": "📋"
    }
    return icons.get(category.value, "📝")

def _get_category_topic(category) -> int:
    """Get topic ID for category"""
    topic_map = {
        "system": 5,        # ⚙️ System Events
        "user": 1,          # 🔐 Authentication & Security
        "plugin": 2,        # 🔌 Plugin Activity
        "payment": 3,       # 💰 Payment & Transactions
        "security": 1,      # 🔐 Authentication & Security
        "communication": 4, # 📡 Communication Logs
        "storage": 6,       # 🎯 General Topic (extended)
        "knowledge_base": 6,# 🎯 General Topic (extended)
        "personal_log": 6   # 🎯 General Topic (extended)
    }
    return topic_map.get(category.value, 6)

async def _schedule_event_cleanup(
    service: EventService,
    event_id: str,
    expires_at
):
    """Schedule event cleanup after expiry"""
    try:
        import asyncio
        from datetime import datetime
        
        # Calculate sleep time
        now = datetime.utcnow()
        if expires_at > now:
            sleep_seconds = (expires_at - now).total_seconds()
            await asyncio.sleep(sleep_seconds)
        
        # Remove expired event
        if event_id in service.processor.events:
            del service.processor.events[event_id]
            logger.info("Expired event cleaned up", event_id=event_id)
            
    except Exception as e:
        logger.error("Event cleanup failed", event_id=event_id, error=str(e))

# Cleanup handler
@router.on_event("startup")
async def startup_event_service():
    """Initialize event service"""
    # Service is lazy-loaded via dependency injection
    pass

@router.on_event("shutdown")
async def cleanup_event_service():
    """Cleanup event service resources"""
    global _event_service
    if _event_service:
        await _event_service.cleanup()
        _event_service = None
        logger.info("Event service cleanup completed")