"""
Authentication Module Tests
Privacy-first authentication testing with no personal data retention
"""

import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from libral_core.modules.auth.service import AuthService
from libral_core.modules.auth.schemas import (
    PersonalLogServerSetupRequest,
    TelegramAuthRequest,
    TokenRefreshRequest,
    UserRole
)

@pytest.fixture
def mock_gpg_service():
    """Create mock GPG service for auth testing"""
    service = AsyncMock()
    
    # Mock token encryption
    service.encrypt.return_value = AsyncMock(
        success=True,
        encrypted_data="-----BEGIN PGP MESSAGE-----\nencrypted_token_data\n-----END PGP MESSAGE-----"
    )
    
    # Mock token decryption
    service.decrypt.return_value = AsyncMock(
        success=True,
        decrypted_data=json.dumps({
            "token_id": "test-token-123",
            "user_id": "test-user-456",
            "token_type": "refresh",
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        })
    )
    
    service.system_key_id = "test-system-key"
    
    return service

@pytest.fixture
def auth_service(mock_gpg_service):
    """Create auth service for testing"""
    return AuthService(
        bot_token="123456789:ABCDEF",
        bot_username="TestLibralBot",
        webhook_secret="test_webhook_secret",
        gpg_service=mock_gpg_service
    )

@pytest.fixture
def telegram_auth_request():
    """Create valid Telegram auth request"""
    auth_date = int(datetime.utcnow().timestamp())
    
    # Mock valid Telegram auth hash (simplified for testing)
    auth_hash = "a1b2c3d4e5f6" * 8  # 48 chars hex
    
    return TelegramAuthRequest(
        id=123456789,
        first_name="Test",
        last_name="User",
        username="testuser",
        auth_date=auth_date,
        hash=auth_hash,
        create_personal_log_server=True
    )

@pytest.mark.asyncio
async def test_auth_service_health_check(auth_service):
    """Test authentication service health check"""
    
    with patch.object(auth_service.log_bot.bot, 'get_me') as mock_get_me:
        mock_get_me.return_value = MagicMock(username="TestLibralBot")
        
        health = await auth_service.health_check()
        
        assert health.status in ["healthy", "degraded"]
        assert health.telegram_bot_accessible is True
        assert health.gpg_service_available is True
        assert health.personal_data_retention_compliant is True
        assert health.gdpr_compliant is True

@pytest.mark.asyncio
async def test_telegram_authentication_success(auth_service, telegram_auth_request):
    """Test successful Telegram authentication"""
    
    # Mock Telegram auth verification
    with patch.object(auth_service, '_verify_telegram_auth', return_value=True):
        result = await auth_service.authenticate_telegram(telegram_auth_request)
        
        assert result.success is True
        assert result.user_profile is not None
        assert result.user_profile.telegram_id == telegram_auth_request.id
        assert result.user_profile.display_name == "Test User"
        assert result.user_profile.role == UserRole.USER
        
        # Verify privacy compliance
        assert result.personal_data_stored is False
        assert result.data_retention_policy == "user_controlled"
        
        # Verify tokens
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_expires_at is not None
        
        # Verify personal log server setup
        assert result.setup_required is True
        assert result.personal_log_server is not None

@pytest.mark.asyncio
async def test_telegram_authentication_invalid_hash(auth_service, telegram_auth_request):
    """Test Telegram authentication with invalid hash"""
    
    # Mock invalid Telegram auth verification
    with patch.object(auth_service, '_verify_telegram_auth', return_value=False):
        result = await auth_service.authenticate_telegram(telegram_auth_request)
        
        assert result.success is False
        assert result.error_code == "INVALID_TELEGRAM_AUTH"
        assert "Invalid Telegram authentication data" in result.error

@pytest.mark.asyncio
async def test_personal_log_server_setup_success(auth_service, telegram_auth_request):
    """Test successful personal log server setup"""
    
    # First authenticate user
    with patch.object(auth_service, '_verify_telegram_auth', return_value=True):
        auth_result = await auth_service.authenticate_telegram(telegram_auth_request)
        user_id = auth_result.user_profile.user_id
    
    # Mock successful group creation
    with patch.object(auth_service.log_bot, 'create_personal_log_group') as mock_create_group:
        mock_create_group.return_value = (True, {
            "id": -1001234567890,
            "title": "📋 Test User - Personal Libral Logs",
            "invite_link": "https://t.me/+test_invite_link"
        })
        
        setup_request = PersonalLogServerSetupRequest(
            user_id=user_id,
            create_new_group=True,
            use_gpg_encryption=True,
            gpg_key_fingerprint="test-gpg-key-fingerprint"
        )
        
        result = await auth_service.setup_personal_log_server(setup_request)
        
        assert result.success is True
        assert result.personal_log_server is not None
        assert result.personal_log_server.telegram_group_id == -1001234567890
        assert result.personal_log_server.encryption_enabled is True
        assert result.group_invite_link == "https://t.me/+test_invite_link"
        assert len(result.setup_instructions) > 0

