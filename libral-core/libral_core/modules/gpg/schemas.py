"""
GPG Module Pydantic Schemas
Type-safe API contracts for GPG operations
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class KeyType(str, Enum):
    """Supported key types"""
    RSA_4096 = "rsa4096"
    ED25519 = "ed25519" 
    ECDSA_P256 = "ecdsa-p256"


class EncryptionPolicy(str, Enum):
    """Encryption policy presets"""
    MODERN_STRONG = "modern-strong"  # SEIPDv2 + AES-256-OCB
    COMPAT = "compat"               # Standard OpenPGP compatibility
    BACKUP_LONGTERM = "backup-longterm"  # Long-term archival


class ContextLockLabel(BaseModel):
    """Context-Lock signature label"""
    key: str = Field(..., description="Label key")
    value: str = Field(..., description="Label value")


# Request Schemas
class EncryptRequest(BaseModel):
    """Encrypt data request"""
    data: str = Field(..., description="Data to encrypt (base64 or plain text)")
    recipients: List[str] = Field(..., description="Recipient key IDs or emails")
    policy: EncryptionPolicy = Field(default=EncryptionPolicy.MODERN_STRONG)
    armor: bool = Field(default=True, description="ASCII armor output")
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    
    @validator('recipients')
    def recipients_not_empty(cls, v):
        if not v:
            raise ValueError('At least one recipient is required')
        return v


class DecryptRequest(BaseModel):
    """Decrypt data request"""
    encrypted_data: str = Field(..., description="GPG encrypted data")
    passphrase: Optional[str] = Field(default=None, description="Key passphrase")
    

class SignRequest(BaseModel):
    """Sign data request"""
    data: str = Field(..., description="Data to sign")
    key_id: Optional[str] = Field(default=None, description="Signing key ID")
    passphrase: Optional[str] = Field(default=None, description="Key passphrase") 
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    detached: bool = Field(default=True, description="Create detached signature")


class VerifyRequest(BaseModel):
    """Verify signature request"""
    signed_data: str = Field(..., description="Signed data or signature")
    original_data: Optional[str] = Field(default=None, description="Original data for detached signature")


class KeyGenerationRequest(BaseModel):
    """Generate key pair request"""
    key_type: KeyType = Field(default=KeyType.RSA_4096)
    name: str = Field(..., description="Key owner name")
    email: str = Field(..., description="Key owner email")
    comment: Optional[str] = Field(default=None, description="Key comment")
    passphrase: Optional[str] = Field(default=None, description="Key passphrase")
    expire_date: Optional[datetime] = Field(default=None, description="Key expiration")


# Response Schemas
class EncryptResponse(BaseModel):
    """Encrypt operation response"""
    success: bool
    encrypted_data: Optional[str] = Field(default=None)
    fingerprints: List[str] = Field(default_factory=list, description="Recipient key fingerprints")
    policy_applied: EncryptionPolicy
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


class DecryptResponse(BaseModel):
    """Decrypt operation response"""
    success: bool
    decrypted_data: Optional[str] = Field(default=None)
    signer_fingerprints: List[str] = Field(default_factory=list)
    signature_valid: Optional[bool] = Field(default=None)
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


class SignResponse(BaseModel):
    """Sign operation response"""
    success: bool
    signature: Optional[str] = Field(default=None)
    signer_fingerprint: Optional[str] = Field(default=None)
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


class VerifyResponse(BaseModel):
    """Verify operation response"""
    success: bool
    valid: Optional[bool] = Field(default=None)
    signer_fingerprints: List[str] = Field(default_factory=list)
    signature_timestamp: Optional[datetime] = Field(default=None)
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


class KeyInfo(BaseModel):
    """Key information"""
    key_id: str
    fingerprint: str
    user_ids: List[str]
    algorithm: str
    key_size: int
    creation_date: datetime
    expiration_date: Optional[datetime] = None
    is_secret: bool
    trust_level: str


class KeyGenerationResponse(BaseModel):
    """Key generation response"""
    success: bool
    public_key: Optional[str] = Field(default=None)
    key_info: Optional[KeyInfo] = Field(default=None)
    fingerprint: Optional[str] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Unique request identifier")


# Utility Schemas
class WKDPathRequest(BaseModel):
    """WKD path generation request"""
    email: str = Field(..., description="Email address for WKD lookup")


class WKDPathResponse(BaseModel):
    """WKD path response"""
    wkd_path: str = Field(..., description="WKD lookup path")
    local_part: str = Field(..., description="Local part of email")
    domain: str = Field(..., description="Domain part of email")
    z_base32: str = Field(..., description="Z-Base32 encoded local part")


class GPGHealthResponse(BaseModel):
    """GPG module health check response"""
    status: str = Field(..., description="Module status")
    version: str = Field(..., description="GPG version")
    keys_available: int = Field(..., description="Available keys count")
    default_key: Optional[str] = Field(default=None, description="Default key fingerprint")
    policies_loaded: List[str] = Field(..., description="Available encryption policies")
    last_check: datetime = Field(..., description="Last health check timestamp")