"""
Payment & Billing Schemas
Privacy-first payment processing with encrypted billing logs
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class PaymentStatus(str, Enum):
    """Payment processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class PaymentMethod(str, Enum):
    """Supported payment methods"""
    TELEGRAM_STARS = "telegram_stars"
    CRYPTOCURRENCY = "cryptocurrency"
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"


class CurrencyCode(str, Enum):
    """Supported currencies"""
    XTR = "XTR"  # Telegram Stars
    USD = "USD"
    EUR = "EUR"
    JPY = "JPY"
    BTC = "BTC"
    ETH = "ETH"


class SubscriptionStatus(str, Enum):
    """Subscription status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    TRIAL = "trial"


class RevenueShareType(str, Enum):
    """Revenue sharing types"""
    PLUGIN_DEVELOPER = "plugin_developer"
    PLATFORM_FEE = "platform_fee"
    PAYMENT_PROCESSOR = "payment_processor"
    REFERRAL_BONUS = "referral_bonus"


class Payment(BaseModel):
    """Core payment model with privacy controls"""
    
    # Payment identification
    payment_id: str = Field(..., description="Unique payment identifier")
    external_payment_id: Optional[str] = Field(default=None, description="External processor payment ID")
    correlation_id: Optional[str] = Field(default=None, description="Request correlation ID")
    
    # Payment details
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: CurrencyCode = Field(default=CurrencyCode.XTR)
    payment_method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Customer information
    user_id: str = Field(..., description="Customer user ID")
    customer_telegram_id: Optional[int] = Field(default=None, description="Customer Telegram ID")
    
    # Transaction context
    description: str = Field(..., max_length=500, description="Payment description")
    item_type: str = Field(..., description="Type of item being purchased")
    item_id: Optional[str] = Field(default=None, description="ID of purchased item")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    
    # Financial details
    platform_fee: Optional[Decimal] = Field(default=None, ge=0)
    developer_share: Optional[Decimal] = Field(default=None, ge=0)
    net_amount: Optional[Decimal] = Field(default=None, ge=0)
    
    # Payment processor details
    processor_fee: Optional[Decimal] = Field(default=None, ge=0)
    exchange_rate: Optional[Decimal] = Field(default=None, gt=0)
    
    # Privacy and compliance
    log_to_personal_server: bool = Field(default=True)
    encrypt_billing_data: bool = Field(default=True)
    retention_days: int = Field(default=2555, ge=1, le=3650)  # 7 years default for billing
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    payment_source: str = Field(default="libral_core", description="Payment source system")


class PaymentCreate(BaseModel):
    """Payment creation request"""
    
    # Payment details
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    currency: CurrencyCode = Field(default=CurrencyCode.XTR)
    payment_method: PaymentMethod
    
    # Customer
    user_id: str = Field(..., description="Customer user ID")
    customer_telegram_id: Optional[int] = Field(default=None)
    
    # Transaction details
    description: str = Field(..., max_length=500)
    item_type: str = Field(..., pattern=r"^[a-z_]+$", description="Item type (plugin, subscription, etc.)")
    item_id: Optional[str] = Field(default=None)
    
    # Revenue sharing
    enable_revenue_sharing: bool = Field(default=True)
    developer_user_id: Optional[str] = Field(default=None, description="Plugin developer user ID")
    platform_fee_percentage: Decimal = Field(default=Decimal("30.0"), ge=0, le=100)
    
    # Timing and expiry
    expires_in_minutes: int = Field(default=30, ge=1, le=1440)  # Max 24 hours
    
    # Privacy settings
    log_to_personal_server: bool = Field(default=True)
    encrypt_billing_data: bool = Field(default=True)
    
    # Context
    correlation_id: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment creation/processing response"""
    
    success: bool
    payment_id: str
    payment: Optional[Payment] = Field(default=None)
    
    # Payment processing info
    payment_url: Optional[str] = Field(default=None, description="Payment URL for customer")
    qr_code_data: Optional[str] = Field(default=None, description="QR code for payment")
    
    # Telegram Stars specific
    telegram_invoice_payload: Optional[str] = Field(default=None)
    telegram_provider_token: Optional[str] = Field(default=None)
    
    # Timing
    expires_at: datetime
    estimated_processing_time_minutes: int = Field(default=5, ge=1)
    
    # Privacy compliance
    personal_log_recorded: bool = Field(default=False)
    billing_data_encrypted: bool = Field(default=False)
    
    # Error handling
    error: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)
    retry_possible: bool = Field(default=True)
    
    request_id: str = Field(..., description="Unique request identifier")