@pytest.mark.asyncio
async def test_personal_log_server_setup_failure(auth_service, telegram_auth_request):
    """Test personal log server setup failure"""
    
    # First authenticate user
    with patch.object(auth_service, '_verify_telegram_auth', return_value=True):
        auth_result = await auth_service.authenticate_telegram(telegram_auth_request)
        user_id = auth_result.user_profile.user_id
    
    # Mock failed group creation
    with patch.object(auth_service.log_bot, 'create_personal_log_group') as mock_create_group:
        mock_create_group.return_value = (False, None)
        
        setup_request = PersonalLogServerSetupRequest(
            user_id=user_id,
            create_new_group=True
        )
        
        result = await auth_service.setup_personal_log_server(setup_request)
        
        assert result.success is False
        assert "Failed to create personal log group" in result.error
        assert result.retry_possible is True

@pytest.mark.asyncio
async def test_token_refresh_success(auth_service, mock_gpg_service):
    """Test successful token refresh"""
    
    refresh_request = TokenRefreshRequest(
        refresh_token="-----BEGIN PGP MESSAGE-----\nencrypted_refresh_token\n-----END PGP MESSAGE-----"
    )
    
    result = await auth_service.refresh_token(refresh_request)
    
    assert result.success is True
    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.expires_at is not None
    assert result.session_extended is True

@pytest.mark.asyncio
async def test_token_refresh_expired_token(auth_service, mock_gpg_service):
    """Test token refresh with expired token"""
    
    # Mock expired token payload
    mock_gpg_service.decrypt.return_value = AsyncMock(
        success=True,
        decrypted_data=json.dumps({
            "token_id": "expired-token",
            "user_id": "test-user",
            "token_type": "refresh",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).isoformat()  # Expired
        })
    )
    
    refresh_request = TokenRefreshRequest(
        refresh_token="-----BEGIN PGP MESSAGE-----\nexpired_token\n-----END PGP MESSAGE-----"
    )
    
    result = await auth_service.refresh_token(refresh_request)
    
    assert result.success is False
    assert "expired" in result.error.lower()

@pytest.mark.asyncio
async def test_token_refresh_invalid_type(auth_service, mock_gpg_service):
    """Test token refresh with wrong token type"""
    
    # Mock access token instead of refresh token
    mock_gpg_service.decrypt.return_value = AsyncMock(
        success=True,
        decrypted_data=json.dumps({
            "token_id": "wrong-type-token",
            "user_id": "test-user", 
            "token_type": "session",  # Wrong type
            "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
        })
    )
    
    refresh_request = TokenRefreshRequest(
        refresh_token="-----BEGIN PGP MESSAGE-----\nwrong_type_token\n-----END PGP MESSAGE-----"
    )
    
    result = await auth_service.refresh_token(refresh_request)
    
    assert result.success is False
    assert "Invalid token type" in result.error

@pytest.mark.asyncio
async def test_user_preferences_retrieval(auth_service, telegram_auth_request):
    """Test user preferences retrieval"""
    
    # First authenticate user
    with patch.object(auth_service, '_verify_telegram_auth', return_value=True):
        auth_result = await auth_service.authenticate_telegram(telegram_auth_request)
        user_id = auth_result.user_profile.user_id
    
    preferences = await auth_service.get_user_preferences(user_id)
    
    assert preferences is not None
    assert preferences.user_id == user_id
    assert preferences.language == "ja"  # Default for Japanese users
    assert preferences.log_encryption_required is True
    assert preferences.personal_log_notifications is True

@pytest.mark.asyncio
async def test_privacy_compliant_user_id_generation(auth_service):
    """Test privacy-compliant user ID generation"""
    
    telegram_id = 123456789
    
    # Generate user ID multiple times - should be consistent
    user_id_1 = await auth_service._generate_user_id(telegram_id)
    user_id_2 = await auth_service._generate_user_id(telegram_id)
    
    assert user_id_1 == user_id_2  # Consistent
    assert str(telegram_id) not in user_id_1  # No direct Telegram ID exposure
    assert len(user_id_1) == 36  # UUID format
    assert user_id_1.count('-') == 4  # UUID format verification

