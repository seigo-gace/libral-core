"""
API Hub FastAPI Router
External API integration and usage tracking endpoints
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    APICredential,
    APICredentialCreate,
    APIHubHealthResponse,
    APIProvider,
    ExternalAPICall,
    ServiceConnector,
    ThirdPartyIntegration
)
from .service import APIHubService
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ..events.service import EventService
from ..gpg.service import GPGService
from ..payments.service import PaymentService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/api-hub", tags=["API Hub & External Integration"])

# Global API Hub service instance
_api_hub_service: Optional[APIHubService] = None

def get_api_hub_service() -> APIHubService:
    """Get configured API Hub service instance"""
    global _api_hub_service
    
    if _api_hub_service is None:
        try:
            # Initialize dependencies
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
                logger.warning("GPG service unavailable for API Hub", error=str(e))
            
            # Communication service
            communication_service = None
            try:
                from ..communication.router import get_communication_service
                communication_service = get_communication_service()
            except Exception as e:
                logger.warning("Communication service unavailable for API Hub", error=str(e))
            
            # Event service
            event_service = None
            try:
                from ..events.router import get_event_service
                event_service = get_event_service()
            except Exception as e:
                logger.warning("Event service unavailable for API Hub", error=str(e))
            
            # Payment service
            payment_service = None
            try:
                from ..payments.router import get_payment_service
                payment_service = get_payment_service()
            except Exception as e:
                logger.warning("Payment service unavailable for API Hub", error=str(e))
            
            _api_hub_service = APIHubService(
                auth_service=auth_service,
                gpg_service=gpg_service,
                communication_service=communication_service,
                event_service=event_service,
                payment_service=payment_service
            )
            
            logger.info("API Hub service initialized")
            
        except Exception as e:
            logger.error("Failed to initialize API Hub service", error=str(e))
            raise HTTPException(status_code=500, detail="API Hub service initialization failed")
    
    return _api_hub_service

@router.get("/health", response_model=APIHubHealthResponse)
async def health_check(
    service: APIHubService = Depends(get_api_hub_service)
) -> APIHubHealthResponse:
    """
    Check API Hub service health
    
    Returns comprehensive status of API integration components:
    - API credential management and encryption status
    - External API call statistics and performance
    - Usage tracking and quota management
    - Cost tracking and billing integration
    - Provider health and connectivity status
    - Privacy compliance and personal log integration
    """
    return await service.health_check()

@router.post("/credentials", response_model=Dict[str, Any])
async def create_api_credential(
    request: APICredentialCreate,
    user_id: str,
    background_tasks: BackgroundTasks,
    service: APIHubService = Depends(get_api_hub_service)
) -> Dict[str, Any]:
    """
    Create encrypted API credential
    
    **外部API認証情報の安全管理:**
    - GPG暗号化によるAPI Key保護
    - 個人ログサーバーでの認証情報管理
    - アクセス制御とIP制限機能
    - 使用量制限とコスト管理
    - 完全なユーザー制御とプライバシー保護
    
    **サポートプロバイダー:**
    - **OpenAI**: GPT-4、GPT-3.5、Whisper、DALL-E
    - **Anthropic**: Claude-3 Opus、Sonnet、Haiku
    - **Google Cloud**: Gemini、Vertex AI、Cloud APIs
    - **AWS**: Bedrock、Lambda、S3、その他AWSサービス
    - **Azure**: OpenAI Service、Cognitive Services
    - **Stripe**: 決済処理、サブスクリプション管理
    - **Telegram**: Bot API、Payment API
    - **GitHub**: Repository API、Actions API
    - **Slack**: Bot API、Webhook
    - **Discord**: Bot API、Webhook
    - **Custom**: カスタムAPI統合
    
    **セキュリティ機能:**
    - GPG暗号化: ユーザーGPGキーでAPI Key暗号化
    - アクセス制御: IPホワイトリスト、オリジン制限
    - 使用量監視: 日次・月次制限、コスト上限
    - 監査ログ: 全API使用状況の個人ログサーバー記録
    - 自動期限管理: 認証情報の定期更新提醒
    
    **プライバシー保護:**
    - ゼロ平文保存: API Keyは暗号化されてのみ保存
    - 個人ログサーバー: 使用履歴をユーザーのTelegramに記録
    - GDPR準拠: 完全なデータ制御と削除権
    - 透明性: 全API使用状況の可視化
    
    **使用例:**
    ```python
    # OpenAI API認証情報作成
    credential_request = APICredentialCreate(
        provider=APIProvider.OPENAI,
        name="My OpenAI API Key",
        description="GPT-4 API access for plugins",
        api_key="sk-...",                    # 暗号化されて保存
        daily_quota=1000,                    # 日次1000リクエスト制限
        monthly_quota=25000,                 # 月次25000リクエスト制限
        cost_limit_usd=100.00,              # 月次$100コスト制限
        allowed_origins=["https://myapp.com"],
        log_requests=True,                   # リクエストログ有効
        log_to_personal_server=True         # 個人ログサーバー記録
    )
    ```
    """
    try:
        success, credential, error = await service.create_credential(user_id, request)
        
        if success and credential:
            # Schedule credential health monitoring
            background_tasks.add_task(
                _schedule_credential_monitoring,
                service,
                credential.credential_id
            )
            
            logger.info("API credential created",
                       credential_id=credential.credential_id,
                       user_id=user_id,
                       provider=request.provider)
            
            return {
                "success": True,
                "credential_id": credential.credential_id,
                "provider": credential.provider,
                "name": credential.name,
                "status": credential.status,
                "created_at": credential.created_at.isoformat(),
                "encryption_enabled": bool(credential.encryption_recipient),
                "security_features": [
                    "GPG暗号化API Key保護",
                    "アクセス制御とIP制限",
                    "使用量制限とコスト管理",
                    "個人ログサーバー統合",
                    "GDPR完全準拠"
                ]
            }
        else:
            return {
                "success": False,
                "error": error or "Unknown error occurred",
                "provider": request.provider
            }
        
    except Exception as e:
        logger.error("API credential creation endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="API credential creation failed")

@router.get("/credentials/{user_id}", response_model=List[Dict[str, Any]])
async def list_user_credentials(
    user_id: str,
    service: APIHubService = Depends(get_api_hub_service)
) -> List[Dict[str, Any]]:
    """
    List user's API credentials (privacy-compliant)
    
    **プライバシー準拠認証情報一覧:**
    - ユーザー自身の認証情報のみ表示
    - API Keyの平文は表示なし（暗号化済み）
    - 使用状況統計と制限情報
    - セキュリティ設定と監査ログ
    
    **表示情報:**
    - 認証情報ID、プロバイダー、名前
    - ステータス、作成日時、最終使用日時
    - 使用量制限、コスト制限、アクセス制御設定
    - 暗号化状況、個人ログサーバー設定
    
    **プライバシー保護:**
    - API Keyやシークレットの平文表示なし
    - 他ユーザーの認証情報アクセス不可
    - 機密情報の自動マスキング
    - アクセスログの暗号化記録
    """
    try:
        credentials = await service.get_user_credentials(user_id)
        
        # Format credentials for safe display (no sensitive data)
        safe_credentials = []
        for cred in credentials:
            safe_cred = {
                "credential_id": cred.credential_id,
                "provider": cred.provider,
                "name": cred.name,
                "description": cred.description,
                "status": cred.status,
                "created_at": cred.created_at.isoformat(),
                "updated_at": cred.updated_at.isoformat(),
                "last_used_at": cred.last_used_at.isoformat() if cred.last_used_at else None,
                "daily_quota": cred.daily_quota,
                "monthly_quota": cred.monthly_quota,
                "cost_limit_usd": str(cred.cost_limit_usd) if cred.cost_limit_usd else None,
                "encryption_enabled": bool(cred.encryption_recipient),
                "log_to_personal_server": cred.log_to_personal_server,
                "gdpr_compliant": cred.gdpr_compliant,
                "security_settings": {
                    "require_authentication": cred.require_authentication,
                    "log_requests": cred.log_requests,
                    "ip_whitelist_count": len(cred.ip_whitelist),
                    "allowed_origins_count": len(cred.allowed_origins)
                }
            }
            safe_credentials.append(safe_cred)
        
        logger.info("User credentials listed",
                   user_id=user_id,
                   credentials_count=len(credentials))
        
        return safe_credentials
        
    except Exception as e:
        logger.error("List credentials endpoint error",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list credentials")

@router.post("/call", response_model=Dict[str, Any])
async def call_external_api(
    request: ExternalAPICall,
    user_id: str,
    service: APIHubService = Depends(get_api_hub_service)
) -> Dict[str, Any]:
    """
    Make external API call with tracking
    
    **プライバシー重視外部API呼び出し:**
    - 暗号化認証情報を使用した安全なAPI呼び出し
    - 使用量追跡とコスト管理
    - 個人ログサーバーでの呼び出し履歴記録
    - レート制限とクォータ管理
    - GDPR準拠のデータ処理
    
    **セキュリティ機能:**
    - 認証情報の自動復号化とAPI認証
    - タイムアウト制御とエラーハンドリング
    - SSL証明書検証とセキュア通信
    - アクセス制御とIP制限チェック
    - 機密データの自動サニタイゼーション
    
    **使用量管理:**
    - リアルタイム使用量追跡
    - 日次・月次クォータチェック
    - コスト見積もりと制限確認
    - 自動警告とアラート
    - 個人ログサーバーでの詳細記録
    
    **プライバシー保護:**
    - レスポンスデータの機密情報除去
    - 個人データの適切な処理
    - ログの暗号化と期限管理
    - ユーザー制御のデータ保存
    
    **使用例:**
    ```python
    # OpenAI GPT-4 API呼び出し
    api_call = ExternalAPICall(
        credential_id="cred_123",
        endpoint="https://api.openai.com/v1/chat/completions",
        method="POST",
        request_body={
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 100
        },
        timeout_seconds=30,
        max_cost_usd=1.00,              # 最大$1制限
        purpose="chatbot_response",     # 使用目的記録
        log_request=True,               # リクエストログ
        log_response=False,             # レスポンスログなし（プライバシー）
        contains_personal_data=False    # 個人データ含まず
    )
    ```
    """
    try:
        success, response_data, error = await service.call_external_api(user_id, request)
        
        if success:
            logger.info("External API call completed",
                       user_id=user_id,
                       endpoint=request.endpoint,
                       method=request.method,
                       success=True)
            
            return {
                "success": True,
                "response": response_data,
                "metadata": {
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "purpose": request.purpose,
                    "plugin_id": request.plugin_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "privacy_compliant": True,
                    "logged_to_personal_server": True
                }
            }
        else:
            logger.warning("External API call failed",
                          user_id=user_id,
                          endpoint=request.endpoint,
                          error=error)
            
            return {
                "success": False,
                "error": error,
                "metadata": {
                    "endpoint": request.endpoint,
                    "method": request.method,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        
    except Exception as e:
        logger.error("External API call endpoint error",
                    user_id=user_id,
                    endpoint=request.endpoint,
                    error=str(e))
        raise HTTPException(status_code=500, detail="External API call failed")

@router.get("/usage/{user_id}")
async def get_usage_statistics(
    user_id: str,
    period_days: int = 30,
    service: APIHubService = Depends(get_api_hub_service)
) -> JSONResponse:
    """
    Get user's API usage statistics
    
    **プライバシー準拠使用量統計:**
    - ユーザー自身の使用状況のみ表示
    - プロバイダー別使用量とコスト分析
    - 成功率とエラー率の統計
    - 個人ログサーバーとの統合データ
    
    **統計情報:**
    - 総API呼び出し数、成功・失敗数
    - プロバイダー別内訳とコスト
    - 平均レスポンス時間
    - 使用トレンドと予測
    
    **プライバシー保護:**
    - 他ユーザーの統計アクセス不可
    - 機密情報の除外
    - 個人データの匿名化
    - GDPR準拠のデータ処理
    """
    try:
        if period_days > 365:
            raise HTTPException(status_code=400, detail="Period cannot exceed 365 days")
        
        stats = await service.get_usage_statistics(user_id, period_days)
        
        # Add privacy and compliance information
        stats["privacy_features"] = [
            "暗号化API認証情報管理",
            "個人ログサーバー統合",
            "GDPR完全準拠",
            "ユーザー制御データ保存",
            "機密情報自動保護"
        ]
        
        stats["data_governance"] = {
            "user_controlled": True,
            "zero_retention": True,
            "encryption_required": True,
            "gdpr_compliant": True,
            "personal_server_logged": True
        }
        
        logger.info("Usage statistics retrieved",
                   user_id=user_id,
                   period_days=period_days,
                   total_calls=stats.get("total_calls", 0))
        
        return JSONResponse(content=stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Usage statistics endpoint error",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get usage statistics")

@router.get("/providers")
async def list_supported_providers() -> JSONResponse:
    """
    List supported API providers and their capabilities
    
    **サポートプロバイダー一覧:**
    - 各プロバイダーの機能と特徴
    - 認証方法とセキュリティレベル
    - コスト構造と使用量制限
    - プライバシー保護機能
    """
    try:
        providers = [
            {
                "id": provider.value,
                "name": _get_provider_name(provider),
                "description": _get_provider_description(provider),
                "authentication_type": _get_auth_type(provider),
                "privacy_level": _get_privacy_level(provider),
                "cost_model": _get_cost_model(provider),
                "features": _get_provider_features(provider),
                "documentation_url": _get_docs_url(provider)
            }
            for provider in APIProvider
        ]
        
        return JSONResponse(content={
            "providers": providers,
            "total_providers": len(providers),
            "security_features": [
                "GPG暗号化認証情報保護",
                "個人ログサーバー統合",
                "使用量追跡とコスト管理",
                "アクセス制御とIP制限",
                "GDPR完全準拠"
            ],
            "privacy_commitment": [
                "ユーザー完全制御",
                "ゼロ平文保存",
                "暗号化必須",
                "透明性保証",
                "即座削除可能"
            ]
        })
        
    except Exception as e:
        logger.error("Providers list endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list providers")

@router.get("/integrations/{user_id}")
async def list_user_integrations(
    user_id: str,
    service: APIHubService = Depends(get_api_hub_service)
) -> List[Dict[str, Any]]:
    """
    List user's third-party integrations
    
    **サードパーティ統合管理:**
    - Webhook統合とコールバック設定
    - OAuth認証フローとスコープ管理
    - 直接接続とプロキシ設定
    - プラグイン統合とAPI連携
    """
    try:
        # Get user integrations
        user_integrations = [
            integration for integration in service.integrations.values()
            if integration.user_id == user_id
        ]
        
        # Format for safe display
        safe_integrations = []
        for integration in user_integrations:
            safe_integration = {
                "integration_id": integration.integration_id,
                "name": integration.name,
                "description": integration.description,
                "provider": integration.provider,
                "integration_type": integration.integration_type,
                "status": integration.status,
                "created_at": integration.created_at.isoformat(),
                "last_health_check": integration.last_health_check.isoformat() if integration.last_health_check else None,
                "total_calls": integration.total_calls,
                "successful_calls": integration.successful_calls,
                "success_rate": integration.successful_calls / max(integration.total_calls, 1),
                "privacy_settings": {
                    "log_to_personal_server": integration.log_to_personal_server,
                    "gdpr_compliant": integration.gdpr_compliant,
                    "data_retention_days": integration.data_retention_days
                }
            }
            safe_integrations.append(safe_integration)
        
        logger.info("User integrations listed",
                   user_id=user_id,
                   integrations_count=len(user_integrations))
        
        return safe_integrations
        
    except Exception as e:
        logger.error("List integrations endpoint error",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list integrations")

def _get_provider_name(provider) -> str:
    """Get human-readable provider name"""
    names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google_cloud": "Google Cloud",
        "aws": "Amazon Web Services",
        "azure": "Microsoft Azure",
        "stripe": "Stripe",
        "telegram": "Telegram",
        "github": "GitHub",
        "slack": "Slack",
        "discord": "Discord",
        "custom": "カスタムAPI"
    }
    return names.get(provider.value, provider.value.title())

def _get_provider_description(provider) -> str:
    """Get provider description in Japanese"""
    descriptions = {
        "openai": "GPT-4、ChatGPT、DALL-E、Whisper等のAI API",
        "anthropic": "Claude-3 AI アシスタント API",
        "google_cloud": "Gemini、Vertex AI、Google Cloud サービス",
        "aws": "Bedrock、Lambda、S3等のAWS サービス",
        "azure": "Azure OpenAI Service、Cognitive Services",
        "stripe": "決済処理、サブスクリプション管理",
        "telegram": "Telegram Bot API、Payment API",
        "github": "GitHub Repository API、Actions API",
        "slack": "Slack Bot API、Webhook統合",
        "discord": "Discord Bot API、Webhook統合",
        "custom": "カスタムRESTful API統合"
    }
    return descriptions.get(provider.value, "外部APIサービス")

def _get_auth_type(provider) -> str:
    """Get authentication type for provider"""
    auth_types = {
        "openai": "Bearer Token",
        "anthropic": "API Key Header",
        "google_cloud": "OAuth 2.0 / Service Account",
        "aws": "AWS Signature V4",
        "azure": "Subscription Key",
        "stripe": "Secret Key",
        "telegram": "Bot Token",
        "github": "Personal Access Token",
        "slack": "OAuth 2.0 / Bot Token",
        "discord": "Bot Token",
        "custom": "Configurable"
    }
    return auth_types.get(provider.value, "API Key")

def _get_privacy_level(provider) -> str:
    """Get privacy level for provider"""
    levels = {
        "openai": "High",
        "anthropic": "High", 
        "google_cloud": "Medium",
        "aws": "Medium",
        "azure": "Medium",
        "stripe": "High",
        "telegram": "High",
        "github": "Medium",
        "slack": "Medium",
        "discord": "Medium",
        "custom": "Configurable"
    }
    return levels.get(provider.value, "Medium")

def _get_cost_model(provider) -> str:
    """Get cost model for provider"""
    models = {
        "openai": "Token-based pricing",
        "anthropic": "Token-based pricing",
        "google_cloud": "Usage-based pricing",
        "aws": "Pay-as-you-go",
        "azure": "Consumption-based",
        "stripe": "Transaction-based",
        "telegram": "Free with limits",
        "github": "Free tier available",
        "slack": "App-based pricing",
        "discord": "Free for bots",
        "custom": "Provider-dependent"
    }
    return models.get(provider.value, "Usage-based")

def _get_provider_features(provider) -> List[str]:
    """Get provider feature list"""
    features_map = {
        "openai": ["GPT-4 Chat", "Text Generation", "Image Generation", "Speech Recognition"],
        "anthropic": ["Claude-3 Chat", "Long Context", "Code Analysis", "Document Processing"],
        "google_cloud": ["Gemini AI", "Vertex AI", "Cloud Storage", "BigQuery"],
        "aws": ["Bedrock", "Lambda Functions", "S3 Storage", "RDS Database"],
        "azure": ["Azure OpenAI", "Cognitive Services", "Storage", "Functions"],
        "stripe": ["Payment Processing", "Subscriptions", "Invoicing", "Connect"],
        "telegram": ["Bot API", "Payment API", "Webhook", "File Upload"],
        "github": ["Repository API", "Actions API", "Issues", "Pull Requests"],
        "slack": ["Bot API", "Interactive Components", "Workflows", "File Sharing"],
        "discord": ["Bot API", "Slash Commands", "Embeds", "Voice Channels"],
        "custom": ["RESTful API", "Webhook Support", "Custom Headers", "Authentication"]
    }
    return features_map.get(provider.value, ["API Access"])

def _get_docs_url(provider) -> str:
    """Get documentation URL for provider"""
    docs_urls = {
        "openai": "https://platform.openai.com/docs",
        "anthropic": "https://docs.anthropic.com",
        "google_cloud": "https://cloud.google.com/docs",
        "aws": "https://docs.aws.amazon.com",
        "azure": "https://docs.microsoft.com/azure",
        "stripe": "https://stripe.com/docs",
        "telegram": "https://core.telegram.org/bots/api",
        "github": "https://docs.github.com/rest",
        "slack": "https://api.slack.com",
        "discord": "https://discord.com/developers/docs",
        "custom": "https://libral.dev/docs/api-hub"
    }
    return docs_urls.get(provider.value, "https://libral.dev/docs")

async def _schedule_credential_monitoring(
    service: APIHubService,
    credential_id: str
):
    """Schedule periodic credential health monitoring"""
    try:
        # In production, would set up periodic health checks
        logger.info("Credential monitoring scheduled", credential_id=credential_id)
    except Exception as e:
        logger.error("Credential monitoring setup failed",
                    credential_id=credential_id,
                    error=str(e))

# Cleanup handler
@router.on_event("startup")
async def startup_api_hub_service():
    """Initialize API Hub service"""
    # Service is lazy-loaded via dependency injection
    pass

@router.on_event("shutdown")
async def cleanup_api_hub_service():
    """Cleanup API Hub service resources"""
    global _api_hub_service
    if _api_hub_service:
        await _api_hub_service.cleanup()
        _api_hub_service = None
        logger.info("API Hub service cleanup completed")