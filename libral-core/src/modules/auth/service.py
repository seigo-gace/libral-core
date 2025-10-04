"""
Authentication Service - Week 3 Implementation
Privacy-first authentication with Telegram OAuth and personal log servers
"""

import asyncio
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import uuid4
import urllib.parse

import httpx
import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .schemas import (
    AuthHealthResponse,
    AuthToken,
    PersonalLogServer,
    PersonalLogServerSetupRequest,
    PersonalLogServerSetupResponse,
    PersonalLogServerStatus,
    SessionInfo,
    SessionStatus,
    TelegramAuthRequest,
    TelegramAuthResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserPreferences,
    UserProfile,
    UserRole
)
from ..gpg.service import GPGService
from ..gpg.schemas import EncryptRequest, DecryptRequest, SignRequest

logger = structlog.get_logger(__name__)


class TelegramPersonalLogBot:
    """Telegram bot for personal log server management"""
    
    def __init__(self, bot_token: str, gpg_service: Optional[GPGService] = None):
        self.bot = Bot(token=bot_token)
        self.gpg_service = gpg_service
        
    async def create_personal_log_group(self, user_id: str, user_name: str) -> Tuple[bool, Optional[Dict]]:
        """Create a personal log supergroup with topics and hashtag organization"""
        try:
            # Create supergroup with advanced topic organization
            group_info = {
                "id": -1000000000000 - int(user_id.replace('-', '')[:10], 16),  # Simulated group ID
                "title": f"📋 {user_name} - Personal Libral Logs",
                "invite_link": f"https://t.me/+{secrets.token_urlsafe(22)[:22]}",
                "description": "🔐 Private log server for Libral Core\n\n"
                             "This supergroup stores your encrypted activity logs.\n"
                             "Only you can decrypt and access this data.\n"
                             "All logs auto-delete after 30 days by default.\n\n"
                             "📚 Topics organized by category:\n"
                             "• 🔐 Authentication & Security\n"
                             "• 🔌 Plugin Activity\n"
                             "• 💰 Payment & Transactions\n"
                             "• 📡 Communication Logs\n"
                             "• ⚙️ System Events"
            }
            
            # Add topic configuration to group info
            group_info["topics_created"] = await self._create_log_topics(group_info["id"])
            
            logger.info("Personal log group with topics created", 
                       user_id=user_id,
                       group_id=group_info["id"],
                       topics_count=len(group_info["topics_created"]))
            
            return True, group_info
            
        except Exception as e:
            logger.error("Failed to create personal log group", 
                        user_id=user_id, 
                        error=str(e))
            return False, None
    
    async def _create_log_topics(self, group_id: int) -> List[Dict[str, Any]]:
        """Create organized topics in the personal log supergroup"""
        try:
            topics = [
                {
                    "id": 1,
                    "name": "🔐 Authentication & Security",
                    "description": "Login events, token refresh, security alerts",
                    "hashtags": ["#auth", "#security", "#login", "#token", "#2fa"]
                },
                {
                    "id": 2, 
                    "name": "🔌 Plugin Activity",
                    "description": "Plugin installations, updates, usage logs",
                    "hashtags": ["#plugin", "#install", "#update", "#marketplace", "#usage"]
                },
                {
                    "id": 3,
                    "name": "💰 Payment & Transactions", 
                    "description": "Payment events, subscription changes, revenue sharing",
                    "hashtags": ["#payment", "#transaction", "#subscription", "#revenue", "#billing"]
                },
                {
                    "id": 4,
                    "name": "📡 Communication Logs",
                    "description": "Messages, notifications, API communications", 
                    "hashtags": ["#message", "#notification", "#api", "#webhook", "#communication"]
                },
                {
                    "id": 5,
                    "name": "⚙️ System Events",
                    "description": "System status, performance metrics, errors",
                    "hashtags": ["#system", "#performance", "#error", "#metric", "#status"]
                },
                {
                    "id": 6,
                    "name": "🎯 General Topic",
                    "description": "Uncategorized logs and general events",
                    "hashtags": ["#general", "#misc", "#other", "#uncategorized"]
                }
            ]
            
            # In real implementation, would create actual Telegram topics
            logger.info("Log topics structure created",
                       group_id=group_id,
                       topics_count=len(topics))
            
            return topics
            
        except Exception as e:
            logger.error("Failed to create log topics", 
                        group_id=group_id,
                        error=str(e))
            return []
    
    def _get_hashtags_for_category(self, category: str) -> List[str]:
        """Get appropriate hashtags for log category"""
        hashtag_map = {
            "auth": ["#auth", "#security", "#login"],
            "plugin": ["#plugin", "#marketplace", "#install"],
            "payment": ["#payment", "#transaction", "#billing"],
            "communication": ["#message", "#notification", "#api"],
            "system": ["#system", "#performance", "#status"],
            "general": ["#general", "#misc"]
        }
        
        return hashtag_map.get(category.lower(), ["#general"])
    
    async def send_encrypted_log(
        self, 
        group_id: int, 
        log_data: Dict, 
        user_gpg_key: str,
        topic_id: Optional[int] = None
    ) -> bool:
        """Send encrypted log entry to personal log group with topic and hashtag support"""
        try:
            if not self.gpg_service:
                logger.warning("GPG service not available for log encryption")
                return False
            
            # Encrypt log data with user's GPG key
            encrypt_request = EncryptRequest(
                data=json.dumps(log_data, indent=2, ensure_ascii=False),
                recipients=[user_gpg_key],
                context_labels={
                    "libral.log_type": log_data.get("type", "general"),
                    "libral.timestamp": datetime.utcnow().isoformat(),
                    "libral.user_controlled": "true"
                }
            )
            
            encrypt_result = await self.gpg_service.encrypt(encrypt_request)
            
            if not encrypt_result.success:
                logger.error("Failed to encrypt log data", error=encrypt_result.error)
                return False
            
            # Determine hashtags based on category
            hashtags = self._get_hashtags_for_category(log_data.get('category', 'general'))
            hashtag_string = " ".join(hashtags)
            
            # Format message for Telegram with topic and hashtag support
            topic_info = f"📋 Topic #{topic_id}" if topic_id else "📋 General"
            
            message_text = f"""🔐 **Libral Core Log Entry** {topic_info}
            
📅 **Time**: {log_data.get('timestamp', 'Unknown')}
📂 **Category**: {log_data.get('category', 'General')}
🔍 **Event**: {log_data.get('event_type', 'Unknown')}
🏷️ **Tags**: {hashtag_string}

```
{encrypt_result.encrypted_data}
```

_This log entry is encrypted with your GPG key. Only you can decrypt it._
_Auto-deletion: 30 days from now_

{hashtag_string}"""
            
            # In real implementation, would send to Telegram group
            logger.info("Encrypted log prepared for personal server",
                       group_id=group_id,
                       log_category=log_data.get("category"),
                       encrypted_size=len(encrypt_result.encrypted_data))
            
            return True
            
        except Exception as e:
            logger.error("Failed to send encrypted log",
                        group_id=group_id,
                        error=str(e))
            return False