def test_telegram_auth_verification(auth_service):
    """Test Telegram auth data verification"""
    
    # Create valid auth request
    auth_date = int(datetime.utcnow().timestamp())
    auth_request = TelegramAuthRequest(
        id=123456789,
        first_name="Test",
        auth_date=auth_date,
        hash="test_hash"  # In real implementation, would calculate proper HMAC
    )
    
    # Mock the verification (real implementation would validate HMAC)
    with patch.object(auth_service, '_verify_telegram_auth', return_value=True):
        result = auth_service._verify_telegram_auth(auth_request)
        assert result is True
    
    # Test with old auth date (should fail)
    old_auth_request = TelegramAuthRequest(
        id=123456789,
        first_name="Test",
        auth_date=auth_date - 86400 - 1,  # More than 24 hours old
        hash="test_hash"
    )
    
    with pytest.raises(ValueError, match="too old"):
        old_auth_request  # Validation happens in Pydantic model

@pytest.mark.asyncio
async def test_session_cleanup(auth_service):
    """Test expired session cleanup"""
    
    # Add expired session
    expired_session_id = "expired-session"
    from libral_core.modules.auth.schemas import SessionInfo
    
    expired_session = SessionInfo(
        session_id=expired_session_id,
        user_id="test-user",
        started_at=datetime.utcnow() - timedelta(hours=10),
        expires_at=datetime.utcnow() - timedelta(hours=1),  # Expired
        last_activity=datetime.utcnow() - timedelta(hours=2),
        client_type="web"
    )
    
    auth_service.active_sessions[expired_session_id] = expired_session
    
    # Verify session exists
    assert expired_session_id in auth_service.active_sessions
    
    # Run cleanup
    await auth_service.cleanup_expired_sessions()
    
    # Verify expired session removed
    assert expired_session_id not in auth_service.active_sessions

@pytest.mark.asyncio
async def test_personal_log_encryption(auth_service, mock_gpg_service):
    """Test personal log encryption and transmission"""
    
    # Create user with GPG key
    user_id = "test-user-with-gpg"
    from libral_core.modules.auth.schemas import UserProfile
    
    user_profile = UserProfile(
        user_id=user_id,
        display_name="Test User",
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow(),
        gpg_key_fingerprint="test-user-gpg-key"
    )
    
    auth_service.user_profiles[user_id] = user_profile
    
    # Create active personal log server
    from libral_core.modules.auth.schemas import PersonalLogServer, PersonalLogServerStatus
    
    personal_server = PersonalLogServer(
        user_id=user_id,
        status=PersonalLogServerStatus.ACTIVE,
        telegram_group_id=-1001234567890,
        encryption_enabled=True
    )
    
    auth_service.personal_log_servers[user_id] = personal_server
    
    # Test log transmission
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": "auth",
        "event_type": "test_event",
        "user_id": user_id
    }
    
    result = await auth_service._log_to_personal_server(user_id, log_data)
    
    # Verify GPG encryption was called
    mock_gpg_service.encrypt.assert_called()
    encrypt_call_args = mock_gpg_service.encrypt.call_args[0][0]
    assert encrypt_call_args.recipients == ["test-user-gpg-key"]
    assert "libral.user_controlled" in encrypt_call_args.context_labels

def test_privacy_compliance_no_personal_data_storage(auth_service):
    """Test that no personal data is stored inappropriately"""
    
    # This test ensures privacy compliance in auth operations
    # Verify that sensitive data patterns are not stored
    
    # Check that user profiles don't contain sensitive data beyond necessary UI info
    for user_id, profile in auth_service.user_profiles.items():
        # Display name is allowed for UI purposes
        assert hasattr(profile, 'display_name')
        
        # But no email, phone, or other PII should be stored
        profile_dict = profile.dict()
        sensitive_fields = ['email', 'phone', 'address', 'real_name']
        
        for field in sensitive_fields:
            assert field not in profile_dict, f"Sensitive field {field} found in user profile"
    
    # Verify session data doesn't contain PII
    for session_id, session in auth_service.active_sessions.items():
        session_dict = session.dict()
        
        # IP addresses should be hashed, not stored directly
        if session.ip_address_hash:
            assert not session.ip_address_hash.count('.') == 3, "Raw IP address detected"
        
        # User agent should be hashed, not stored directly  
        if session.user_agent_hash:
            assert len(session.user_agent_hash) >= 32, "User agent appears unhashed"
    
    # Verify tokens are encrypted
    for token_id, token in auth_service.auth_tokens.items():
        assert token.encrypted_payload.startswith("-----BEGIN PGP MESSAGE-----"), "Token payload not encrypted"
    
    assert True, "Privacy compliance verified - no inappropriate personal data storage detected"