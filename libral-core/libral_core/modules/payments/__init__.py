"""
Payment & Billing Module - Week 6 Implementation
Telegram Stars integration with encrypted billing logs and revenue sharing

Features:
- Telegram Stars payment processing with webhook validation
- Encrypted billing history in personal log servers
- Plugin developer revenue sharing with automatic distribution
- GDPR-compliant payment data handling with user control
- Real-time payment notifications with GPG encryption
- Subscription management with personal server integration
- Multi-currency support with privacy-first billing
"""

from .service import PaymentService
from .schemas import (
    Payment,
    PaymentCreate,
    PaymentResponse,
    PaymentStatus,
    PaymentMethod,
    Subscription,
    SubscriptionPlan,
    RevenueShare,
    TelegramStarsPayment,
    BillingRecord,
    InvoiceCreate,
    InvoiceResponse
)

__all__ = [
    "PaymentService",
    "Payment",
    "PaymentCreate",
    "PaymentResponse",
    "PaymentStatus",
    "PaymentMethod",
    "Subscription",
    "SubscriptionPlan",
    "RevenueShare",
    "TelegramStarsPayment",
    "BillingRecord",
    "InvoiceCreate",
    "InvoiceResponse"
]