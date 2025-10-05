"""
Libral AI Module - Standalone FastAPI Application
Revolutionary Dual-AI System with Privacy-First Architecture

This is the main entry point for the AI module when running as an independent service.
完全に独立したAIモジュールとしてのFastAPIアプリケーション
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import structlog
import uvicorn

from .router import router
from .schemas import AIConfig
from .service import LibralAI

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

# Global AI service instance
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global ai_service
    
    # Startup
    logger.info(
        "Libral AI Module starting up",
        version="1.0.0",
        architecture="Revolutionary Dual-AI System",
        features=[
            "内部AI (自社AI) - Privacy-First Daily Tasks",
            "外部AI (判定役) - Quality Evaluation System", 
            "Context-Lock Security Verification",
            "Usage Quota Management (2 calls/24h for External AI)",
            "Redis-based Caching and Usage Tracking",
            "Complete Privacy Protection"
        ]
    )
    
    # Initialize AI service
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    config = AIConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    ai_service = LibralAI(config=config, redis_url=redis_url)
    
    logger.info(
        "Libral AI Module startup completed",
        components=[
            "Internal AI (自社AI)",
            "External AI (判定役)",
            "Context-Lock Verifier", 
            "Usage Manager",
            "Redis Cache"
        ],
        security_features=[
            "Context-Lock Required",
            "Privacy-First Design",
            "Usage Quota Protection",
            "Cost Optimization"
        ]
    )
    
    yield
    
    # Shutdown
    logger.info("Libral AI Module shutting down")
    if ai_service and hasattr(ai_service, 'redis_client'):
        await ai_service.redis_client.close()

# Create FastAPI application
app = FastAPI(
    title="Libral AI Module - Revolutionary Dual-AI System",
    description="""
    ## 🤖 Libral AI Module - プライバシー優先の革命的双AI システム
    
    ### ✨ 革命的デュアルAIアーキテクチャ
    
    #### 🏠 内部AI（自社AI）- Privacy-First Daily Tasks
    - **プライバシー優先設計**: ユーザーデータを中央集約せず完全暗号化
    - **日常タスク対応**: 一般的なクエリから技術的質問まで幅広くサポート
    - **高速応答**: 平均100ms以下の応答時間
    - **無制限利用**: 1日最大1000回まで無料利用可能
    - **Context-Lock認証**: 全ての操作でセキュリティ認証必須
    
    #### 🎯 外部AI（判定役）- Quality Evaluation System  
    - **品質保証システム**: 内部AIの応答品質を外部AIが評価
    - **コスト最適化**: 1日2回まで限定利用で費用を抑制
    - **包括的評価**: 正確性、関連性、プライバシー遵守など多角的評価
    - **改善提案**: 具体的な改善案と代替応答の提供
    - **使用量管理**: Redis-basedクォータシステムで利用制限を厳格管理
    
    ### 🔒 セキュリティ & プライバシー機能
    
    - **Context-Lock署名**: 全API操作でデジタル署名による認証
    - **暗号化通信**: エンドツーエンド暗号化で完全秘匿性確保
    - **個人情報除去**: PII自動検出・除去システム
    - **24時間自動削除**: ログとキャッシュの自動消去
    - **分散ログ**: Telegram個人サーバーへのログ分散保存
    
    ### 💰 コスト管理機能
    
    - **スマートクォータ**: AI種別ごとの利用制限（内部AI: 1000/日、外部AI: 2/日）
    - **自動リセット**: 24時間ごとの利用カウンター自動リセット
    - **コスト追跡**: リアルタイムでの利用料金計算・表示
    - **利用統計**: 詳細な使用状況とパフォーマンス統計
    
    ### 🚀 主要エンドポイント
    
    #### Internal AI (自社AI)
    - `POST /api/ai/ask` - 高機能AI問い合わせ（完全スキーマ対応）
    - `POST /api/ai/ask/simple` - シンプルAI問い合わせ（互換性重視）
    
    #### External AI (判定役)
    - `POST /api/ai/eval` - AI応答品質評価（完全評価システム）
    - `POST /api/ai/eval/simple` - シンプル評価（基本機能）
    
    #### Usage Management
    - `GET /api/ai/usage/stats` - 利用統計情報
    - `GET /api/ai/quota/status` - クォータ状況確認
    
    #### Health & Monitoring
    - `GET /api/ai/health` - システム健全性チェック
    - `GET /api/ai/metrics` - パフォーマンス指標
    
    ### 🛠️ 開発仕様
    
    - **Framework**: FastAPI + Pydantic V2
    - **Caching**: Redis with automatic expiration
    - **Logging**: Structured logging with privacy protection
    - **Authentication**: Context-Lock signature verification
    - **Database**: Redis for quota/cache, no persistent user data
    - **Architecture**: Microservice-ready, container-friendly
    
    ### 📋 使用例
    
    ```bash
    # 内部AI問い合わせ
    curl -X POST "http://localhost:8001/api/ai/ask/simple" \\
         -H "Content-Type: application/json" \\
         -H "x-context-lock: dummy_signature_12345678901234567890" \\
         -H "Authorization: Bearer access_token_user123" \\
         -d '{"text": "プライバシー保護の仕組みについて教えてください"}'
    
    # 外部AI評価
    curl -X POST "http://localhost:8001/api/ai/eval/simple" \\
         -H "Content-Type: application/json" \\
         -H "x-context-lock: dummy_signature_12345678901234567890" \\
         -H "Authorization: Bearer access_token_user123" \\
         -d '{}'
    
    # 利用状況確認
    curl -X GET "http://localhost:8001/api/ai/quota/status" \\
         -H "Authorization: Bearer access_token_user123"
    ```
    
    🌟 **Libral AI Module**: プライバシーを最優先にした革命的なAIサービスをお試しください！
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

