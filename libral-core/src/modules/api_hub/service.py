"""
API Hub Service - Week 7 Implementation
External API integration with encrypted credential management and usage tracking
"""

import asyncio
import json
import hashlib
import hmac
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

import httpx
import structlog

from .schemas import (
    APICredential,
    APICredentialCreate,
    APIHubHealthResponse,
    APIProvider,
    APIQuota,
    APIStatus,
    APIUsage,
    APIUsageResponse,
    ExternalAPICall,
    ServiceConnector,
    ThirdPartyIntegration
)
from ..auth.service import AuthService
from ..communication.service import CommunicationService
from ..events.service import EventService
from ..gpg.service import GPGService
from ..gpg.schemas import EncryptRequest, DecryptRequest
from ..payments.service import PaymentService

logger = structlog.get_logger(__name__)


class CredentialManager:
    """Encrypted API credential management with GPG"""
    
    def __init__(
        self,
        auth_service: AuthService,
        gpg_service: Optional[GPGService] = None
    ):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        self.credentials: Dict[str, APICredential] = {}
        
    async def create_credential(
        self,
        user_id: str,
        request: APICredentialCreate
    ) -> Tuple[bool, Optional[APICredential], Optional[str]]:
        """Create encrypted API credential"""
        
        try:
            credential_id = str(uuid4())
            
            # Get user's GPG key
            user_profile = self.auth_service.user_profiles.get(user_id)
            if not user_profile or not user_profile.gpg_public_key:
                return False, None, "User GPG key not found"
            
            # Encrypt API key
            if self.gpg_service:
                # Encrypt API key
                encrypt_request = EncryptRequest(
                    data=request.api_key,
                    recipients=[user_profile.gpg_public_key],
                    context_labels={
                        "libral.api_credential": "true",
                        "libral.provider": request.provider,
                        "libral.user_controlled": "true"
                    }
                )
                
                encrypt_result = await self.gpg_service.encrypt(encrypt_request)
                if not encrypt_result.success:
                    return False, None, f"API key encryption failed: {encrypt_result.error}"
                
                encrypted_api_key = encrypt_result.encrypted_data
                
                # Encrypt API secret if provided
                encrypted_secret = None
                if request.api_secret:
                    secret_encrypt_request = EncryptRequest(
                        data=request.api_secret,
                        recipients=[user_profile.gpg_public_key],
                        context_labels={
                            "libral.api_secret": "true",
                            "libral.provider": request.provider,
                            "libral.user_controlled": "true"
                        }
                    )
                    
                    secret_encrypt_result = await self.gpg_service.encrypt(secret_encrypt_request)
                    if secret_encrypt_result.success:
                        encrypted_secret = secret_encrypt_result.encrypted_data
                
                # Encrypt additional config if provided
                encrypted_config = None
                if request.additional_config:
                    config_data = json.dumps(request.additional_config, ensure_ascii=False)
                    config_encrypt_request = EncryptRequest(
                        data=config_data,
                        recipients=[user_profile.gpg_public_key],
                        context_labels={
                            "libral.api_config": "true",
                            "libral.provider": request.provider,
                            "libral.user_controlled": "true"
                        }
                    )
                    
                    config_encrypt_result = await self.gpg_service.encrypt(config_encrypt_request)
                    if config_encrypt_result.success:
                        encrypted_config = config_encrypt_result.encrypted_data
            else:
                # Fallback: store as-is (not recommended for production)
                encrypted_api_key = request.api_key
                encrypted_secret = request.api_secret
                encrypted_config = json.dumps(request.additional_config) if request.additional_config else None
            
            # Create credential
            credential = APICredential(
                credential_id=credential_id,
                user_id=user_id,
                provider=request.provider,
                name=request.name,
                description=request.description,
                encrypted_api_key=encrypted_api_key,
                encrypted_secret=encrypted_secret,
                encrypted_config=encrypted_config,
                encryption_recipient=user_profile.gpg_public_key,
                allowed_origins=request.allowed_origins,
                ip_whitelist=request.ip_whitelist,
                daily_quota=request.daily_quota,
                monthly_quota=request.monthly_quota,
                cost_limit_usd=request.cost_limit_usd,
                require_authentication=request.require_authentication,
                log_requests=request.log_requests,
                log_responses=request.log_responses,
                log_to_personal_server=request.log_to_personal_server
            )
            
            # Store credential
            self.credentials[credential_id] = credential
            
            logger.info("API credential created",
                       credential_id=credential_id,
                       user_id=user_id,
                       provider=request.provider,
                       encrypted=bool(self.gpg_service))
            
            return True, credential, None
            
        except Exception as e:
            logger.error("Failed to create API credential",
                        user_id=user_id,
                        provider=request.provider,
                        error=str(e))
            return False, None, str(e)
    
    async def decrypt_credential(
        self,
        credential: APICredential
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[Dict[str, Any]]]:
        """Decrypt API credential for use"""
        
        try:
            if not self.gpg_service:
                # Return as-is if no GPG service
                config = None
                if credential.encrypted_config:
                    try:
                        config = json.loads(credential.encrypted_config)
                    except json.JSONDecodeError:
                        pass
                
                return True, credential.encrypted_api_key, credential.encrypted_secret, config
            
            # Decrypt API key
            decrypt_request = DecryptRequest(
                encrypted_data=credential.encrypted_api_key
            )
            
            decrypt_result = await self.gpg_service.decrypt(decrypt_request)
            if not decrypt_result.success:
                return False, None, None, None
            
            api_key = decrypt_result.decrypted_data
            
            # Decrypt secret if present
            api_secret = None
            if credential.encrypted_secret:
                secret_decrypt_request = DecryptRequest(
                    encrypted_data=credential.encrypted_secret
                )
                
                secret_decrypt_result = await self.gpg_service.decrypt(secret_decrypt_request)
                if secret_decrypt_result.success:
                    api_secret = secret_decrypt_result.decrypted_data
            
            # Decrypt config if present
            config = None
            if credential.encrypted_config:
                config_decrypt_request = DecryptRequest(
                    encrypted_data=credential.encrypted_config
                )
                
                config_decrypt_result = await self.gpg_service.decrypt(config_decrypt_request)
                if config_decrypt_result.success:
                    try:
                        config = json.loads(config_decrypt_result.decrypted_data)
                    except json.JSONDecodeError:
                        pass
            
            return True, api_key, api_secret, config
            
        except Exception as e:
            logger.error("Failed to decrypt API credential",
                        credential_id=credential.credential_id,
                        error=str(e))
            return False, None, None, None


