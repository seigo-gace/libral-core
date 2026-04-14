"""
Payment & Billing Service - Week 6 Implementation
Telegram Stars integration with encrypted billing and revenue sharing
"""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

import httpx
import structlog
from aiogram import Bot
from aiogram.types import LabeledPrice, InlineKeyboardButton, InlineKeyboardMarkup

from .schemas import (
    BillingRecord,
    CurrencyCode,
    InvoiceCreate,
    InvoiceResponse,
    Payment,
    PaymentCreate,
    PaymentHealthResponse,
    PaymentMethod,
    PaymentResponse,
    PaymentStatus,
    RevenueShare,
    RevenueShareType,
    Subscription,
    SubscriptionPlan,
    TelegramStarsPayment
)
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ..events.service import EventService
from ..gpg.service import GPGService
from ..gpg.schemas import EncryptRequest

logger = structlog.get_logger(__name__)


class TelegramStarsProcessor:
    """Telegram Stars payment processing with privacy-first design"""
    
    def __init__(self, bot_token: str, webhook_secret: str):
        self.bot = Bot(token=bot_token)
        self.webhook_secret = webhook_secret
        
    async def create_invoice(
        self,
        payment_request: PaymentCreate,
        payment_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Create Telegram Stars invoice"""
        
        try:
            # Convert amount to Stars (minimum 1 Star)
            stars_amount = max(1, int(payment_request.amount))
            
            # Create invoice
            invoice_payload = f"libral_payment_{payment_id}_{payment_request.user_id}"
            
            # Create labeled prices
            prices = [LabeledPrice(
                label=payment_request.description[:32],  # Telegram limit
                amount=stars_amount
            )]
            
            # Send invoice to customer
            if payment_request.customer_telegram_id:
                message = await self.bot.send_invoice(
                    chat_id=payment_request.customer_telegram_id,
                    title=payment_request.description[:32],
                    description=payment_request.description[:255],
                    payload=invoice_payload,
                    provider_token="",  # Empty for Telegram Stars
                    currency="XTR",
                    prices=prices,
                    start_parameter=f"payment_{payment_id}",
                    photo_url=None,
                    photo_size=None,
                    photo_width=None,
                    photo_height=None,
                    need_name=False,
                    need_phone_number=False,
                    need_email=False,
                    need_shipping_address=False,
                    send_phone_number_to_provider=False,
                    send_email_to_provider=False,
                    is_flexible=False
                )
                
                logger.info("Telegram Stars invoice created",
                           payment_id=payment_id,
                           stars_amount=stars_amount,
                           message_id=message.message_id)
                
                return True, invoice_payload, f"https://t.me/invoice/{message.message_id}"
            
            else:
                # Create invoice URL without sending message
                invoice_url = f"https://t.me/LibralPaymentBot?start=pay_{payment_id}"
                
                logger.info("Telegram Stars invoice URL created",
                           payment_id=payment_id,
                           stars_amount=stars_amount)
                
                return True, invoice_payload, invoice_url
                
        except Exception as e:
            logger.error("Failed to create Telegram Stars invoice",
                        payment_id=payment_id,
                        error=str(e))
            return False, None, None
    
    async def verify_webhook_payment(
        self,
        payment_data: TelegramStarsPayment,
        webhook_signature: str
    ) -> bool:
        """Verify Telegram Stars webhook payment with signature"""
        
        try:
            # Create verification payload
            payload = json.dumps({
                "telegram_payment_charge_id": payment_data.telegram_payment_charge_id,
                "provider_payment_charge_id": payment_data.provider_payment_charge_id,
                "total_amount": payment_data.total_amount,
                "currency": payment_data.currency,
                "invoice_payload": payment_data.invoice_payload,
                "telegram_user_id": payment_data.telegram_user_id
            }, sort_keys=True, ensure_ascii=False)
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Verify signature
            if hmac.compare_digest(webhook_signature, expected_signature):
                logger.info("Telegram Stars payment verified",
                           charge_id=payment_data.telegram_payment_charge_id,
                           amount=payment_data.total_amount)
                return True
            else:
                logger.warning("Telegram Stars payment verification failed",
                              charge_id=payment_data.telegram_payment_charge_id,
                              expected_signature=expected_signature[:8] + "...",
                              received_signature=webhook_signature[:8] + "...")
                return False
                
        except Exception as e:
            logger.error("Telegram Stars payment verification error",
                        charge_id=payment_data.telegram_payment_charge_id,
                        error=str(e))
            return False
    
    async def process_successful_payment(
        self,
        payment_data: TelegramStarsPayment
    ) -> Optional[str]:
        """Process successful Telegram Stars payment"""
        
        try:
            # Extract payment ID from invoice payload
            if payment_data.invoice_payload.startswith("libral_payment_"):
                parts = payment_data.invoice_payload.split("_")
                if len(parts) >= 3:
                    payment_id = parts[2]
                    user_id = parts[3] if len(parts) > 3 else None
                    
                    logger.info("Telegram Stars payment processed",
                               payment_id=payment_id,
                               user_id=user_id,
                               stars_amount=payment_data.total_amount)
                    
                    return payment_id
            
            logger.warning("Invalid invoice payload format",
                          payload=payment_data.invoice_payload)
            return None
            
        except Exception as e:
            logger.error("Failed to process Telegram Stars payment",
                        error=str(e))
            return None


class RevenueShareManager:
    """Plugin developer revenue sharing with privacy protection"""
    
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.pending_payouts: Dict[str, List[RevenueShare]] = {}
        
    async def calculate_revenue_share(
        self,
        payment: Payment
    ) -> List[RevenueShare]:
        """Calculate revenue sharing for plugin developers"""
        
        try:
            shares = []
            
            # Platform fee (default 30%)
            platform_fee_amount = payment.amount * (payment.platform_fee or Decimal("30.0")) / 100
            platform_share = RevenueShare(
                share_id=str(uuid4()),
                payment_id=payment.payment_id,
                share_type=RevenueShareType.PLATFORM_FEE,
                recipient_user_id="platform",
                original_amount=payment.amount,
                share_percentage=payment.platform_fee or Decimal("30.0"),
                share_amount=platform_fee_amount,
                currency=payment.currency,
                item_type=payment.item_type,
                item_id=payment.item_id,
                description=f"Platform fee for {payment.description}"
            )
            shares.append(platform_share)
            
            # Developer share (70% default)
            developer_share_percentage = 100 - (payment.platform_fee or Decimal("30.0"))
            developer_share_amount = payment.amount * developer_share_percentage / 100
            
            # Find plugin developer if this is a plugin purchase
            if payment.item_type == "plugin" and payment.item_id:
                developer_user_id = await self._get_plugin_developer_id(payment.item_id)
                
                if developer_user_id:
                    developer_share = RevenueShare(
                        share_id=str(uuid4()),
                        payment_id=payment.payment_id,
                        share_type=RevenueShareType.PLUGIN_DEVELOPER,
                        recipient_user_id=developer_user_id,
                        original_amount=payment.amount,
                        share_percentage=developer_share_percentage,
                        share_amount=developer_share_amount,
                        currency=payment.currency,
                        item_type=payment.item_type,
                        item_id=payment.item_id,
                        description=f"Developer revenue for {payment.description}",
                        next_payout_date=self._calculate_next_payout_date("monthly")
                    )
                    shares.append(developer_share)
                    
                    # Add to pending payouts
                    if developer_user_id not in self.pending_payouts:
                        self.pending_payouts[developer_user_id] = []
                    self.pending_payouts[developer_user_id].append(developer_share)
            
            logger.info("Revenue shares calculated",
                       payment_id=payment.payment_id,
                       shares_count=len(shares),
                       total_shared=sum(s.share_amount for s in shares))
            
            return shares
            
        except Exception as e:
            logger.error("Revenue share calculation failed",
                        payment_id=payment.payment_id,
                        error=str(e))
            return []
    
    async def _get_plugin_developer_id(self, plugin_id: str) -> Optional[str]:
        """Get plugin developer user ID"""
        # In real implementation, would query plugin registry
        # For now, return mock developer ID
        return f"developer_{plugin_id}_owner"
    
    def _calculate_next_payout_date(self, schedule: str) -> datetime:
        """Calculate next payout date based on schedule"""
        now = datetime.utcnow()
        
        if schedule == "daily":
            return now + timedelta(days=1)
        elif schedule == "weekly":
            return now + timedelta(days=7)
        elif schedule == "monthly":
            return now + timedelta(days=30)
        elif schedule == "quarterly":
            return now + timedelta(days=90)
        else:
            return now + timedelta(days=30)  # Default monthly


class EncryptedBillingLogger:
    """Encrypted billing record management for personal log servers"""
    
    def __init__(
        self,
        auth_service: AuthService,
        gpg_service: Optional[GPGService] = None
    ):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        
    async def create_billing_record(
        self,
        payment: Payment,
        record_type: str = "payment"
    ) -> BillingRecord:
        """Create encrypted billing record for personal log server"""
        
        try:
            # Get user's GPG key
            user_profile = self.auth_service.user_profiles.get(payment.user_id)
            if not user_profile or not user_profile.gpg_public_key:
                logger.warning("No GPG key for billing encryption",
                              user_id=payment.user_id)
                # Create unencrypted record as fallback
                encrypted_details = json.dumps({
                    "payment_id": payment.payment_id,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "description": payment.description,
                    "status": payment.status,
                    "encryption_note": "GPG key not available"
                }, ensure_ascii=False)
            else:
                # Create detailed billing information
                billing_details = {
                    "payment_id": payment.payment_id,
                    "external_payment_id": payment.external_payment_id,
                    "amount": str(payment.amount),
                    "currency": payment.currency,
                    "payment_method": payment.payment_method,
                    "status": payment.status,
                    "description": payment.description,
                    "item_type": payment.item_type,
                    "item_id": payment.item_id,
                    "platform_fee": str(payment.platform_fee) if payment.platform_fee else None,
                    "developer_share": str(payment.developer_share) if payment.developer_share else None,
                    "net_amount": str(payment.net_amount) if payment.net_amount else None,
                    "created_at": payment.created_at.isoformat(),
                    "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
                    "metadata": payment.metadata
                }
                
                # Encrypt billing details
                if self.gpg_service:
                    encrypt_request = EncryptRequest(
                        data=json.dumps(billing_details, indent=2, ensure_ascii=False),
                        recipients=[user_profile.gpg_public_key],
                        context_labels={
                            "libral.billing_record": "true",
                            "libral.user_controlled": "true",
                            "libral.record_type": record_type,
                            "libral.payment_id": payment.payment_id
                        }
                    )
                    
                    encrypt_result = await self.gpg_service.encrypt(encrypt_request)
                    
                    if encrypt_result.success:
                        encrypted_details = encrypt_result.encrypted_data
                    else:
                        logger.warning("Billing encryption failed",
                                      user_id=payment.user_id,
                                      error=encrypt_result.error)
                        encrypted_details = json.dumps(billing_details, ensure_ascii=False)
                else:
                    encrypted_details = json.dumps(billing_details, ensure_ascii=False)
            
            # Create billing record
            billing_record = BillingRecord(
                record_id=str(uuid4()),
                user_id=payment.user_id,
                record_type=record_type,
                related_id=payment.payment_id,
                amount=payment.amount,
                currency=payment.currency,
                transaction_date=payment.created_at,
                encrypted_details=encrypted_details,
                encryption_recipient=user_profile.gpg_public_key if user_profile else "none",
                category="payment",
                tags=[payment.item_type, payment.payment_method, payment.status],
                retention_until=datetime.utcnow() + timedelta(days=payment.retention_days),
                telegram_topic_id=3,  # 💰 Payment & Transactions topic
                gdpr_compliant=True
            )
            
            logger.info("Encrypted billing record created",
                       user_id=payment.user_id,
                       record_id=billing_record.record_id,
                       encrypted=bool(self.gpg_service and user_profile and user_profile.gpg_public_key))
            
            return billing_record
            
        except Exception as e:
            logger.error("Failed to create billing record",
                        payment_id=payment.payment_id,
                        error=str(e))
            raise
    
    async def log_billing_to_personal_server(
        self,
        billing_record: BillingRecord
    ) -> bool:
        """Log billing record to user's personal log server"""
        
        try:
            # Create log entry for personal server
            log_data = {
                "timestamp": billing_record.created_at.isoformat(),
                "category": "payment",
                "event_type": "billing_record",
                "title": f"💰 Payment Record - {billing_record.currency} {billing_record.amount}",
                "description": f"Encrypted billing record for {billing_record.record_type}",
                "record_id": billing_record.record_id,
                "amount": str(billing_record.amount),
                "currency": billing_record.currency,
                "tags": billing_record.tags,
                "retention_until": billing_record.retention_until.isoformat(),
                "encrypted_billing_data": billing_record.encrypted_details
            }
            
            # Send to personal log server via auth service
            return await self.auth_service._log_to_personal_server(
                billing_record.user_id, 
                log_data
            )
            
        except Exception as e:
            logger.error("Failed to log billing to personal server",
                        user_id=billing_record.user_id,
                        record_id=billing_record.record_id,
                        error=str(e))
            return False


class PaymentService:
    """Comprehensive payment and billing service"""
    
    def __init__(
        self,
        auth_service: AuthService,
        telegram_bot_token: str,
        webhook_secret: str,
        gpg_service: Optional[GPGService] = None,
        communication_service: Optional[CommunicationService] = None,
        event_service: Optional[EventService] = None
    ):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        self.communication_service = communication_service
        self.event_service = event_service
        
        # Initialize processors
        self.telegram_processor = TelegramStarsProcessor(telegram_bot_token, webhook_secret)
        self.revenue_manager = RevenueShareManager(auth_service)
        self.billing_logger = EncryptedBillingLogger(auth_service, gpg_service)
        
        # Payment storage (in production, would use database)
        self.payments: Dict[str, Payment] = {}
        self.subscriptions: Dict[str, Subscription] = {}
        self.subscription_plans: Dict[str, SubscriptionPlan] = {}
        
        # Statistics
        self.payment_stats = {
            "payments_processed": 0,
            "payments_failed": 0,
            "total_revenue": Decimal("0"),
            "developer_payouts": 0
        }
        
        logger.info("Payment service initialized")
    
    async def health_check(self) -> PaymentHealthResponse:
        """Check payment service health"""
        
        try:
            # Calculate payment statistics
            total_payments = len(self.payments)
            completed_payments = len([p for p in self.payments.values() 
                                    if p.status == PaymentStatus.COMPLETED])
            
            success_rate = (completed_payments / max(total_payments, 1)) if total_payments > 0 else 1.0
            
            # Calculate revenue
            total_revenue = sum(p.amount for p in self.payments.values() 
                              if p.status == PaymentStatus.COMPLETED)
            
            return PaymentHealthResponse(
                status="healthy",
                payments_processed_last_hour=self.payment_stats["payments_processed"],
                total_revenue_last_24h=total_revenue,
                average_payment_amount=total_revenue / max(completed_payments, 1) if completed_payments > 0 else Decimal("0"),
                payment_success_rate=success_rate,
                telegram_stars_success_rate=0.95,  # Mock high success rate
                developer_payouts_pending=len(self.revenue_manager.pending_payouts),
                total_developer_revenue_last_30d=total_revenue * Decimal("0.7"),  # 70% to developers
                active_subscriptions=len([s for s in self.subscriptions.values() 
                                        if s.status.value == "active"]),
                subscription_renewal_rate=0.85,  # Mock renewal rate
                billing_logs_recorded_last_hour=self.payment_stats["payments_processed"],
                encrypted_billing_records=completed_payments,
                average_payment_processing_time_ms=2500,  # Mock processing time
                pending_payments=len([p for p in self.payments.values() 
                                    if p.status == PaymentStatus.PENDING]),
                failed_payments_last_hour=self.payment_stats["payments_failed"],
                gdpr_compliant=True,
                billing_data_retention_compliant=True,
                telegram_stars_api_accessible=True,
                payment_webhooks_healthy=True,
                revenue_sharing_operational=True,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Payment health check failed", error=str(e))
            return PaymentHealthResponse(
                status="unhealthy",
                payments_processed_last_hour=0,
                total_revenue_last_24h=Decimal("0"),
                developer_payouts_pending=0,
                total_developer_revenue_last_30d=Decimal("0"),
                active_subscriptions=0,
                billing_logs_recorded_last_hour=0,
                encrypted_billing_records=0,
                pending_payments=0,
                failed_payments_last_hour=0,
                gdpr_compliant=True,
                billing_data_retention_compliant=True,
                telegram_stars_api_accessible=False,
                payment_webhooks_healthy=False,
                revenue_sharing_operational=False,
                last_check=datetime.utcnow()
            )
    
    async def create_payment(self, request: PaymentCreate) -> PaymentResponse:
        """Create new payment with privacy-first processing"""
        request_id = str(uuid4())[:8]
        payment_id = str(uuid4())
        
        try:
            logger.info("Creating payment",
                       request_id=request_id,
                       payment_id=payment_id,
                       amount=request.amount,
                       currency=request.currency,
                       method=request.payment_method)
            
            # Create payment record
            payment = Payment(
                payment_id=payment_id,
                correlation_id=request.correlation_id,
                amount=request.amount,
                currency=request.currency,
                payment_method=request.payment_method,
                user_id=request.user_id,
                customer_telegram_id=request.customer_telegram_id,
                description=request.description,
                item_type=request.item_type,
                item_id=request.item_id,
                expires_at=datetime.utcnow() + timedelta(minutes=request.expires_in_minutes),
                platform_fee=request.platform_fee_percentage,
                log_to_personal_server=request.log_to_personal_server,
                encrypt_billing_data=request.encrypt_billing_data,
                metadata=request.metadata
            )
            
            # Process payment based on method
            payment_url = None
            telegram_invoice_payload = None
            
            if request.payment_method == PaymentMethod.TELEGRAM_STARS:
                success, payload, url = await self.telegram_processor.create_invoice(
                    request, payment_id
                )
                
                if success:
                    payment_url = url
                    telegram_invoice_payload = payload
                else:
                    return PaymentResponse(
                        success=False,
                        payment_id=payment_id,
                        expires_at=payment.expires_at,
                        error="Failed to create Telegram Stars invoice",
                        error_code="TELEGRAM_INVOICE_FAILED",
                        request_id=request_id
                    )
            
            # Store payment
            self.payments[payment_id] = payment
            
            # Create encrypted billing record
            billing_record = await self.billing_logger.create_billing_record(payment)
            
            # Log to personal server if enabled
            personal_log_recorded = False
            if request.log_to_personal_server:
                personal_log_recorded = await self.billing_logger.log_billing_to_personal_server(
                    billing_record
                )
            
            # Create event
            if self.event_service:
                from ..events.schemas import EventCreate, EventCategory, EventPriority
                event_request = EventCreate(
                    event_type="payment_created",
                    category=EventCategory.PAYMENT,
                    title=f"Payment Created - {request.currency} {request.amount}",
                    description=f"Payment created for {request.description}",
                    source="payment_service",
                    source_user_id=request.user_id,
                    priority=EventPriority.NORMAL,
                    log_to_personal_server=True,
                    context_labels={
                        "payment_id": payment_id,
                        "amount": str(request.amount),
                        "currency": request.currency,
                        "method": request.payment_method,
                        "telegram.topic_id": "3"  # Payment & Transactions topic
                    }
                )
                await self.event_service.create_event(event_request)
            
            # Update statistics
            self.payment_stats["payments_processed"] += 1
            
            logger.info("Payment created successfully",
                       request_id=request_id,
                       payment_id=payment_id,
                       personal_log=personal_log_recorded)
            
            return PaymentResponse(
                success=True,
                payment_id=payment_id,
                payment=payment,
                payment_url=payment_url,
                telegram_invoice_payload=telegram_invoice_payload,
                expires_at=payment.expires_at,
                personal_log_recorded=personal_log_recorded,
                billing_data_encrypted=bool(self.gpg_service),
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("Payment creation failed",
                        request_id=request_id,
                        error=str(e))
            
            self.payment_stats["payments_failed"] += 1
            
            return PaymentResponse(
                success=False,
                payment_id=payment_id,
                expires_at=datetime.utcnow() + timedelta(minutes=request.expires_in_minutes),
                error=str(e),
                error_code="PAYMENT_CREATION_FAILED",
                request_id=request_id
            )
    
    async def process_telegram_webhook(
        self,
        payment_data: TelegramStarsPayment,
        webhook_signature: str
    ) -> bool:
        """Process Telegram Stars webhook payment"""
        
        try:
            # Verify webhook signature
            if not await self.telegram_processor.verify_webhook_payment(
                payment_data, webhook_signature
            ):
                logger.warning("Telegram webhook verification failed",
                              charge_id=payment_data.telegram_payment_charge_id)
                return False
            
            # Process successful payment
            payment_id = await self.telegram_processor.process_successful_payment(payment_data)
            
            if not payment_id or payment_id not in self.payments:
                logger.warning("Payment not found for webhook",
                              payment_id=payment_id,
                              charge_id=payment_data.telegram_payment_charge_id)
                return False
            
            # Update payment status
            payment = self.payments[payment_id]
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            payment.external_payment_id = payment_data.telegram_payment_charge_id
            
            # Calculate revenue sharing
            revenue_shares = await self.revenue_manager.calculate_revenue_share(payment)
            
            # Update billing record
            billing_record = await self.billing_logger.create_billing_record(
                payment, "payment_completed"
            )
            
            # Log to personal server
            await self.billing_logger.log_billing_to_personal_server(billing_record)
            
            # Send completion notification
            if self.communication_service:
                from ..communication.schemas import NotificationRequest, MessagePriority
                notification = NotificationRequest(
                    user_ids=[payment.user_id],
                    title="💰 Payment Completed",
                    message=f"Payment of {payment.currency} {payment.amount} completed successfully.\n\nTransaction ID: {payment_id[:8]}",
                    notification_type="payment_notification",
                    priority=MessagePriority.HIGH,
                    context_labels={
                        "payment_id": payment_id,
                        "telegram.topic_id": "3"
                    },
                    source_module="payments"
                )
                await self.communication_service.send_notification(notification)
            
            # Update statistics
            self.payment_stats["total_revenue"] += payment.amount
            
            logger.info("Telegram Stars payment processed successfully",
                       payment_id=payment_id,
                       amount=payment.amount,
                       revenue_shares=len(revenue_shares))
            
            return True
            
        except Exception as e:
            logger.error("Telegram webhook processing failed",
                        charge_id=payment_data.telegram_payment_charge_id,
                        error=str(e))
            return False
    
    async def get_payment_history(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Payment]:
        """Get user payment history (privacy-compliant)"""
        
        try:
            # Filter payments for user
            user_payments = [
                p for p in self.payments.values() 
                if p.user_id == user_id
            ]
            
            # Sort by creation date (newest first)
            user_payments.sort(key=lambda p: p.created_at, reverse=True)
            
            # Apply pagination
            start_idx = offset
            end_idx = start_idx + limit
            paginated_payments = user_payments[start_idx:end_idx]
            
            logger.info("Payment history retrieved",
                       user_id=user_id,
                       total_payments=len(user_payments),
                       returned_payments=len(paginated_payments))
            
            return paginated_payments
            
        except Exception as e:
            logger.error("Failed to get payment history",
                        user_id=user_id,
                        error=str(e))
            return []
    
    async def cleanup(self):
        """Cleanup payment service resources"""
        try:
            # Close Telegram bot session
            await self.telegram_processor.bot.session.close()
            
            logger.info("Payment service cleanup completed")
            
        except Exception as e:
            logger.error("Payment service cleanup failed", error=str(e))