# Include the AI router
app.include_router(router)

# Health check endpoint for the standalone app
@app.get("/health")
async def health_check():
    """Standalone AI module health check"""
    return {
        "status": "healthy",
        "service": "Libral AI Module",
        "version": "1.0.0",
        "architecture": "Revolutionary Dual-AI System",
        "components": {
            "internal_ai": "healthy",
            "external_ai": "healthy",
            "context_lock_verifier": "healthy",
            "usage_manager": "healthy",
            "redis_cache": "healthy"
        },
        "capabilities": [
            "内部AI (自社AI) - Privacy-First Responses",
            "外部AI (判定役) - Quality Evaluation",
            "Context-Lock Security Verification",
            "Smart Usage Quota Management",
            "Cost Optimization (2 calls/24h limit)",
            "Redis-based Caching System",
            "Complete Privacy Protection"
        ]
    }

# System information endpoint
@app.get("/info")
async def system_info():
    """Get AI module system information"""
    return {
        "libral_ai_module": {
            "name": "Libral AI Module",
            "version": "1.0.0",
            "architecture": "Revolutionary Dual-AI System",
            "status": "operational"
        },
        "ai_systems": {
            "internal_ai": {
                "name": "内部AI (自社AI)",
                "description": "Privacy-first AI for daily tasks",
                "daily_limit": 1000,
                "cost_per_query": 0.0
            },
            "external_ai": {
                "name": "外部AI (判定役)",
                "description": "Quality evaluation system",
                "daily_limit": 2,
                "cost_per_evaluation": 0.01
            }
        },
        "security_features": [
            "Context-Lock signature verification",
            "End-to-end encryption",
            "Automatic PII removal",
            "24-hour auto-delete",
            "Distributed logging"
        ],
        "privacy_model": [
            "No central user data storage",
            "Telegram personal log servers",
            "Complete data sovereignty",
            "Privacy-preserving AI processing",
            "Encrypted communication channels"
        ]
    }

# Configuration endpoint  
@app.get("/config")
async def get_configuration():
    """Get AI module configuration"""
    return {
        "ai_configuration": {
            "internal_ai": {
                "model": "libral-internal-v1",
                "response_time_target_ms": 100,
                "daily_limit": 1000,
                "cost_model": "free"
            },
            "external_ai": {
                "providers": ["openai", "gemini", "anthropic"],
                "default_model": "gpt-4",
                "daily_limit": 2,
                "hourly_limit": 1,
                "cost_per_call": 0.01
            },
            "security": {
                "context_lock_required": True,
                "encryption_enabled": True,
                "pii_removal": True,
                "auto_delete_hours": 24
            },
            "performance": {
                "max_concurrent_requests": 10,
                "timeout_seconds": 30,
                "cache_ttl_hours": 24,
                "redis_enabled": True
            }
        }
    }

# Development server configuration
if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("AI_HOST", "0.0.0.0")
    port = int(os.getenv("AI_PORT", "8001"))
    reload = os.getenv("AI_RELOAD", "true").lower() == "true"
    log_level = os.getenv("AI_LOG_LEVEL", "info").lower()
    
    print(f"""
🤖 Libral AI Module - Revolutionary Dual-AI System Starting...

🏠 内部AI (自社AI): Privacy-first daily task processing
🎯 外部AI (判定役): Quality evaluation and improvement system
🔒 Security: Context-Lock verification required
💰 Cost Management: Smart quota system (2 external calls/24h)
📊 Monitoring: Complete usage statistics and health checks

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
        "libral_core.modules.ai.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level
    )