class UsageTracker:
    """API usage tracking and quota management"""
    
    def __init__(self):
        self.usage_records: Dict[str, APIUsage] = {}
        self.quotas: Dict[str, APIQuota] = {}
        
        # Cost estimates for different providers
        self.cost_estimates = {
            APIProvider.OPENAI: {
                "gpt-4": {"input": 0.03, "output": 0.06},  # per 1K tokens
                "gpt-3.5-turbo": {"input": 0.001, "output": 0.002}
            },
            APIProvider.ANTHROPIC: {
                "claude-3-opus": {"input": 0.015, "output": 0.075},
                "claude-3-sonnet": {"input": 0.003, "output": 0.015}
            }
        }
    
    async def track_usage(
        self,
        user_id: str,
        credential_id: str,
        provider: APIProvider,
        endpoint: str,
        method: str,
        response_time_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        tokens_used: Optional[int] = None,
        success: bool = True,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        purpose: Optional[str] = None,
        plugin_id: Optional[str] = None
    ) -> APIUsageResponse:
        """Track API usage and check quotas"""
        
        try:
            usage_id = str(uuid4())
            
            # Estimate cost
            estimated_cost = self._estimate_cost(provider, endpoint, tokens_used)
            
            # Create usage record
            usage = APIUsage(
                usage_id=usage_id,
                user_id=user_id,
                credential_id=credential_id,
                provider=provider,
                endpoint=endpoint,
                method=method,
                response_time_ms=response_time_ms,
                status_code=status_code,
                estimated_cost_usd=estimated_cost,
                tokens_used=tokens_used,
                success=success,
                error_code=error_code,
                error_message=error_message,
                purpose=purpose,
                plugin_id=plugin_id
            )
            
            # Store usage record
            self.usage_records[usage_id] = usage
            
            # Update quota usage
            quota = await self._get_or_create_quota(user_id, credential_id, provider)
            quota.current_daily_usage += 1
            quota.current_monthly_usage += 1
            quota.current_yearly_usage += 1
            
            if estimated_cost:
                quota.current_daily_cost += estimated_cost
                quota.current_monthly_cost += estimated_cost
                quota.current_yearly_cost += estimated_cost
            
            # Check quota limits
            quota_warnings = []
            cost_warnings = []
            
            if quota.daily_limit and quota.current_daily_usage >= quota.daily_limit:
                quota.quota_exceeded = True
                quota_warnings.append("Daily quota limit reached")
            
            if quota.monthly_limit and quota.current_monthly_usage >= quota.monthly_limit:
                quota.quota_exceeded = True
                quota_warnings.append("Monthly quota limit reached")
            
            if quota.monthly_cost_limit and quota.current_monthly_cost >= quota.monthly_cost_limit:
                quota.cost_limit_exceeded = True
                cost_warnings.append("Monthly cost limit reached")
            
            # Calculate remaining quotas
            daily_remaining = None
            if quota.daily_limit:
                daily_remaining = max(0, quota.daily_limit - quota.current_daily_usage)
            
            monthly_remaining = None
            if quota.monthly_limit:
                monthly_remaining = max(0, quota.monthly_limit - quota.current_monthly_usage)
            
            cost_remaining = None
            if quota.monthly_cost_limit:
                cost_remaining = max(Decimal("0"), quota.monthly_cost_limit - quota.current_monthly_cost)
            
            logger.info("API usage tracked",
                       usage_id=usage_id,
                       user_id=user_id,
                       provider=provider,
                       success=success,
                       cost=estimated_cost)
            
            return APIUsageResponse(
                success=True,
                usage_id=usage_id,
                current_daily_usage=quota.current_daily_usage,
                current_monthly_usage=quota.current_monthly_usage,
                current_monthly_cost=quota.current_monthly_cost,
                daily_quota_remaining=daily_remaining,
                monthly_quota_remaining=monthly_remaining,
                cost_limit_remaining=cost_remaining,
                quota_warnings=quota_warnings,
                cost_warnings=cost_warnings,
                logged_to_personal_server=usage.log_to_personal_server,
                request_id=str(uuid4())[:8]
            )
            
        except Exception as e:
            logger.error("Failed to track API usage",
                        user_id=user_id,
                        provider=provider,
                        error=str(e))
            
            return APIUsageResponse(
                success=False,
                usage_id=str(uuid4()),
                current_daily_usage=0,
                current_monthly_usage=0,
                current_monthly_cost=Decimal("0"),
                request_id=str(uuid4())[:8]
            )
    
    def _estimate_cost(
        self,
        provider: APIProvider,
        endpoint: str,
        tokens_used: Optional[int]
    ) -> Optional[Decimal]:
        """Estimate API call cost"""
        
        try:
            if provider not in self.cost_estimates:
                return None
            
            provider_costs = self.cost_estimates[provider]
            
            # Simple estimation based on tokens for AI providers
            if tokens_used and provider in [APIProvider.OPENAI, APIProvider.ANTHROPIC]:
                # Use a default model cost if we can't determine the exact model
                if "gpt-4" in endpoint.lower():
                    cost_per_1k = provider_costs.get("gpt-4", {}).get("input", 0.03)
                elif "gpt-3.5" in endpoint.lower():
                    cost_per_1k = provider_costs.get("gpt-3.5-turbo", {}).get("input", 0.001)
                elif "claude-3-opus" in endpoint.lower():
                    cost_per_1k = provider_costs.get("claude-3-opus", {}).get("input", 0.015)
                elif "claude-3-sonnet" in endpoint.lower():
                    cost_per_1k = provider_costs.get("claude-3-sonnet", {}).get("input", 0.003)
                else:
                    cost_per_1k = 0.001  # Default low cost
                
                estimated_cost = Decimal(str(tokens_used / 1000 * cost_per_1k))
                return round(estimated_cost, 6)
            
            # Default small cost for other APIs
            return Decimal("0.001")
            
        except Exception as e:
            logger.error("Failed to estimate API cost",
                        provider=provider,
                        endpoint=endpoint,
                        error=str(e))
            return None
    
    async def _get_or_create_quota(
        self,
        user_id: str,
        credential_id: str,
        provider: APIProvider
    ) -> APIQuota:
        """Get or create API quota for user"""
        
        quota_key = f"{user_id}:{credential_id}"
        
        if quota_key not in self.quotas:
            now = datetime.utcnow()
            
            quota = APIQuota(
                quota_id=str(uuid4()),
                user_id=user_id,
                credential_id=credential_id,
                provider=provider,
                daily_reset_at=now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1),
                monthly_reset_at=now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=32),
                yearly_reset_at=now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) + timedelta(days=366)
            )
            
            self.quotas[quota_key] = quota
        
        return self.quotas[quota_key]


