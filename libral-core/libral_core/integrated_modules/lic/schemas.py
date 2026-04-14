"""
Libral Identity Core (LIC) - Unified Schemas
Integrated GPG + Auth + ZKP + DID functionality
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# Core Identity Types
class IdentityProvider(str, Enum):
    """Supported identity providers"""
    TELEGRAM = "telegram"
    GPG_KEY = "gpg_key"
    DID = "did"
    ZKP = "zkp"
    ANONYMOUS = "anonymous"


class KeyType(str, Enum):
    """Supported key types"""
    RSA_4096 = "rsa4096"
    ED25519 = "ed25519" 
    ECDSA_P256 = "ecdsa-p256"
    ECDSA_SECP256K1 = "ecdsa-secp256k1"  # For DID compatibility
    BLS12_381 = "bls12-381"  # For ZKP operations


class EncryptionPolicy(str, Enum):
    """Encryption policy presets"""
    MODERN_STRONG = "modern-strong"
    COMPAT = "compat"
    BACKUP_LONGTERM = "backup-longterm"
    ZKP_OPTIMIZED = "zkp-optimized"
    DID_COMPLIANT = "did-compliant"


class SessionStatus(str, Enum):
    """Authentication session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"
    ZKP_PENDING = "zkp_pending"


class DIDMethod(str, Enum):
    """Supported DID methods"""
    KEY = "key"
    WEB = "web"
    ION = "ion"
    LIBRAL = "libral"  # Custom Libral DID method


class ZKPScheme(str, Enum):
    """Supported ZKP schemes"""
    PLONK = "plonk"
    GROTH16 = "groth16"
    BULLETPROOFS = "bulletproofs"
    STARK = "stark"


# GPG Integration Schemas
class GPGOperation(BaseModel):
    """GPG operation request"""
    operation: str = Field(..., description="encrypt|decrypt|sign|verify")
    data: str = Field(..., description="Data to process")
    recipients: Optional[List[str]] = Field(default=None)
    key_id: Optional[str] = Field(default=None)
    policy: EncryptionPolicy = Field(default=EncryptionPolicy.MODERN_STRONG)
    context_labels: Optional[Dict[str, str]] = Field(default=None)


class GPGResponse(BaseModel):
    """GPG operation response"""
    success: bool
    result: Optional[str] = Field(default=None)
    fingerprints: List[str] = Field(default_factory=list)
    context_labels: Optional[Dict[str, str]] = Field(default=None)
    error: Optional[str] = Field(default=None)
    request_id: str


# Authentication Schemas
class TelegramAuthData(BaseModel):
    """Telegram OAuth data"""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str


class PersonalLogServer(BaseModel):
    """Personal log server configuration"""
    user_id: str
    telegram_group_id: Optional[int] = None
    telegram_group_invite_link: Optional[str] = None
    log_encryption_key: Optional[str] = None
    encryption_enabled: bool = True
    setup_completed_at: Optional[datetime] = None
    last_log_sent: Optional[datetime] = None


# DID Schemas
class DIDDocument(BaseModel):
    """W3C DID Document"""
    context: List[str] = Field(default=["https://www.w3.org/ns/did/v1"])
    id: str = Field(..., description="DID identifier")
    controller: Optional[Union[str, List[str]]] = None
    verification_method: List[Dict[str, Any]] = Field(default_factory=list)
    authentication: Optional[List[Union[str, Dict[str, Any]]]] = None
    assertion_method: Optional[List[Union[str, Dict[str, Any]]]] = None
    key_agreement: Optional[List[Union[str, Dict[str, Any]]]] = None
    capability_invocation: Optional[List[Union[str, Dict[str, Any]]]] = None
    capability_delegation: Optional[List[Union[str, Dict[str, Any]]]] = None
    service: Optional[List[Dict[str, Any]]] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    proof: Optional[Dict[str, Any]] = None


class DIDCreateRequest(BaseModel):
    """Create DID request"""
    method: DIDMethod = Field(default=DIDMethod.LIBRAL)
    key_type: KeyType = Field(default=KeyType.ED25519)
    controller: Optional[str] = None
    services: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    context_labels: Optional[Dict[str, str]] = Field(default=None)


