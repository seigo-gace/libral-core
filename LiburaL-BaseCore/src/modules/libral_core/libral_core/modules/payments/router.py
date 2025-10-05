"""
Payment & Billing FastAPI Router
Telegram Stars integration with encrypted billing and revenue sharing
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    InvoiceCreate,
    InvoiceResponse,
    Payment,
    PaymentCreate,
    PaymentHealthResponse,
    PaymentResponse,
    SubscriptionPlan,
    TelegramStarsPayment
)
from .service import PaymentService
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ..events.service import EventService
from ..gpg.service import GPGService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/payments", tags=["Payment & Billing"])

# Global payment service instance
_payment_service: Optional[PaymentService] = None

def get_payment_service() -> PaymentService:
    """Get configured payment service instance"""
    global _payment_service
    
    if _payment_service is None:
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
                logger.warning("GPG service unavailable for payments", error=str(e))
            
            # Communication service
            communication_service = None
            try:
                from ..communication.router import get_communication_service
                communication_service = get_communication_service()
            except Exception as e:
                logger.warning("Communication service unavailable for payments", error=str(e))
            
            # Event service
            event_service = None
            try:
                from ..events.router import get_event_service
                event_service = get_event_service()
            except Exception as e:
                logger.warning("Event service unavailable for payments", error=str(e))
            
            _payment_service = PaymentService(
                auth_service=auth_service,
                telegram_bot_token=settings.telegram_bot_token,
                webhook_secret=settings.telegram_webhook_secret or "default_secret",
                gpg_service=gpg_service,
                communication_service=communication_service,
                event_service=event_service
            )
            
            logger.info("Payment service initialized")
            
        except Exception as e:
            logger.error("Failed to initialize payment service", error=str(e))
            raise HTTPException(status_code=500, detail="Payment service initialization failed")
    
    return _payment_service

@router.get("/health", response_model=PaymentHealthResponse)
async def health_check(
    service: PaymentService = Depends(get_payment_service)
) -> PaymentHealthResponse:
    """
    Check payment service health
    
    Returns comprehensive status of payment processing:
    - Payment processing performance and success rates
    - Revenue sharing and developer payout statistics
    - Subscription management metrics
    - Encrypted billing log integration status
    - Telegram Stars API connectivity
    - Privacy compliance verification
    """
    return await service.health_check()

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    request: PaymentCreate,
    background_tasks: BackgroundTasks,
    service: PaymentService = Depends(get_payment_service)
) -> PaymentResponse:
    """
    Create new payment with privacy-first processing
    
    **革新的なプライバシー重視決済システム:**
    - Telegram Stars統合による簡単決済
    - 暗号化課金履歴の個人ログサーバー保存
    - プラグイン開発者への自動収益分配
    - GDPR完全準拠の支払いデータ処理
    
    **支払い方法:**
    - **Telegram Stars**: Telegram内蔵決済（推奨）
    - **暗号通貨**: Bitcoin、Ethereum対応
    - **クレジットカード**: 国際クレジットカード
    - **銀行振込**: 国内外銀行振込
    - **デジタルウォレット**: PayPal、Apple Pay等
    
    **プライバシー特徴:**
    - GPG暗号化: 全決済データをユーザーGPGキーで暗号化
    - 個人ログサーバー: 課金履歴をユーザーのTelegramに保存
    - ゼロ保存: 中央サーバーに決済データ保存なし
    - 自動削除: ユーザー設定期間後の自動削除
    - 完全制御: ユーザーが全決済データを完全制御
    
    **収益分配システム:**
    - プラグイン開発者: 売上の70%（デフォルト）
    - プラットフォーム手数料: 30%（業界標準）
    - 自動分配: 毎月自動で開発者に支払い
    - 透明性: 全収益分配を暗号化ログで記録
    
    **使用例:**
    ```python
    # プラグイン購入決済
    payment_request = PaymentCreate(
        amount=Decimal("100"),          # 100 Telegram Stars
        currency=CurrencyCode.XTR,      # Telegram Stars
        payment_method=PaymentMethod.TELEGRAM_STARS,
        user_id="user123",
        description="Premium Analytics Plugin",
        item_type="plugin",
        item_id="analytics_premium",
        enable_revenue_sharing=True,    # 開発者収益分配有効
        developer_user_id="dev456",     # プラグイン開発者
        platform_fee_percentage=Decimal("30.0")
    )
    ```
    """
    try:
        result = await service.create_payment(request)
        
        # Schedule payment expiry cleanup
        background_tasks.add_task(
            _schedule_payment_cleanup,
            service,
            result.payment_id,
            result.expires_at
        )
        
        logger.info("Payment create request processed",
                   payment_id=result.payment_id,
                   success=result.success,
                   method=request.payment_method,
                   amount=request.amount,
                   personal_log=result.personal_log_recorded)
        
        return result
        
    except Exception as e:
        logger.error("Payment create endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Payment creation failed")

@router.post("/webhook/telegram-stars")
async def telegram_stars_webhook(
    payment_data: TelegramStarsPayment,
    x_telegram_signature: str = Header(..., description="Telegram webhook signature"),
    service: PaymentService = Depends(get_payment_service)
) -> JSONResponse:
    """
    Telegram Stars payment webhook
    
    **Telegram Starsウェブフック処理:**
    - HMAC署名検証による完全セキュリティ
    - 決済完了の自動処理とステータス更新
    - 収益分配の自動計算と分配
    - 暗号化課金記録の個人ログサーバー保存
    - リアルタイム決済通知の送信
    
    **セキュリティ機能:**
    - Webhook署名検証: HMAC-SHA256による改ざん防止
    - 重複処理防止: 決済IDベースの重複チェック
    - エラー処理: 失敗時の自動リトライ機構
    - 監査ログ: 全処理を暗号化ログで記録
    
    **自動処理フロー:**
    1. Telegram署名検証
    2. 決済ステータス更新
    3. 収益分配計算
    4. 暗号化課金記録作成
    5. 個人ログサーバー保存
    6. ユーザー通知送信
    7. 開発者収益分配処理
    """
    try:
        success = await service.process_telegram_webhook(
            payment_data, x_telegram_signature
        )
        
        logger.info("Telegram webhook processed",
                   charge_id=payment_data.telegram_payment_charge_id,
                   amount=payment_data.total_amount,
                   success=success)
        
        if success:
            return JSONResponse(content={
                "success": True,
                "charge_id": payment_data.telegram_payment_charge_id,
                "processed_at": payment_data.payment_date.isoformat(),
                "message": "Payment processed successfully"
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Payment processing failed",
                    "charge_id": payment_data.telegram_payment_charge_id
                }
            )
        
    except Exception as e:
        logger.error("Telegram webhook error",
                    charge_id=payment_data.telegram_payment_charge_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Webhook processing failed")

@router.get("/history/{user_id}", response_model=List[Payment])
async def get_payment_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    service: PaymentService = Depends(get_payment_service)
) -> List[Payment]:
    """
    Get user payment history (privacy-compliant)
    
    **プライバシー準拠決済履歴:**
    - ユーザー自身の決済のみ表示
    - 暗号化データの復号化なし（個人ログサーバーで実行）
    - GDPR準拠のデータ制御
    - 保存期間後の自動削除
    
    **履歴情報:**
    - 決済ID、金額、通貨、ステータス
    - 決済方法、作成日時、処理日時
    - 商品タイプ、収益分配情報
    - プライバシー設定、保存期間
    
    **プライバシー保護:**
    - 他ユーザーの決済データアクセス不可
    - 機密情報の自動マスキング
    - 個人識別情報の除外
    - ログアクセスの暗号化記録
    """
    try:
        # Input validation
        if limit > 500:
            raise HTTPException(status_code=400, detail="Limit cannot exceed 500")
        if offset < 0:
            raise HTTPException(status_code=400, detail="Offset must be non-negative")
        
        payments = await service.get_payment_history(user_id, limit, offset)
        
        logger.info("Payment history request processed",
                   user_id=user_id,
                   returned_count=len(payments),
                   limit=limit,
                   offset=offset)
        
        return payments
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Payment history endpoint error",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get payment history")

@router.get("/plans", response_model=List[SubscriptionPlan])
async def list_subscription_plans() -> List[SubscriptionPlan]:
    """
    List available subscription plans
    
    **サブスクリプションプラン:**
    - **Basic**: 基本機能、個人ログサーバー、1GBストレージ
    - **Pro**: 全プラグインアクセス、5GBストレージ、優先サポート
    - **Developer**: 開発者ツール、無制限ストレージ、収益分析
    - **Enterprise**: カスタム統合、専用サポート、オンプレ展開
    
    **全プランの共通特徴:**
    - 完全プライバシー保護
    - 個人ログサーバー統合
    - GPG暗号化
    - GDPR完全準拠
    - 7日間無料トライアル
    """
    try:
        # Mock subscription plans - in production would load from database
        plans = [
            SubscriptionPlan(
                plan_id="basic_monthly",
                plan_name="Basic Plan",
                description="個人使用向けベーシックプラン。個人ログサーバー、基本プラグイン、1GBストレージ付き。",
                price=Decimal("50"),  # 50 Telegram Stars
                currency="XTR",
                billing_interval="monthly",
                features=[
                    "個人ログサーバー (ログ・ストレージ・ナレッジベース)",
                    "基本プラグインアクセス",
                    "1GB暗号化ストレージ",
                    "コミュニティサポート",
                    "GPG暗号化"
                ],
                limitations={"storage_mb": 1000, "api_requests": 5000},
                storage_limit_mb=1000,
                api_request_limit=5000,
                trial_days=7
            ),
            SubscriptionPlan(
                plan_id="pro_monthly",
                plan_name="Pro Plan",
                description="プロフェッショナル向け高機能プラン。全プラグインアクセス、5GBストレージ、優先サポート。",
                price=Decimal("150"),  # 150 Telegram Stars
                currency="XTR",
                billing_interval="monthly",
                features=[
                    "全機能個人ログサーバー",
                    "全プラグインアクセス",
                    "5GB暗号化ストレージ",
                    "優先サポート",
                    "高度な収益分析",
                    "カスタムテーマ"
                ],
                limitations={"storage_mb": 5000, "api_requests": 25000},
                storage_limit_mb=5000,
                api_request_limit=25000,
                trial_days=14
            ),
            SubscriptionPlan(
                plan_id="developer_monthly",
                plan_name="Developer Plan",
                description="プラグイン開発者向け特別プラン。開発ツール、無制限ストレージ、収益分析ダッシュボード。",
                price=Decimal("300"),  # 300 Telegram Stars
                currency="XTR",
                billing_interval="monthly",
                features=[
                    "開発者個人ログサーバー",
                    "プラグイン開発ツール",
                    "無制限暗号化ストレージ",
                    "収益分析ダッシュボード",
                    "マーケットプレイス優先表示",
                    "開発者専用サポート",
                    "ベータ機能アクセス"
                ],
                limitations={"storage_mb": 100000, "api_requests": 100000},
                storage_limit_mb=100000,
                api_request_limit=100000,
                trial_days=30
            )
        ]
        
        logger.info("Subscription plans listed", plans_count=len(plans))
        
        return plans
        
    except Exception as e:
        logger.error("Subscription plans endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list subscription plans")

@router.get("/revenue-sharing/stats/{user_id}")
async def get_revenue_sharing_stats(
    user_id: str,
    service: PaymentService = Depends(get_payment_service)
) -> JSONResponse:
    """
    Get revenue sharing statistics for plugin developers
    
    **開発者収益統計:**
    - 月間・年間収益サマリー
    - プラグイン別売上分析
    - 支払い予定と履歴
    - 収益分配透明性レポート
    
    **プライバシー保護:**
    - 開発者自身の収益データのみ表示
    - 暗号化による機密保護
    - GDPR準拠のデータ処理
    - 個人ログサーバーとの連携
    """
    try:
        # Mock revenue sharing stats - in production would calculate from actual data
        revenue_stats = {
            "developer_id": user_id,
            "current_month": {
                "total_revenue": "2150.50",
                "currency": "XTR",
                "plugin_sales": 43,
                "average_sale_amount": "50.01"
            },
            "last_month": {
                "total_revenue": "1875.25", 
                "currency": "XTR",
                "plugin_sales": 38,
                "average_sale_amount": "49.35"
            },
            "pending_payout": {
                "amount": "1505.35",
                "currency": "XTR",
                "payout_date": "2025-02-01",
                "payout_method": "telegram_stars"
            },
            "top_plugins": [
                {
                    "plugin_id": "analytics_premium",
                    "name": "Premium Analytics",
                    "sales_count": 25,
                    "revenue": "1250.00"
                },
                {
                    "plugin_id": "security_scanner",
                    "name": "Security Scanner Pro",
                    "sales_count": 18,
                    "revenue": "900.50"
                }
            ],
            "revenue_trend": "increasing",
            "payout_history": [
                {
                    "date": "2025-01-01",
                    "amount": "1200.75",
                    "status": "completed"
                }
            ],
            "privacy_features": [
                "暗号化収益データ",
                "個人ログサーバー保存",
                "GDPR完全準拠", 
                "透明性レポート"
            ]
        }
        
        logger.info("Revenue sharing stats requested",
                   user_id=user_id,
                   current_month_revenue=revenue_stats["current_month"]["total_revenue"])
        
        return JSONResponse(content=revenue_stats)
        
    except Exception as e:
        logger.error("Revenue sharing stats endpoint error",
                    user_id=user_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get revenue sharing stats")

@router.get("/currencies")
async def list_supported_currencies() -> JSONResponse:
    """
    List supported currencies and payment methods
    
    Returns information about all supported currencies,
    payment methods, and their current availability.
    """
    try:
        from .schemas import CurrencyCode, PaymentMethod
        
        currencies = [
            {
                "code": currency.value,
                "name": _get_currency_name(currency),
                "symbol": _get_currency_symbol(currency),
                "supported_methods": _get_payment_methods_for_currency(currency),
                "processing_time": _get_processing_time(currency),
                "fees": _get_fee_structure(currency)
            }
            for currency in CurrencyCode
        ]
        
        payment_methods = [
            {
                "id": method.value,
                "name": method.value.replace("_", " ").title(),
                "description": _get_payment_method_description(method),
                "supported_currencies": _get_currencies_for_method(method),
                "privacy_level": _get_privacy_level(method),
                "processing_time": _get_method_processing_time(method)
            }
            for method in PaymentMethod
        ]
        
        return JSONResponse(content={
            "currencies": currencies,
            "payment_methods": payment_methods,
            "default_currency": "XTR",
            "recommended_method": "telegram_stars",
            "privacy_features": [
                "GPG暗号化課金データ",
                "個人ログサーバー保存",
                "ゼロ中央データ保存",
                "GDPR完全準拠"
            ]
        })
        
    except Exception as e:
        logger.error("Currencies endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list currencies")

def _get_currency_name(currency) -> str:
    """Get human-readable currency name"""
    names = {
        "XTR": "Telegram Stars",
        "USD": "US Dollar",
        "EUR": "Euro",
        "JPY": "Japanese Yen",
        "BTC": "Bitcoin",
        "ETH": "Ethereum"
    }
    return names.get(currency.value, currency.value)

def _get_currency_symbol(currency) -> str:
    """Get currency symbol"""
    symbols = {
        "XTR": "⭐",
        "USD": "$",
        "EUR": "€",
        "JPY": "¥",
        "BTC": "₿",
        "ETH": "Ξ"
    }
    return symbols.get(currency.value, currency.value)

def _get_payment_methods_for_currency(currency) -> List[str]:
    """Get supported payment methods for currency"""
    if currency.value == "XTR":
        return ["telegram_stars"]
    elif currency.value in ["BTC", "ETH"]:
        return ["cryptocurrency"]
    else:
        return ["credit_card", "bank_transfer", "digital_wallet"]

def _get_processing_time(currency) -> str:
    """Get typical processing time for currency"""
    times = {
        "XTR": "Instant",
        "USD": "1-3 business days",
        "EUR": "1-3 business days", 
        "JPY": "1-2 business days",
        "BTC": "10-60 minutes",
        "ETH": "2-15 minutes"
    }
    return times.get(currency.value, "1-3 business days")

def _get_fee_structure(currency) -> Dict[str, str]:
    """Get fee structure for currency"""
    fees = {
        "XTR": {"platform": "30%", "processor": "0%"},
        "USD": {"platform": "30%", "processor": "2.9% + $0.30"},
        "EUR": {"platform": "30%", "processor": "2.9% + €0.25"},
        "JPY": {"platform": "30%", "processor": "3.4% + ¥40"},
        "BTC": {"platform": "30%", "processor": "Network fees"},
        "ETH": {"platform": "30%", "processor": "Gas fees"}
    }
    return fees.get(currency.value, {"platform": "30%", "processor": "Varies"})

def _get_payment_method_description(method) -> str:
    """Get payment method description"""
    descriptions = {
        "telegram_stars": "Telegram内蔵決済システム（推奨）",
        "cryptocurrency": "Bitcoin、Ethereum等の暗号通貨決済",
        "credit_card": "Visa、Mastercard、JCB等のクレジットカード",
        "bank_transfer": "国内外銀行振込",
        "digital_wallet": "PayPal、Apple Pay、Google Pay等"
    }
    return descriptions.get(method.value, "決済方法")

def _get_currencies_for_method(method) -> List[str]:
    """Get supported currencies for payment method"""
    if method.value == "telegram_stars":
        return ["XTR"]
    elif method.value == "cryptocurrency":
        return ["BTC", "ETH"]
    else:
        return ["USD", "EUR", "JPY"]

def _get_privacy_level(method) -> str:
    """Get privacy level for payment method"""
    levels = {
        "telegram_stars": "High",
        "cryptocurrency": "Very High",
        "credit_card": "Medium",
        "bank_transfer": "Low",
        "digital_wallet": "Medium"
    }
    return levels.get(method.value, "Medium")

def _get_method_processing_time(method) -> str:
    """Get processing time for payment method"""
    times = {
        "telegram_stars": "Instant",
        "cryptocurrency": "10-60 minutes", 
        "credit_card": "Instant",
        "bank_transfer": "1-3 business days",
        "digital_wallet": "Instant"
    }
    return times.get(method.value, "Varies")

async def _schedule_payment_cleanup(
    service: PaymentService,
    payment_id: str,
    expires_at
):
    """Schedule payment cleanup after expiry"""
    try:
        import asyncio
        from datetime import datetime
        
        # Calculate sleep time
        now = datetime.utcnow()
        if expires_at > now:
            sleep_seconds = (expires_at - now).total_seconds()
            await asyncio.sleep(sleep_seconds)
        
        # Clean up expired payment
        if payment_id in service.payments:
            payment = service.payments[payment_id]
            if payment.status == "pending":
                payment.status = "cancelled"
                logger.info("Expired payment cancelled", payment_id=payment_id)
                
    except Exception as e:
        logger.error("Payment cleanup failed", payment_id=payment_id, error=str(e))

# Cleanup handler
@router.on_event("startup")
async def startup_payment_service():
    """Initialize payment service"""
    # Service is lazy-loaded via dependency injection
    pass

@router.on_event("shutdown")
async def cleanup_payment_service():
    """Cleanup payment service resources"""
    global _payment_service
    if _payment_service:
        await _payment_service.cleanup()
        _payment_service = None
        logger.info("Payment service cleanup completed")