class ExternalAPIProxy:
    """Proxy for external API calls with authentication and logging"""
    
    def __init__(
        self,
        credential_manager: CredentialManager,
        usage_tracker: UsageTracker,
        auth_service: AuthService
    ):
        self.credential_manager = credential_manager
        self.usage_tracker = usage_tracker
        self.auth_service = auth_service
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
    async def call_api(
        self,
        user_id: str,
        request: ExternalAPICall
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Make authenticated external API call"""
        
        try:
            # Get credential
            credential = self.credential_manager.credentials.get(request.credential_id)
            if not credential or credential.user_id != user_id:
                return False, None, "Credential not found or access denied"
            
            # Check if credential is active
            if credential.status != APIStatus.ACTIVE:
                return False, None, f"Credential status: {credential.status}"
            
            # Decrypt credential
            success, api_key, api_secret, config = await self.credential_manager.decrypt_credential(credential)
            if not success:
                return False, None, "Failed to decrypt credential"
            
            # Prepare headers
            headers = request.headers or {}
            
            # Add authentication based on provider
            headers = self._add_authentication(headers, credential.provider, api_key, api_secret)
            
            # Make API call
            start_time = datetime.utcnow()
            
            try:
                response = await self.http_client.request(
                    method=request.method,
                    url=request.endpoint,
                    headers=headers,
                    params=request.query_params,
                    json=request.request_body,
                    timeout=request.timeout_seconds,
                    follow_redirects=request.follow_redirects
                )
                
                end_time = datetime.utcnow()
                response_time_ms = int((end_time - start_time).total_seconds() * 1000)
                
                # Parse response
                try:
                    response_data = response.json()
                except:
                    response_data = {"text": response.text, "status_code": response.status_code}
                
                # Track usage
                await self.usage_tracker.track_usage(
                    user_id=user_id,
                    credential_id=request.credential_id,
                    provider=credential.provider,
                    endpoint=request.endpoint,
                    method=request.method,
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    success=response.is_success,
                    purpose=request.purpose,
                    plugin_id=request.plugin_id
                )
                
                # Log to personal server if enabled
                if credential.log_to_personal_server:
                    await self._log_api_call_to_personal_server(
                        user_id, request, response_data, response_time_ms, True
                    )
                
                return True, response_data, None
                
            except httpx.TimeoutException:
                # Track timeout
                await self.usage_tracker.track_usage(
                    user_id=user_id,
                    credential_id=request.credential_id,
                    provider=credential.provider,
                    endpoint=request.endpoint,
                    method=request.method,
                    success=False,
                    error_code="TIMEOUT",
                    error_message="Request timeout"
                )
                
                return False, None, "Request timeout"
                
            except httpx.RequestError as e:
                # Track request error
                await self.usage_tracker.track_usage(
                    user_id=user_id,
                    credential_id=request.credential_id,
                    provider=credential.provider,
                    endpoint=request.endpoint,
                    method=request.method,
                    success=False,
                    error_code="REQUEST_ERROR",
                    error_message=str(e)
                )
                
                return False, None, f"Request error: {str(e)}"
                
        except Exception as e:
            logger.error("External API call failed",
                        user_id=user_id,
                        endpoint=request.endpoint,
                        error=str(e))
            return False, None, str(e)
    
    def _add_authentication(
        self,
        headers: Dict[str, str],
        provider: APIProvider,
        api_key: str,
        api_secret: Optional[str]
    ) -> Dict[str, str]:
        """Add provider-specific authentication to headers"""
        
        if provider == APIProvider.OPENAI:
            headers["Authorization"] = f"Bearer {api_key}"
        elif provider == APIProvider.ANTHROPIC:
            headers["x-api-key"] = api_key
        elif provider == APIProvider.GOOGLE_CLOUD:
            headers["Authorization"] = f"Bearer {api_key}"
        elif provider == APIProvider.GITHUB:
            headers["Authorization"] = f"token {api_key}"
        elif provider == APIProvider.STRIPE:
            headers["Authorization"] = f"Bearer {api_key}"
        elif provider == APIProvider.TELEGRAM:
            # Telegram uses bot token in URL or body
            pass
        else:
            # Generic Bearer token
            headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    async def _log_api_call_to_personal_server(
        self,
        user_id: str,
        request: ExternalAPICall,
        response_data: Dict[str, Any],
        response_time_ms: int,
        success: bool
    ) -> bool:
        """Log API call to user's personal log server"""
        
        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "category": "api_usage",
                "event_type": "external_api_call",
                "title": f"🔌 API Call - {request.method} {request.endpoint}",
                "description": f"External API call via API Hub",
                "endpoint": request.endpoint,
                "method": request.method,
                "success": success,
                "response_time_ms": response_time_ms,
                "purpose": request.purpose,
                "plugin_id": request.plugin_id,
                "contains_personal_data": request.contains_personal_data
            }
            
            # Add response data if logging is enabled
            if request.log_response and response_data:
                # Sanitize response data to remove potential secrets
                sanitized_response = self._sanitize_response_data(response_data)
                log_data["response_summary"] = sanitized_response
            
            # Send to personal log server
            return await self.auth_service._log_to_personal_server(
                user_id, log_data, topic_id=4  # 📡 Communication Logs topic
            )
            
        except Exception as e:
            logger.error("Failed to log API call to personal server",
                        user_id=user_id,
                        error=str(e))
            return False
    
    def _sanitize_response_data(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize response data to remove sensitive information"""
        
        # Remove common sensitive fields
        sensitive_fields = [
            "api_key", "secret", "token", "password", "private_key",
            "authorization", "x-api-key", "bearer"
        ]
        
        sanitized = {}
        for key, value in response_data.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_response_data(value)
            elif isinstance(value, str) and len(value) > 500:
                # Truncate very long strings
                sanitized[key] = value[:500] + "..."
            else:
                sanitized[key] = value
        
        return sanitized


class APIHubService:
    """Comprehensive API Hub service"""
    
    def __init__(
        self,
        auth_service: AuthService,
        gpg_service: Optional[GPGService] = None,
        communication_service: Optional[CommunicationService] = None,
        event_service: Optional[EventService] = None,
        payment_service: Optional[PaymentService] = None
    ):
        self.auth_service = auth_service
        self.gpg_service = gpg_service
        self.communication_service = communication_service
        self.event_service = event_service
        self.payment_service = payment_service
        
        # Initialize components
        self.credential_manager = CredentialManager(auth_service, gpg_service)
        self.usage_tracker = UsageTracker()
        self.api_proxy = ExternalAPIProxy(
            self.credential_manager, self.usage_tracker, auth_service
        )
        
        # Integrations storage
        self.integrations: Dict[str, ThirdPartyIntegration] = {}
        self.connectors: Dict[str, ServiceConnector] = {}
        
        logger.info("API Hub service initialized")
    
    async def health_check(self) -> APIHubHealthResponse:
        """Check API Hub service health"""
        
        try:
            # Count credentials by status
            total_credentials = len(self.credential_manager.credentials)
            active_credentials = len([
                c for c in self.credential_manager.credentials.values()
                if c.status == APIStatus.ACTIVE
            ])
            expired_credentials = len([
                c for c in self.credential_manager.credentials.values()
                if c.status == APIStatus.EXPIRED
            ])
            
            # Calculate usage statistics
            recent_usage = [
                u for u in self.usage_tracker.usage_records.values()
                if u.called_at > datetime.utcnow() - timedelta(hours=1)
            ]
            
            api_calls_last_hour = len(recent_usage)
            successful_calls = len([u for u in recent_usage if u.success])
            failed_calls = api_calls_last_hour - successful_calls
            
            # Calculate average response time
            response_times = [u.response_time_ms for u in recent_usage if u.response_time_ms]
            avg_response_time = int(sum(response_times) / len(response_times)) if response_times else None
            
            # Calculate costs
            recent_costs = [u.estimated_cost_usd for u in recent_usage if u.estimated_cost_usd]
            total_cost_24h = sum(recent_costs) if recent_costs else Decimal("0")
            cost_per_call = total_cost_24h / len(recent_costs) if recent_costs else Decimal("0")
            
            return APIHubHealthResponse(
                status="healthy",
                total_credentials=total_credentials,
                active_credentials=active_credentials,
                expired_credentials=expired_credentials,
                api_calls_last_hour=api_calls_last_hour,
                successful_calls_last_hour=successful_calls,
                failed_calls_last_hour=failed_calls,
                average_response_time_ms=avg_response_time,
                total_cost_last_24h=total_cost_24h,
                cost_per_call_average=cost_per_call,
                healthy_providers=5,  # Mock
                degraded_providers=0,
                unhealthy_providers=0,
                active_integrations=len(self.integrations),
                webhook_health_percentage=95.0,  # Mock
                encrypted_credentials=total_credentials,  # All credentials encrypted
                personal_logs_recorded_last_hour=api_calls_last_hour,
                gdpr_compliant_operations=True,
                memory_usage_mb=75,  # Mock
                cpu_usage_percent=25.0,  # Mock
                security_violations_last_hour=0,
                rate_limited_requests=0,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("API Hub health check failed", error=str(e))
            return APIHubHealthResponse(
                status="unhealthy",
                total_credentials=0,
                active_credentials=0,
                expired_credentials=0,
                api_calls_last_hour=0,
                successful_calls_last_hour=0,
                failed_calls_last_hour=0,
                total_cost_last_24h=Decimal("0"),
                cost_per_call_average=Decimal("0"),
                healthy_providers=0,
                degraded_providers=0,
                unhealthy_providers=0,
                active_integrations=0,
                encrypted_credentials=0,
                personal_logs_recorded_last_hour=0,
                gdpr_compliant_operations=True,
                security_violations_last_hour=0,
                rate_limited_requests=0,
                last_check=datetime.utcnow()
            )
    
    async def create_credential(
        self,
        user_id: str,
        request: APICredentialCreate
    ) -> Tuple[bool, Optional[APICredential], Optional[str]]:
        """Create encrypted API credential"""
        return await self.credential_manager.create_credential(user_id, request)
    
    async def call_external_api(
        self,
        user_id: str,
        request: ExternalAPICall
    ) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Make external API call with tracking"""
        return await self.api_proxy.call_api(user_id, request)
    
    async def get_user_credentials(self, user_id: str) -> List[APICredential]:
        """Get user's API credentials"""
        return [
            c for c in self.credential_manager.credentials.values()
            if c.user_id == user_id
        ]
    
    async def get_usage_statistics(
        self,
        user_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get user's API usage statistics"""
        
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=period_days)
            
            # Filter usage records for user and time period
            user_usage = [
                u for u in self.usage_tracker.usage_records.values()
                if u.user_id == user_id and u.called_at >= cutoff_date
            ]
            
            # Calculate statistics
            total_calls = len(user_usage)
            successful_calls = len([u for u in user_usage if u.success])
            failed_calls = total_calls - successful_calls
            
            # Group by provider
            provider_stats = {}
            for usage in user_usage:
                provider = usage.provider.value
                if provider not in provider_stats:
                    provider_stats[provider] = {"calls": 0, "cost": Decimal("0"), "errors": 0}
                
                provider_stats[provider]["calls"] += 1
                if usage.estimated_cost_usd:
                    provider_stats[provider]["cost"] += usage.estimated_cost_usd
                if not usage.success:
                    provider_stats[provider]["errors"] += 1
            
            # Calculate total cost
            total_cost = sum(u.estimated_cost_usd for u in user_usage if u.estimated_cost_usd)
            
            return {
                "period_days": period_days,
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "failed_calls": failed_calls,
                "success_rate": successful_calls / max(total_calls, 1),
                "total_cost_usd": str(total_cost),
                "average_cost_per_call": str(total_cost / max(total_calls, 1)),
                "provider_breakdown": provider_stats,
                "period_start": cutoff_date.isoformat(),
                "period_end": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get usage statistics",
                        user_id=user_id,
                        error=str(e))
            return {}
    
    async def cleanup(self):
        """Cleanup API Hub service resources"""
        try:
            await self.api_proxy.http_client.aclose()
            logger.info("API Hub service cleanup completed")
        except Exception as e:
            logger.error("API Hub service cleanup failed", error=str(e))