class DIDResolveRequest(BaseModel):
    """Resolve DID request"""
    did: str = Field(..., description="DID to resolve")
    accept: str = Field(default="application/did+ld+json")


class DIDUpdateRequest(BaseModel):
    """Update DID document request"""
    did: str
    document: DIDDocument
    proof: Dict[str, Any] = Field(..., description="Update authorization proof")


# ZKP Schemas
class ZKPCircuit(BaseModel):
    """Zero Knowledge Proof Circuit"""
    circuit_id: str
    scheme: ZKPScheme
    circuit_definition: Dict[str, Any]
    public_inputs: List[str] = Field(default_factory=list)
    private_inputs: List[str] = Field(default_factory=list)
    constraints: Dict[str, Any]
    trusted_setup: Optional[Dict[str, Any]] = None


class ZKPProofRequest(BaseModel):
    """Generate ZKP proof request"""
    circuit_id: str
    public_inputs: Dict[str, Any]
    private_inputs: Dict[str, Any]
    scheme: ZKPScheme = Field(default=ZKPScheme.PLONK)
    context_labels: Optional[Dict[str, str]] = Field(default=None)


class ZKPProof(BaseModel):
    """Zero Knowledge Proof"""
    circuit_id: str
    scheme: ZKPScheme
    proof_data: str = Field(..., description="Base64 encoded proof")
    public_inputs: Dict[str, Any]
    verification_key: str
    created_at: datetime
    context_labels: Optional[Dict[str, str]] = Field(default=None)


class ZKPVerifyRequest(BaseModel):
    """Verify ZKP proof request"""
    proof: ZKPProof
    expected_public_inputs: Optional[Dict[str, Any]] = None


# Unified Identity Schemas
class IdentityProfile(BaseModel):
    """Unified identity profile"""
    user_id: str = Field(..., description="Internal user ID (UUID)")
    
    # Multi-provider identity
    telegram_id: Optional[int] = None
    did: Optional[str] = None
    gpg_fingerprint: Optional[str] = None
    zkp_identity: Optional[str] = None
    
    # Profile information
    display_name: str = Field(..., max_length=64)
    username: Optional[str] = Field(default=None, max_length=32)
    preferred_language: str = Field(default="ja", pattern="^[a-z]{2}$")
    timezone: str = Field(default="Asia/Tokyo")
    
    # Privacy settings
    data_retention_hours: int = Field(default=24, ge=1, le=8760)
    analytics_enabled: bool = Field(default=False)
    context_lock_enabled: bool = Field(default=True)
    
    # Personal log server
    personal_log_server: Optional[PersonalLogServer] = None
    
    # Account status
    created_at: datetime
    last_active: datetime
    is_active: bool = True


class AuthenticationRequest(BaseModel):
    """Unified authentication request"""
    provider: IdentityProvider
    
    # Provider-specific data
    telegram_data: Optional[TelegramAuthData] = None
    gpg_signature: Optional[str] = None
    did_proof: Optional[Dict[str, Any]] = None
    zkp_proof: Optional[ZKPProof] = None
    
    # Common options
    create_personal_log_server: bool = Field(default=True)
    context_labels: Optional[Dict[str, str]] = Field(default=None)


class AuthenticationResponse(BaseModel):
    """Unified authentication response"""
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_profile: Optional[IdentityProfile] = None
    personal_log_server: Optional[PersonalLogServer] = None
    session_expires_at: Optional[datetime] = None
    error: Optional[str] = None
    request_id: str


class SessionInfo(BaseModel):
    """Current session information"""
    session_id: str
    user_id: str
    provider: IdentityProvider
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    context_labels: Optional[Dict[str, str]] = Field(default=None)


# Health and Status
class LICHealthResponse(BaseModel):
    """LIC module health status"""
    status: str
    version: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "gpg": {"status": "unknown", "keys_available": 0},
        "authentication": {"status": "unknown", "active_sessions": 0},
        "did": {"status": "unknown", "documents_cached": 0},
        "zkp": {"status": "unknown", "circuits_loaded": 0},
        "personal_log_servers": {"status": "unknown", "active_servers": 0}
    })
    uptime_seconds: float
    last_health_check: datetime


# Error Schemas
class LICError(BaseModel):
    """LIC module error response"""
    error_code: str
    error_message: str
    component: str = Field(..., description="gpg|auth|did|zkp")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str