class TelegramStarsPayment(BaseModel):
    """Telegram Stars payment specifics"""
    
    # Telegram payment details
    telegram_payment_charge_id: str = Field(..., description="Telegram payment charge ID")
    provider_payment_charge_id: str = Field(..., description="Provider payment charge ID")
    
    # Stars details
    total_amount: int = Field(..., gt=0, description="Total amount in Stars")
    currency: str = Field(default="XTR", pattern=r"^XTR$")
    
    # Invoice details
    invoice_payload: str = Field(..., description="Invoice payload for verification")
    shipping_option_id: Optional[str] = Field(default=None)
    
    # Customer info
    telegram_user_id: int = Field(..., description="Telegram user ID")
    
    # Order info (optional)
    order_info: Optional[Dict[str, Any]] = Field(default=None)
    
    # Timing
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Verification
    verified: bool = Field(default=False)
    verification_signature: Optional[str] = Field(default=None)


class SubscriptionPlan(BaseModel):
    """Subscription plan definition"""
    
    plan_id: str = Field(..., description="Unique plan identifier")
    plan_name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=1000)
    
    # Pricing
    price: Decimal = Field(..., gt=0)
    currency: CurrencyCode = Field(default=CurrencyCode.XTR)
    billing_interval: str = Field(..., pattern=r"^(monthly|yearly|weekly|daily)$")
    
    # Features
    features: List[str] = Field(default_factory=list, max_items=20)
    limitations: Dict[str, Any] = Field(default_factory=dict)
    
    # Access control
    plugin_access: List[str] = Field(default_factory=list, description="Included plugin IDs")
    storage_limit_mb: int = Field(default=1000, ge=100)
    api_request_limit: int = Field(default=10000, ge=1000)
    
    # Plan status
    active: bool = Field(default=True)
    public: bool = Field(default=True)
    trial_days: int = Field(default=0, ge=0, le=365)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Subscription(BaseModel):
    """User subscription model"""
    
    subscription_id: str = Field(..., description="Unique subscription identifier")
    user_id: str = Field(..., description="Subscriber user ID")
    plan_id: str = Field(..., description="Subscription plan ID")
    
    # Subscription status
    status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIAL)
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime
    
    # Billing
    amount: Decimal = Field(..., gt=0)
    currency: CurrencyCode = Field(default=CurrencyCode.XTR)
    payment_method: PaymentMethod
    
    # Trial information
    trial_start: Optional[datetime] = Field(default=None)
    trial_end: Optional[datetime] = Field(default=None)
    
    # Cancellation
    cancel_at_period_end: bool = Field(default=False)
    cancelled_at: Optional[datetime] = Field(default=None)
    cancellation_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Auto-renewal
    auto_renew: bool = Field(default=True)
    renewal_attempts: int = Field(default=0, ge=0)
    last_renewal_attempt: Optional[datetime] = Field(default=None)
    
    # Privacy settings
    log_to_personal_server: bool = Field(default=True)
    encrypt_subscription_data: bool = Field(default=True)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('current_period_end', pre=True, always=True)
    def set_period_end(cls, v, values):
        if v is None and 'current_period_start' in values:
            # Default to 1 month from start
            return values['current_period_start'] + timedelta(days=30)
        return v


