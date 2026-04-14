"""
Libral APP Module - Standalone FastAPI Application
Privacy-First Application Management System

This is the main entry point for the APP module when running as an independent service.
完全独立したアプリケーション管理モジュール
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
import uvicorn

from . import router
from .schemas import AppConfig
from .service import LibralApp

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

# Global APP service instance
app_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global app_service
    
    # Startup
    logger.info(
        "Libral APP Module starting up",
        version="1.0.0",
        architecture="Privacy-First Application Management",
        features=[
            "Application Registry & Management",
            "PostgreSQL Persistent Storage",
            "Redis High-Performance Caching",
            "Permission-Based Access Control",
            "Analytics & Usage Tracking",
            "Privacy-First Design"
        ]
    )
    
    # Initialize APP service
    database_url = os.getenv("DATABASE_URL", "postgresql://localhost/libral_app")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    config = AppConfig(
        database_url=database_url,
        redis_url=redis_url,
        cache_ttl_hours=int(os.getenv("APP_CACHE_TTL_HOURS", "24")),
        max_apps_per_user=int(os.getenv("APP_MAX_PER_USER", "100")),
        enable_analytics=os.getenv("APP_ENABLE_ANALYTICS", "true").lower() == "true",
        enable_permissions=os.getenv("APP_ENABLE_PERMISSIONS", "true").lower() == "true",
        auto_archive_days=int(os.getenv("APP_AUTO_ARCHIVE_DAYS", "90"))
    )
    
    app_service = LibralApp(config=config)
    await app_service.startup()
    
    # Set service in router module
    router.app_service = app_service
    
    logger.info(
        "Libral APP Module startup completed",
        components=[
            "Database (PostgreSQL)",
            "Cache (Redis)",
            "Application Registry",
            "Permission System",
            "Analytics Engine"
        ],
        features=[
            "Privacy-First Storage",
            "Auto-Archiving",
            "Usage Tracking",
            "Multi-User Support"
        ]
    )
    
    yield
    
    # Shutdown
    logger.info("Libral APP Module shutting down")
    if app_service:
        await app_service.shutdown()

# Create FastAPI application
app = FastAPI(
    title="Libral APP Module - Application Management System",
    description="""
    ## 📱 Libral APP Module - プライバシー優先アプリケーション管理
    
    ### ✨ アプリケーション管理システム
    
    #### 🏗️ 主要機能
    - **アプリケーション登録**: 完全なライフサイクル管理
    - **ステータス管理**: Draft → Active → Paused → Archived
    - **権限制御**: ユーザーベースのアクセス管理
    - **分析機能**: 使用状況の詳細トラッキング
    - **自動アーカイブ**: 非アクティブアプリの自動管理
    
    #### 💾 データストレージ
    - **PostgreSQL**: 永続化データストレージ
    - **Redis**: 高性能キャッシング
    - **プライバシー優先**: 最小限のデータ保持
    - **暗号化対応**: セキュアなデータ管理
    
    #### 🔒 セキュリティ & プライバシー
    - **認証必須**: すべてのエンドポイントで認証
    - **所有者確認**: アプリケーションアクセス制御
    - **監査ログ**: 全操作の追跡
    - **データ主権**: ユーザーが完全にコントロール
    
    #### 📊 アプリケーションタイプ
    - Web Application
    - Mobile Application
    - Desktop Application
    - API Service
    - Plugin/Extension
    - Microservice
    
    ### 🚀 主要エンドポイント
    
    #### Application Management
    - `POST /api/apps/create` - 新規アプリケーション作成
    - `GET /api/apps/{app_id}` - アプリケーション取得
    - `PUT /api/apps/{app_id}` - アプリケーション更新
    - `DELETE /api/apps/{app_id}` - アプリケーション削除
    - `GET /api/apps/` - アプリケーション一覧
    
    #### Quick Operations
    - `POST /api/apps/quick/create` - クイック作成
    - `GET /api/apps/quick/my-apps` - マイアプリ一覧
    
    #### Health & Monitoring
    - `GET /api/apps/health` - システム健全性チェック
    - `GET /api/apps/stats` - 統計情報
    
    ### 🛠️ 開発仕様
    
    - **Framework**: FastAPI + Pydantic V2
    - **Database**: PostgreSQL with AsyncPG
    - **Cache**: Redis with async support
    - **Logging**: Structured logging with privacy
    - **Authentication**: Bearer token authentication
    - **Architecture**: Microservice-ready
    
    ### 📋 使用例
    
    ```bash
    # アプリケーション作成
    curl -X POST "http://localhost:8002/api/apps/quick/create" \\
         -H "Content-Type: application/json" \\
         -H "Authorization: Bearer access_token_user123" \\
         -d '{"name": "My Web App", "app_type": "web"}'
    
    # マイアプリ一覧
    curl -X GET "http://localhost:8002/api/apps/quick/my-apps" \\
         -H "Authorization: Bearer access_token_user123"
    
    # ヘルスチェック
    curl -X GET "http://localhost:8002/api/apps/health"
    ```
    
    🌟 **Libral APP Module**: プライバシーを最優先にしたアプリケーション管理をお試しください！
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, restrict to specific domains
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include the APP router
app.include_router(router.router)