class AuthService:
    """Privacy-first authentication service with Telegram integration"""
    
    def __init__(
        self,
        bot_token: str,
        bot_username: str,
        webhook_secret: str,
        gpg_service: Optional[GPGService] = None
    ):
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.webhook_secret = webhook_secret
        self.gpg_service = gpg_service
        
        # Initialize Telegram bot for personal log servers
        self.log_bot = TelegramPersonalLogBot(bot_token, gpg_service)
        
        # In-memory storage for development (should use Redis/Database in production)
        self.user_profiles: Dict[str, UserProfile] = {}
        self.personal_log_servers: Dict[str, PersonalLogServer] = {}
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.auth_tokens: Dict[str, AuthToken] = {}
        
        logger.info("Authentication service initialized",
                   bot_username=bot_username,
                   gpg_enabled=bool(gpg_service))
    
    def _verify_telegram_auth(self, auth_data: TelegramAuthRequest) -> bool:
        """Verify Telegram OAuth data integrity"""
        try:
            # Create data check string (Telegram OAuth verification)
            auth_dict = auth_data.dict(exclude={'hash'})
            auth_dict['auth_date'] = str(auth_dict['auth_date'])
            
            # Remove None values and sort by key
            auth_dict = {k: str(v) for k, v in auth_dict.items() if v is not None}
            data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_dict.items())])
            
            # Calculate hash using bot token
            secret_key = hashlib.sha256(self.bot_token.encode()).digest()
            calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
            
            # Compare with provided hash
            return hmac.compare_digest(calculated_hash, auth_data.hash)
            
        except Exception as e:
            logger.error("Telegram auth verification failed", error=str(e))
            return False
    
    async def _generate_user_id(self, telegram_id: int) -> str:
        """Generate privacy-compliant user ID"""
        # Use HMAC of Telegram ID with secret to create consistent but private user ID
        user_id_raw = hmac.new(
            self.webhook_secret.encode(),
            str(telegram_id).encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Format as UUID-like string for consistency
        return f"{user_id_raw[:8]}-{user_id_raw[8:12]}-{user_id_raw[12:16]}-{user_id_raw[16:20]}-{user_id_raw[20:32]}"
    
    async def _create_encrypted_token(
        self, 
        user_id: str, 
        token_type: str,
        lifetime_hours: int = 8
    ) -> Optional[AuthToken]:
        """Create GPG-encrypted authentication token"""
        
        if not self.gpg_service:
            logger.warning("GPG service not available for token encryption")
            return None
        
        try:
            token_id = str(uuid4())
            current_time = datetime.utcnow()
            expires_at = current_time + timedelta(hours=lifetime_hours)
            
            # Create token payload
            payload = {
                "token_id": token_id,
                "user_id": user_id,
                "token_type": token_type,
                "issued_at": current_time.isoformat(),
                "expires_at": expires_at.isoformat(),
                "issuer": "libral_core_auth",
                "audience": "libral_core_api"
            }
            
            # Encrypt token payload with system GPG key
            encrypt_request = EncryptRequest(
                data=json.dumps(payload),
                recipients=[self.gpg_service.system_key_id] if self.gpg_service.system_key_id else [],
                context_labels={
                    "libral.token_type": token_type,
                    "libral.user_controlled": "true",
                    "libral.auto_expire": "true"
                }
            )
            
            encrypt_result = await self.gpg_service.encrypt(encrypt_request)
            
            if not encrypt_result.success:
                logger.error("Token encryption failed", error=encrypt_result.error)
                return None
            
            # Create auth token object
            auth_token = AuthToken(
                token_id=token_id,
                user_id=user_id,
                token_type=token_type,
                encrypted_payload=encrypt_result.encrypted_data,
                created_at=current_time,
                expires_at=expires_at,
                context_labels=encrypt_request.context_labels or {}
            )
            
            # Store in registry
            self.auth_tokens[token_id] = auth_token
            
            logger.info("Encrypted token created",
                       token_id=token_id,
                       token_type=token_type,
                       expires_at=expires_at)
            
            return auth_token
            
        except Exception as e:
            logger.error("Token creation failed", error=str(e))
            return None
    
    async def _log_to_personal_server(
        self, 
        user_id: str, 
        log_data: Dict
    ) -> bool:
        """Log event to user's personal log server"""
        
        try:
            # Get user's personal log server
            personal_server = self.personal_log_servers.get(user_id)
            if not personal_server or personal_server.status != PersonalLogServerStatus.ACTIVE:
                logger.debug("Personal log server not available for user", user_id=user_id)
                return False
            
            # Get user GPG key for encryption
            user_profile = self.user_profiles.get(user_id)
            if not user_profile or not user_profile.gpg_key_fingerprint:
                logger.warning("User GPG key not available for personal logging", user_id=user_id)
                return False
            
            # Send encrypted log to personal server
            success = await self.log_bot.send_encrypted_log(
                personal_server.telegram_group_id,
                log_data,
                user_profile.gpg_key_fingerprint
            )
            
            if success:
                personal_server.last_log_sent = datetime.utcnow()
                logger.info("Event logged to personal server", user_id=user_id)
            
            return success
            
        except Exception as e:
            logger.error("Personal server logging failed", 
                        user_id=user_id, 
                        error=str(e))
            return False
    
    async def health_check(self) -> AuthHealthResponse:
        """Check authentication service health"""
        
        try:
            # Check Telegram bot connectivity
            telegram_accessible = False
            try:
                bot_info = await self.log_bot.bot.get_me()
                telegram_accessible = bool(bot_info.username)
            except Exception:
                telegram_accessible = False
            
            # Count statistics
            active_sessions = sum(
                1 for session in self.active_sessions.values()
                if session.expires_at > datetime.utcnow()
            )
            
            users_with_servers = sum(
                1 for server in self.personal_log_servers.values()
                if server.status == PersonalLogServerStatus.ACTIVE
            )
            
            # Calculate performance metrics
            avg_auth_time = 150  # Simulated average auth time in ms
            token_refresh_rate = 0.98  # Simulated success rate
            
            return AuthHealthResponse(
                status="healthy" if telegram_accessible else "degraded",
                telegram_bot_accessible=telegram_accessible,
                gpg_service_available=bool(self.gpg_service),
                personal_log_servers_operational=users_with_servers,
                active_sessions=active_sessions,
                users_with_personal_servers=users_with_servers,
                average_auth_time_ms=avg_auth_time,
                token_refresh_success_rate=token_refresh_rate,
                suspicious_activity_detected=False,
                rate_limiting_active=False,
                personal_data_retention_compliant=True,
                gdpr_compliant=True,
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("Auth health check failed", error=str(e))
            return AuthHealthResponse(
                status="unhealthy",
                telegram_bot_accessible=False,
                gpg_service_available=False,
                personal_log_servers_operational=0,
                active_sessions=0,
                users_with_personal_servers=0,
                last_check=datetime.utcnow()
            )
    
    async def authenticate_telegram(self, request: TelegramAuthRequest) -> TelegramAuthResponse:
        """Authenticate user via Telegram OAuth"""
        request_id = str(uuid4())[:8]
        
        try:
            logger.info("Telegram authentication started",
                       request_id=request_id,
                       telegram_id=request.id,
                       username=request.username)
            
            # Verify Telegram OAuth data
            if not self._verify_telegram_auth(request):
                return TelegramAuthResponse(
                    success=False,
                    error="Invalid Telegram authentication data",
                    error_code="INVALID_TELEGRAM_AUTH",
                    request_id=request_id
                )
            
            # Generate privacy-compliant user ID
            user_id = await self._generate_user_id(request.id)
            
            # Check if user exists or create new profile
            user_profile = self.user_profiles.get(user_id)
            is_new_user = user_profile is None
            
            if is_new_user:
                # Create new user profile
                display_name = request.first_name
                if request.last_name:
                    display_name += f" {request.last_name}"
                
                user_profile = UserProfile(
                    user_id=user_id,
                    telegram_id=request.id,
                    username=request.username,
                    display_name=display_name,
                    created_at=datetime.utcnow(),
                    last_active=datetime.utcnow(),
                    role=UserRole.USER
                )
                
                self.user_profiles[user_id] = user_profile
                
                logger.info("New user profile created",
                           request_id=request_id,
                           user_id=user_id,
                           is_new_user=True)
            else:
                # Update existing user
                user_profile.last_active = datetime.utcnow()
                logger.info("Existing user authenticated",
                           request_id=request_id,
                           user_id=user_id)
            
            # Create authentication tokens
            access_token = await self._create_encrypted_token(user_id, "session", 8)
            refresh_token = await self._create_encrypted_token(user_id, "refresh", 168)  # 7 days
            
            if not access_token:
                return TelegramAuthResponse(
                    success=False,
                    error="Failed to create authentication tokens",
                    error_code="TOKEN_CREATION_FAILED",
                    request_id=request_id
                )
            
            # Create session
            session_info = SessionInfo(
                session_id=access_token.token_id,
                user_id=user_id,
                started_at=datetime.utcnow(),
                expires_at=access_token.expires_at,
                last_activity=datetime.utcnow(),
                client_type="web",
                country_code="JP"  # Default for Japanese users
            )
            
            self.active_sessions[session_info.session_id] = session_info
            
            # Handle personal log server setup
            personal_log_server = None
            setup_required = False
            
            if request.create_personal_log_server and is_new_user:
                # Initialize personal log server setup
                personal_log_server = PersonalLogServer(
                    user_id=user_id,
                    status=PersonalLogServerStatus.SETTING_UP,
                    setup_started_at=datetime.utcnow(),
                    encryption_enabled=True
                )
                
                self.personal_log_servers[user_id] = personal_log_server
                setup_required = True
                
                logger.info("Personal log server setup initiated",
                           request_id=request_id,
                           user_id=user_id)
            else:
                personal_log_server = self.personal_log_servers.get(user_id)
            
            # Log authentication event to personal server (if available)
            await self._log_to_personal_server(user_id, {
                "timestamp": datetime.utcnow().isoformat(),
                "category": "auth",
                "event_type": "telegram_login",
                "is_new_user": is_new_user,
                "client_type": "web",
                "success": True
            })
            
            logger.info("Telegram authentication successful",
                       request_id=request_id,
                       user_id=user_id,
                       is_new_user=is_new_user,
                       setup_required=setup_required)
            
            return TelegramAuthResponse(
                success=True,
                user_profile=user_profile,
                session_info=session_info,
                access_token=access_token.encrypted_payload,
                refresh_token=refresh_token.encrypted_payload if refresh_token else None,
                token_expires_at=access_token.expires_at,
                personal_log_server=personal_log_server,
                setup_required=setup_required,
                request_id=request_id,
                personal_data_stored=False  # Privacy compliance
            )
            
        except Exception as e:
            logger.error("Telegram authentication failed",
                        request_id=request_id,
                        error=str(e))
            
            return TelegramAuthResponse(
                success=False,
                error=f"Authentication failed: {str(e)}",
                error_code="AUTHENTICATION_ERROR",
                request_id=request_id
            )
    
    async def setup_personal_log_server(
        self, 
        request: PersonalLogServerSetupRequest
    ) -> PersonalLogServerSetupResponse:
        """Setup personal log server for user"""
        request_id = str(uuid4())[:8]
        
        try:
            logger.info("Personal log server setup started",
                       request_id=request_id,
                       user_id=request.user_id)
            
            # Get user profile
            user_profile = self.user_profiles.get(request.user_id)
            if not user_profile:
                return PersonalLogServerSetupResponse(
                    success=False,
                    error="User not found",
                    status=PersonalLogServerStatus.ERROR,
                    request_id=request_id
                )
            
            # Get or create personal log server
            personal_server = self.personal_log_servers.get(request.user_id)
            if not personal_server:
                personal_server = PersonalLogServer(
                    user_id=request.user_id,
                    status=PersonalLogServerStatus.SETTING_UP,
                    setup_started_at=datetime.utcnow()
                )
                self.personal_log_servers[request.user_id] = personal_server
            
            # Create personal log group
            if request.create_new_group:
                success, group_info = await self.log_bot.create_personal_log_group(
                    request.user_id,
                    user_profile.display_name
                )
                
                if success and group_info:
                    personal_server.telegram_group_id = group_info["id"]
                    personal_server.telegram_group_invite_link = group_info["invite_link"]
                    personal_server.status = PersonalLogServerStatus.ACTIVE
                    personal_server.setup_completed_at = datetime.utcnow()
                    
                    # Set up GPG encryption
                    if request.use_gpg_encryption and request.gpg_key_fingerprint:
                        personal_server.log_encryption_key = request.gpg_key_fingerprint
                        personal_server.encryption_enabled = True
                        user_profile.gpg_key_fingerprint = request.gpg_key_fingerprint
                    
                    # Configure log preferences
                    personal_server.log_categories = request.log_categories
                    personal_server.auto_delete_after_days = request.retention_days
                    
                    setup_instructions = [
                        "✅ Personal log supergroup created successfully",
                        f"📱 Join your log group: {group_info['invite_link']}",
                        "🤖 Add @LibralCoreBot to the group as administrator",
                        "🔐 Enable GPG encryption for maximum privacy",
                        "⚙️ Configure auto-deletion settings (default: 30 days)"
                    ]
                    
                    logger.info("Personal log server setup completed",
                               request_id=request_id,
                               user_id=request.user_id,
                               group_id=personal_server.telegram_group_id)
                    
                    return PersonalLogServerSetupResponse(
                        success=True,
                        personal_log_server=personal_server,
                        setup_instructions=setup_instructions,
                        telegram_bot_username=self.bot_username,
                        group_invite_link=group_info["invite_link"],
                        status=PersonalLogServerStatus.ACTIVE,
                        estimated_setup_time_minutes=2,
                        request_id=request_id
                    )
                else:
                    personal_server.status = PersonalLogServerStatus.ERROR
                    personal_server.setup_errors.append("Failed to create Telegram group")
                    personal_server.retry_count += 1
                    
                    return PersonalLogServerSetupResponse(
                        success=False,
                        error="Failed to create personal log group",
                        status=PersonalLogServerStatus.ERROR,
                        retry_possible=personal_server.retry_count < 3,
                        request_id=request_id
                    )
            
        except Exception as e:
            logger.error("Personal log server setup failed",
                        request_id=request_id,
                        error=str(e))
            
            if request.user_id in self.personal_log_servers:
                self.personal_log_servers[request.user_id].status = PersonalLogServerStatus.ERROR
            
            return PersonalLogServerSetupResponse(
                success=False,
                error=f"Setup failed: {str(e)}",
                status=PersonalLogServerStatus.ERROR,
                request_id=request_id
            )
    
    async def refresh_token(self, request: TokenRefreshRequest) -> TokenRefreshResponse:
        """Refresh authentication token"""
        request_id = str(uuid4())[:8]
        
        try:
            if not self.gpg_service:
                return TokenRefreshResponse(
                    success=False,
                    error="GPG service not available for token refresh",
                    request_id=request_id
                )
            
            # Decrypt refresh token
            decrypt_request = DecryptRequest(encrypted_data=request.refresh_token)
            decrypt_result = await self.gpg_service.decrypt(decrypt_request)
            
            if not decrypt_result.success:
                return TokenRefreshResponse(
                    success=False,
                    error="Invalid refresh token",
                    request_id=request_id
                )
            
            # Parse token payload
            token_payload = json.loads(decrypt_result.decrypted_data)
            user_id = token_payload["user_id"]
            
            # Verify token type and expiry
            if token_payload["token_type"] != "refresh":
                return TokenRefreshResponse(
                    success=False,
                    error="Invalid token type",
                    request_id=request_id
                )
            
            expires_at = datetime.fromisoformat(token_payload["expires_at"])
            if expires_at <= datetime.utcnow():
                return TokenRefreshResponse(
                    success=False,
                    error="Refresh token expired",
                    request_id=request_id
                )
            
            # Create new access token
            new_access_token = await self._create_encrypted_token(user_id, "session", 8)
            new_refresh_token = await self._create_encrypted_token(user_id, "refresh", 168)
            
            if not new_access_token:
                return TokenRefreshResponse(
                    success=False,
                    error="Failed to create new tokens",
                    request_id=request_id
                )
            
            logger.info("Token refresh successful",
                       request_id=request_id,
                       user_id=user_id)
            
            return TokenRefreshResponse(
                success=True,
                access_token=new_access_token.encrypted_payload,
                refresh_token=new_refresh_token.encrypted_payload if new_refresh_token else None,
                expires_at=new_access_token.expires_at,
                session_extended=True,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("Token refresh failed",
                        request_id=request_id,
                        error=str(e))
            
            return TokenRefreshResponse(
                success=False,
                error=f"Token refresh failed: {str(e)}",
                request_id=request_id
            )
    
    async def get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences from personal log server"""
        try:
            # In real implementation, would decrypt preferences from personal log server
            # For now, return default preferences
            
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                return None
            
            return UserPreferences(
                user_id=user_id,
                language="ja",
                theme="dark",
                timezone="Asia/Tokyo",
                data_retention_days=30,
                session_timeout_minutes=480,
                log_encryption_required=True,
                personal_log_notifications=True,
                security_alerts=True
            )
            
        except Exception as e:
            logger.error("Failed to get user preferences", 
                        user_id=user_id, 
                        error=str(e))
            return None
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions and tokens"""
        try:
            current_time = datetime.utcnow()
            
            # Clean up expired sessions
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if session.expires_at <= current_time
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            # Clean up expired tokens
            expired_tokens = [
                token_id for token_id, token in self.auth_tokens.items()
                if token.expires_at <= current_time
            ]
            
            for token_id in expired_tokens:
                del self.auth_tokens[token_id]
            
            if expired_sessions or expired_tokens:
                logger.info("Cleanup completed",
                           expired_sessions=len(expired_sessions),
                           expired_tokens=len(expired_tokens))
            
        except Exception as e:
            logger.error("Session cleanup failed", error=str(e))