class RevenueShare(BaseModel):
    """Revenue sharing record"""
    
    share_id: str = Field(..., description="Unique revenue share identifier")
    payment_id: str = Field(..., description="Related payment ID")
    
    # Revenue distribution
    share_type: RevenueShareType
    recipient_user_id: str = Field(..., description="Revenue recipient user ID")
    
    # Financial details
    original_amount: Decimal = Field(..., gt=0)
    share_percentage: Decimal = Field(..., ge=0, le=100)
    share_amount: Decimal = Field(..., ge=0)
    currency: CurrencyCode
    
    # Processing
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    processed_at: Optional[datetime] = Field(default=None)
    
    # Payout details
    payout_method: Optional[str] = Field(default=None)
    payout_schedule: str = Field(default="monthly", pattern=r"^(daily|weekly|monthly|quarterly)$")
    next_payout_date: Optional[datetime] = Field(default=None)
    
    # Context
    item_type: str = Field(..., description="Type of item generating revenue")
    item_id: Optional[str] = Field(default=None)
    description: str = Field(..., max_length=500)
    
    # Privacy
    log_to_personal_server: bool = Field(default=True)
    encrypt_revenue_data: bool = Field(default=True)
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BillingRecord(BaseModel):
    """Encrypted billing record for personal log server"""
    
    record_id: str = Field(..., description="Unique billing record identifier")
    user_id: str = Field(..., description="Billing record owner")
    
    # Record type
    record_type: str = Field(..., pattern=r"^(payment|subscription|refund|revenue_share)$")
    related_id: str = Field(..., description="Related payment/subscription ID")
    
    # Financial summary
    amount: Decimal = Field(..., description="Record amount")
    currency: CurrencyCode
    transaction_date: datetime
    
    # Encrypted details
    encrypted_details: str = Field(..., description="GPG-encrypted billing details")
    encryption_recipient: str = Field(..., description="GPG key fingerprint")
    
    # Categories for personal log organization
    category: str = Field(default="payment", description="Personal log category")
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    # Retention and compliance
    retention_until: datetime = Field(..., description="Record retention expiry")
    gdpr_compliant: bool = Field(default=True)
    
    # Personal log server integration
    telegram_topic_id: Optional[int] = Field(default=3, description="Payment & Transactions topic")
    personal_log_message_id: Optional[str] = Field(default=None)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceCreate(BaseModel):
    """Invoice creation request"""
    
    # Customer
    user_id: str = Field(..., description="Invoice recipient user ID")
    customer_email: Optional[str] = Field(default=None)
    
    # Invoice details
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    
    # Line items
    line_items: List[Dict[str, Any]] = Field(..., min_items=1, max_items=50)
    
    # Pricing
    subtotal: Decimal = Field(..., gt=0)
    tax_amount: Optional[Decimal] = Field(default=None, ge=0)
    discount_amount: Optional[Decimal] = Field(default=None, ge=0)
    total_amount: Decimal = Field(..., gt=0)
    currency: CurrencyCode = Field(default=CurrencyCode.XTR)
    
    # Payment terms
    payment_method: PaymentMethod
    due_date: Optional[datetime] = Field(default=None)
    payment_terms_days: int = Field(default=30, ge=1, le=365)
    
    # Options
    auto_send: bool = Field(default=True)
    require_payment: bool = Field(default=True)
    
    # Privacy
    log_to_personal_server: bool = Field(default=True)
    encrypt_invoice_data: bool = Field(default=True)
    
    # Context
    correlation_id: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class InvoiceResponse(BaseModel):
    """Invoice creation response"""
    
    success: bool
    invoice_id: str
    
    # Invoice access
    invoice_url: Optional[str] = Field(default=None)
    invoice_pdf_url: Optional[str] = Field(default=None)
    payment_url: Optional[str] = Field(default=None)
    
    # Telegram integration
    telegram_invoice_message: Optional[str] = Field(default=None)
    
    # Status
    status: str = Field(default="draft")
    due_date: datetime
    
    # Privacy compliance
    personal_log_recorded: bool = Field(default=False)
    invoice_data_encrypted: bool = Field(default=False)
    
    # Error handling
    error: Optional[str] = Field(default=None)
    error_code: Optional[str] = Field(default=None)
    
    request_id: str = Field(..., description="Unique request identifier")


class PaymentHealthResponse(BaseModel):
    """Payment module health response"""
    
    status: str = Field(..., description="Module status")
    
    # Payment processing stats
    payments_processed_last_hour: int = Field(ge=0)
    total_revenue_last_24h: Decimal = Field(ge=0)
    average_payment_amount: Optional[Decimal] = Field(default=None, ge=0)
    
    # Success rates
    payment_success_rate: Optional[float] = Field(default=None, ge=0, le=1)
    telegram_stars_success_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Revenue sharing stats
    developer_payouts_pending: int = Field(ge=0)
    total_developer_revenue_last_30d: Decimal = Field(ge=0)
    
    # Subscription stats
    active_subscriptions: int = Field(ge=0)
    subscription_renewal_rate: Optional[float] = Field(default=None, ge=0, le=1)
    
    # Personal log integration
    billing_logs_recorded_last_hour: int = Field(ge=0)
    encrypted_billing_records: int = Field(ge=0)
    
    # Processing performance
    average_payment_processing_time_ms: Optional[int] = Field(default=None, ge=0)
    pending_payments: int = Field(ge=0)
    failed_payments_last_hour: int = Field(ge=0)
    
    # Compliance
    gdpr_compliant: bool = Field(default=True)
    billing_data_retention_compliant: bool = Field(default=True)
    
    # Integration status
    telegram_stars_api_accessible: bool = Field(default=True)
    payment_webhooks_healthy: bool = Field(default=True)
    revenue_sharing_operational: bool = Field(default=True)
    
    last_check: datetime = Field(..., description="Last health check timestamp")