# Health check endpoint for the standalone app
@app.get("/health")
async def health_check():
    """Standalone APP module health check"""
    return {
        "status": "healthy",
        "service": "Libral APP Module",
        "version": "1.0.0",
        "architecture": "Privacy-First Application Management",
        "components": {
            "database": "PostgreSQL",
            "cache": "Redis",
            "app_registry": "Active",
            "permission_system": "Active",
            "analytics": "Active"
        },
        "capabilities": [
            "Application Registry & Management",
            "Multi-User Support",
            "Permission-Based Access Control",
            "Usage Analytics",
            "Auto-Archiving",
            "Privacy-First Design"
        ]
    }

# System information endpoint
@app.get("/info")
async def system_info():
    """Get APP module system information"""
    return {
        "libral_app_module": {
            "name": "Libral APP Module",
            "version": "1.0.0",
            "architecture": "Privacy-First Application Management",
            "status": "operational"
        },
        "features": {
            "application_types": ["web", "mobile", "desktop", "api", "plugin", "microservice"],
            "status_lifecycle": ["draft", "active", "paused", "archived", "deleted"],
            "permissions": ["read", "write", "admin", "owner"],
            "storage": {
                "database": "PostgreSQL (persistent)",
                "cache": "Redis (high-performance)",
                "encryption": "supported"
            }
        },
        "privacy_model": [
            "User data sovereignty",
            "Minimal data retention",
            "Auto-archiving",
            "Audit logging",
            "Privacy-first design"
        ]
    }

# Configuration endpoint  
@app.get("/config")
async def get_configuration():
    """Get APP module configuration"""
    return {
        "app_configuration": {
            "max_apps_per_user": os.getenv("APP_MAX_PER_USER", "100"),
            "cache_ttl_hours": os.getenv("APP_CACHE_TTL_HOURS", "24"),
            "auto_archive_days": os.getenv("APP_AUTO_ARCHIVE_DAYS", "90"),
            "enable_analytics": os.getenv("APP_ENABLE_ANALYTICS", "true"),
            "enable_permissions": os.getenv("APP_ENABLE_PERMISSIONS", "true")
        },
        "storage": {
            "database": "PostgreSQL with connection pooling",
            "cache": "Redis with TTL support",
            "backup": "Supported"
        }
    }

# Development server configuration
if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8002"))
    reload = os.getenv("APP_RELOAD", "true").lower() == "true"
    log_level = os.getenv("APP_LOG_LEVEL", "info").lower()
    
    print(f"""
📱 Libral APP Module - Application Management System Starting...

🏗️ Application Registry: Full lifecycle management
💾 Storage: PostgreSQL + Redis
🔒 Security: Permission-based access control
📊 Analytics: Usage tracking and statistics
🗂️ Auto-Archive: Automatic cleanup after {os.getenv("APP_AUTO_ARCHIVE_DAYS", "90")} days

Server Configuration:
- Host: {host}
- Port: {port}
- Reload: {reload}
- Log Level: {log_level}

API Documentation: http://{host}:{port}/docs
Health Check: http://{host}:{port}/health
System Info: http://{host}:{port}/info
""")
    
    uvicorn.run(
        "libral_core.modules.app.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )
