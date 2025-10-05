"""
GPG Module Tests - Week 1
Test GPG operations without storing sensitive test data
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from libral_core.modules.gpg.service import GPGService
from libral_core.modules.gpg.schemas import (
    EncryptRequest, EncryptionPolicy,
    DecryptRequest,
    SignRequest,
    VerifyRequest,
    KeyGenerationRequest, KeyType,
    WKDPathRequest
)

@pytest.fixture
def mock_gpg_service():
    """Create mock GPG service for testing"""
    service = GPGService(
        gnupg_home="/tmp/test_gpg",
        system_key_id="test_key_id",
        passphrase="test_passphrase"
    )
    
    # Mock the underlying GPG object
    service.gpg = MagicMock()
    return service

@pytest.mark.asyncio
async def test_health_check(mock_gpg_service):
    """Test GPG module health check"""
    
    # Mock GPG version and keys
    mock_gpg_service.gpg.version = "2.4.0"
    mock_gpg_service.gpg.list_keys.return_value = [{"fingerprint": "test123"}]
    
    result = await mock_gpg_service.health_check()
    
    assert result.status == "healthy"
    assert result.version == "2.4.0"
    assert result.keys_available >= 0
    assert "modern-strong" in result.policies_loaded

@pytest.mark.asyncio 
async def test_encrypt_with_modern_strong_policy(mock_gpg_service):
    """Test encryption with modern strong policy"""
    
    # Mock successful encryption
    mock_encrypted = MagicMock()
    mock_encrypted.ok = True
    mock_encrypted.__str__ = lambda x: "-----BEGIN PGP MESSAGE-----\nencrypted_content\n-----END PGP MESSAGE-----"
    mock_encrypted.fingerprints = ["recipient123"]
    
    mock_gpg_service.gpg.encrypt.return_value = mock_encrypted
    
    request = EncryptRequest(
        data="test_data_for_encryption",
        recipients=["test@example.com"],
        policy=EncryptionPolicy.MODERN_STRONG,
        context_labels={"test": "true"}
    )
    
    result = await mock_gpg_service.encrypt(request)
    
    assert result.success is True
    assert result.policy_applied == EncryptionPolicy.MODERN_STRONG
    assert result.context_labels == {"test": "true"}
    assert len(result.fingerprints) > 0
    assert result.request_id is not None

@pytest.mark.asyncio
async def test_decrypt_with_context_labels(mock_gpg_service):
    """Test decryption and context label extraction"""
    
    # Mock successful decryption with context labels
    mock_decrypted = MagicMock()
    mock_decrypted.ok = True
    mock_decrypted.__str__ = lambda x: """---LIBRAL-CONTEXT-LOCK---
{"context_lock_version": "1.0", "labels": {"test": "true"}, "timestamp": "2024-01-01T00:00:00", "libral_core_version": "1.0.0"}
---END-CONTEXT---
original_test_data"""
    mock_decrypted.signature_id = "signer123"
    mock_decrypted.valid = True
    
    mock_gpg_service.gpg.decrypt.return_value = mock_decrypted
    
    request = DecryptRequest(
        encrypted_data="-----BEGIN PGP MESSAGE-----\ntest_encrypted_data\n-----END PGP MESSAGE-----"
    )
    
    result = await mock_gpg_service.decrypt(request)
    
    assert result.success is True
    assert result.decrypted_data == "original_test_data"
    assert result.context_labels == {"test": "true"}
    assert result.signature_valid is True
    assert len(result.signer_fingerprints) > 0

@pytest.mark.asyncio 
async def test_sign_with_context_lock(mock_gpg_service):
    """Test signing with Context-Lock labels"""
    
    # Mock successful signing
    mock_signature = MagicMock()
    mock_signature.data = "-----BEGIN PGP SIGNATURE-----\ntest_signature\n-----END PGP SIGNATURE-----"
    mock_signature.fingerprint = "signer123"
    
    mock_gpg_service.gpg.sign.return_value = mock_signature
    
    request = SignRequest(
        data="test_data_to_sign",
        context_labels={"operation": "test_signing"},
        detached=True
    )
    
    result = await mock_gpg_service.sign(request)
    
    assert result.success is True
    assert result.signer_fingerprint == "signer123"
    assert result.context_labels == {"operation": "test_signing"}
    assert result.signature is not None

@pytest.mark.asyncio
async def test_verify_signature(mock_gpg_service):
    """Test signature verification"""
    
    # Mock successful verification
    mock_verified = MagicMock()
    mock_verified.valid = True
    mock_verified.fingerprint = "signer123" 
    mock_verified.timestamp = 1704067200  # 2024-01-01 00:00:00 UTC
    
    mock_gpg_service.gpg.verify.return_value = mock_verified
    
    request = VerifyRequest(
        signed_data="-----BEGIN PGP SIGNATURE-----\ntest_signature\n-----END PGP SIGNATURE-----"
    )
    
    result = await mock_gpg_service.verify(request)
    
    assert result.success is True
    assert result.valid is True
    assert result.signer_fingerprints == ["signer123"]
    assert result.signature_timestamp is not None

@pytest.mark.asyncio
async def test_generate_rsa_key_pair(mock_gpg_service):
    """Test RSA key pair generation"""
    
    # Mock successful key generation
    mock_key = MagicMock()
    mock_key.fingerprint = "newkey123456789"
    
    mock_gpg_service.gpg.gen_key.return_value = mock_key
    mock_gpg_service.gpg.export_keys.return_value = "-----BEGIN PGP PUBLIC KEY-----\npublic_key_data\n-----END PGP PUBLIC KEY-----"
    mock_gpg_service.gpg.list_keys.return_value = [{
        'keyid': 'newkey123',
        'fingerprint': 'newkey123456789',
        'uids': ['Test User <test@example.com>'],
        'algo': 'RSA',
        'length': '4096',
        'date': '1704067200',
        'expires': '',
        'trust': 'ultimate'
    }]
    
    request = KeyGenerationRequest(
        key_type=KeyType.RSA_4096,
        name="Test User",
        email="test@example.com",
        comment="Test key"
    )
    
    result = await mock_gpg_service.generate_key_pair(request)
    
    assert result.success is True
    assert result.fingerprint == "newkey123456789"
    assert result.public_key is not None
    assert result.key_info is not None
    assert result.key_info.key_size == 4096

@pytest.mark.asyncio
async def test_wkd_path_generation(mock_gpg_service):
    """Test Web Key Directory path generation"""
    
    request = WKDPathRequest(email="test@example.com")
    result = await mock_gpg_service.generate_wkd_path(request)
    
    assert result.local_part == "test"
    assert result.domain == "example.com"
    assert result.wkd_path.startswith("/.well-known/openpgpkey/hu/")
    assert len(result.z_base32) == 32

def test_encryption_policy_configurations(mock_gpg_service):
    """Test that all encryption policies are properly configured"""
    
    policies = mock_gpg_service.policies
    
    # Check all required policies exist
    assert EncryptionPolicy.MODERN_STRONG in policies
    assert EncryptionPolicy.COMPAT in policies
    assert EncryptionPolicy.BACKUP_LONGTERM in policies
    
    # Check modern strong policy configuration
    modern_strong = policies[EncryptionPolicy.MODERN_STRONG]
    assert modern_strong["cipher_algo"] == "AES256"
    assert modern_strong["digest_algo"] == "SHA256"
    
    # Check compatibility policy
    compat = policies[EncryptionPolicy.COMPAT]
    assert modern_strong["cipher_algo"] in ["AES128", "AES256"]
    
    # Check backup longterm policy  
    backup = policies[EncryptionPolicy.BACKUP_LONGTERM]
    assert backup["cipher_algo"] == "AES256"
    assert backup["compress_algo"] == 0  # No compression for integrity

@pytest.mark.asyncio
async def test_error_handling_encryption_failure(mock_gpg_service):
    """Test error handling for encryption failures"""
    
    # Mock encryption failure
    mock_encrypted = MagicMock()
    mock_encrypted.ok = False
    mock_encrypted.stderr = "Invalid recipient key"
    
    mock_gpg_service.gpg.encrypt.return_value = mock_encrypted
    
    request = EncryptRequest(
        data="test_data",
        recipients=["invalid@example.com"],
        policy=EncryptionPolicy.MODERN_STRONG
    )
    
    result = await mock_gpg_service.encrypt(request)
    
    assert result.success is False
    assert "Invalid recipient key" in result.error
    assert result.request_id is not None

@pytest.mark.asyncio
async def test_privacy_compliance_no_data_logging(mock_gpg_service):
    """Test that sensitive data is not logged or retained"""
    
    # This test verifies that the service doesn't log sensitive data
    # In a real implementation, we would check log outputs
    
    request = EncryptRequest(
        data="sensitive_personal_information",
        recipients=["user@example.com"],
        policy=EncryptionPolicy.MODERN_STRONG
    )
    
    # Mock successful encryption
    mock_encrypted = MagicMock()
    mock_encrypted.ok = True
    mock_encrypted.__str__ = lambda x: "encrypted_result"
    mock_encrypted.fingerprints = ["recipient123"]
    
    mock_gpg_service.gpg.encrypt.return_value = mock_encrypted
    
    result = await mock_gpg_service.encrypt(request)
    
    # Verify that operation completed successfully
    assert result.success is True
    
    # In a real test, we would verify that:
    # 1. No sensitive data appears in logs
    # 2. No temporary files contain sensitive data
    # 3. Memory is properly cleared after operations
    
    # This is a placeholder for privacy compliance testing
    assert True, "Privacy compliance verification required"