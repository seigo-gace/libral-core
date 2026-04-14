"""
Libral Governance Layer (LGL) - Revolutionary Schemas
Advanced digital signatures, trust chains, and governance functionality
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# Signature and Cryptography Types
class SignatureAlgorithm(str, Enum):
    """Supported signature algorithms"""
    ECDSA_P256 = "ecdsa-p256"
    ECDSA_SECP256K1 = "ecdsa-secp256k1"
    EDDSA_ED25519 = "eddsa-ed25519"
    RSA_PSS_2048 = "rsa-pss-2048"
    RSA_PSS_4096 = "rsa-pss-4096"
    BLS12_381 = "bls12-381"
    DILITHIUM3 = "dilithium3"  # Post-quantum
    FALCON512 = "falcon512"   # Post-quantum


class HashAlgorithm(str, Enum):
    """Supported hash algorithms"""
    SHA256 = "sha256"
    SHA384 = "sha384"
    SHA512 = "sha512"
    SHA3_256 = "sha3-256"
    SHA3_512 = "sha3-512"
    BLAKE2B = "blake2b"
    BLAKE3 = "blake3"


class SignatureType(str, Enum):
    """Signature operation types"""
    SINGLE = "single"
    MULTI = "multi"
    THRESHOLD = "threshold"
    RING = "ring"
    GROUP = "group"
    AGGREGATE = "aggregate"
    BLIND = "blind"


class TrustLevel(str, Enum):
    """Trust verification levels"""
    UNTRUSTED = "untrusted"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERIFIED = "verified"
    CERTIFIED = "certified"
    ENTERPRISE = "enterprise"


class AttestationType(str, Enum):
    """Attestation types"""
    CODE_SIGNING = "code_signing"
    MODULE_INTEGRITY = "module_integrity"
    DEPLOYMENT_VERIFICATION = "deployment_verification"
    USER_AUTHENTICATION = "user_authentication"
    API_AUTHORIZATION = "api_authorization"
    DATA_INTEGRITY = "data_integrity"
    TIMESTAMP = "timestamp"
    AUDIT_LOG = "audit_log"


class GovernanceAction(str, Enum):
    """Governance actions"""
    APPROVE = "approve"
    REJECT = "reject"
    REVOKE = "revoke"
    SUSPEND = "suspend"
    REINSTATE = "reinstate"
    AUDIT = "audit"
    INVESTIGATE = "investigate"
    ESCALATE = "escalate"


# Core Signature Schema
class DigitalSignature(BaseModel):
    """Digital signature representation"""
    signature_id: str = Field(..., description="Unique signature identifier")
    
    # Signature details
    algorithm: SignatureAlgorithm
    signature_type: SignatureType = Field(default=SignatureType.SINGLE)
    signature_data: str = Field(..., description="Base64 encoded signature")
    
    # Signed content
    content_hash: str = Field(..., description="Hash of signed content")
    hash_algorithm: HashAlgorithm = Field(default=HashAlgorithm.SHA256)
    content_type: str = Field(default="application/octet-stream")
    content_size: Optional[int] = None
    
    # Signer information
    signer_id: str = Field(..., description="Signer identity")
    signer_public_key: str = Field(..., description="Signer's public key")
    signer_certificate: Optional[str] = None
    
    # Multi-signature support
    required_signatures: int = Field(default=1, ge=1)
    collected_signatures: List[Dict[str, Any]] = Field(default_factory=list)
    threshold_reached: bool = Field(default=False)
    
    # Verification status
    verified: Optional[bool] = None
    verification_time: Optional[datetime] = None
    verifier_id: Optional[str] = None
    trust_level: TrustLevel = Field(default=TrustLevel.UNTRUSTED)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    nonce: Optional[str] = None
    context_labels: Dict[str, str] = Field(default_factory=dict)
    
    # Attestation
    attestation_type: Optional[AttestationType] = None
    attestation_data: Dict[str, Any] = Field(default_factory=dict)


class TrustChain(BaseModel):
    """Trust chain representation"""
    chain_id: str = Field(..., description="Unique chain identifier")
    
    # Chain structure
    root_authority: str = Field(..., description="Root trust authority")
    chain_links: List[Dict[str, Any]] = Field(..., description="Chain of trust links")
    chain_depth: int = Field(..., ge=1)
    
    # Verification
    verified: bool = Field(default=False)
    verification_path: List[str] = Field(default_factory=list)
    trust_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Validity
    valid_from: datetime
    valid_until: datetime
    revocation_status: str = Field(default="valid")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    issuer: str
    subject: str


class GovernancePolicy(BaseModel):
    """Governance policy definition"""
    policy_id: str
    name: str
    description: str
    
    # Policy rules
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules and conditions")
    required_approvals: int = Field(default=1, ge=1)
    approval_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Enforcement
    enforcement_level: str = Field(default="strict")
    violations_allowed: int = Field(default=0, ge=0)
    penalty_actions: List[GovernanceAction] = Field(default_factory=list)
    
    # Scope
    applicable_modules: List[str] = Field(default_factory=list)
    applicable_users: List[str] = Field(default_factory=list)
    applicable_actions: List[str] = Field(default_factory=list)
    
    # Lifecycle
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    version: str = Field(default="1.0.0")


# Module and Application Verification
class ModuleAttestation(BaseModel):
    """Module integrity attestation"""
    module_id: str
    module_name: str
    module_version: str
    
    # Integrity verification
    code_hash: str = Field(..., description="Hash of module code")
    dependencies_hash: str = Field(..., description="Hash of dependencies")
    configuration_hash: str = Field(..., description="Hash of configuration")
    
    # Signatures
    developer_signature: DigitalSignature
    build_signature: Optional[DigitalSignature] = None
    deployment_signature: Optional[DigitalSignature] = None
    
    # Verification results
    integrity_verified: bool = Field(default=False)
    dependencies_verified: bool = Field(default=False)
    permissions_verified: bool = Field(default=False)
    
    # Trust assessment
    trust_level: TrustLevel = Field(default=TrustLevel.UNTRUSTED)
    trust_chain: Optional[TrustChain] = None
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Compliance
    compliance_checks: Dict[str, bool] = Field(default_factory=dict)
    security_scan_results: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    attested_at: datetime = Field(default_factory=datetime.utcnow)
    attestor_id: str
    valid_until: datetime


class ApplicationDeployment(BaseModel):
    """Application deployment verification"""
    deployment_id: str
    application_name: str
    application_version: str
    
    # Deployment details
    deployment_environment: str
    deployment_target: str
    deployment_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Verification signatures
    developer_approval: DigitalSignature
    security_approval: Optional[DigitalSignature] = None
    operations_approval: Optional[DigitalSignature] = None
    
    # Pre-deployment checks
    security_scan_passed: bool = Field(default=False)
    dependency_check_passed: bool = Field(default=False)
    configuration_verified: bool = Field(default=False)
    permission_check_passed: bool = Field(default=False)
    
    # Governance approval
    governance_approved: bool = Field(default=False)
    approval_signatures: List[DigitalSignature] = Field(default_factory=list)
    governance_policy_version: Optional[str] = None
    
    # Deployment status
    deployment_status: str = Field(default="pending")
    deployed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    
    # Rollback information
    rollback_available: bool = Field(default=False)
    previous_version: Optional[str] = None
    rollback_signature: Optional[DigitalSignature] = None


# Audit and Compliance
class AuditEvent(BaseModel):
    """Governance audit event"""
    event_id: str
    event_type: str
    event_category: AttestationType
    
    # Event details
    actor_id: str
    target_resource: str
    action_performed: str
    action_result: str
    
    # Signatures and verification
    event_signature: DigitalSignature
    witness_signatures: List[DigitalSignature] = Field(default_factory=list)
    tamper_evident: bool = Field(default=True)
    
    # Context
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Evidence
    before_state_hash: Optional[str] = None
    after_state_hash: Optional[str] = None
    evidence_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Compliance
    compliance_requirements: List[str] = Field(default_factory=list)
    compliance_status: str = Field(default="compliant")
    
    # Timestamps
    event_time: datetime = Field(default_factory=datetime.utcnow)
    recorded_time: datetime = Field(default_factory=datetime.utcnow)
    retention_until: Optional[datetime] = None


class ComplianceReport(BaseModel):
    """Compliance assessment report"""
    report_id: str
    report_type: str
    assessment_period_start: datetime
    assessment_period_end: datetime
    
    # Scope
    assessed_modules: List[str] = Field(default_factory=list)
    assessed_policies: List[str] = Field(default_factory=list)
    assessed_users: List[str] = Field(default_factory=list)
    
    # Results
    total_events_audited: int
    compliant_events: int
    non_compliant_events: int
    compliance_score: float = Field(..., ge=0.0, le=1.0)
    
    # Findings
    critical_findings: List[Dict[str, Any]] = Field(default_factory=list)
    major_findings: List[Dict[str, Any]] = Field(default_factory=list)
    minor_findings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Recommendations
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    remediation_actions: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Signatures
    assessor_signature: DigitalSignature
    reviewer_signature: Optional[DigitalSignature] = None
    approval_signature: Optional[DigitalSignature] = None
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    assessor_id: str
    report_version: str = Field(default="1.0")


# Request/Response Schemas
class SignatureRequest(BaseModel):
    """Digital signature creation request"""
    content: str = Field(..., description="Content to sign (base64 or text)")
    algorithm: SignatureAlgorithm = Field(default=SignatureAlgorithm.EDDSA_ED25519)
    signature_type: SignatureType = Field(default=SignatureType.SINGLE)
    hash_algorithm: HashAlgorithm = Field(default=HashAlgorithm.SHA256)
    
    # Multi-signature options
    required_signatures: int = Field(default=1, ge=1)
    co_signers: List[str] = Field(default_factory=list)
    
    # Attestation
    attestation_type: Optional[AttestationType] = None
    attestation_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Options
    include_timestamp: bool = Field(default=True)
    include_nonce: bool = Field(default=True)
    expires_in_hours: Optional[int] = None
    context_labels: Dict[str, str] = Field(default_factory=dict)


class SignatureResponse(BaseModel):
    """Digital signature creation response"""
    success: bool
    signature: Optional[DigitalSignature] = None
    signature_id: Optional[str] = None
    pending_co_signatures: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    request_id: str


class VerificationRequest(BaseModel):
    """Signature verification request"""
    signature: DigitalSignature
    content: Optional[str] = None
    verify_trust_chain: bool = Field(default=True)
    required_trust_level: TrustLevel = Field(default=TrustLevel.MEDIUM)
    check_revocation: bool = Field(default=True)


class VerificationResponse(BaseModel):
    """Signature verification response"""
    success: bool
    valid: bool
    trust_level: TrustLevel
    verification_details: Dict[str, Any] = Field(default_factory=dict)
    trust_chain_valid: bool = Field(default=False)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    verified_at: datetime = Field(default_factory=datetime.utcnow)


class GovernanceRequest(BaseModel):
    """Governance action request"""
    action: GovernanceAction
    target_resource: str
    target_type: str
    reason: str
    
    # Evidence and justification
    evidence: Dict[str, Any] = Field(default_factory=dict)
    supporting_documents: List[str] = Field(default_factory=list)
    
    # Approval workflow
    required_approvers: List[str] = Field(default_factory=list)
    approval_deadline: Optional[datetime] = None
    escalation_path: List[str] = Field(default_factory=list)
    
    # Context
    requestor_id: str
    urgency_level: str = Field(default="normal")
    business_impact: str = Field(default="low")


class GovernanceResponse(BaseModel):
    """Governance action response"""
    success: bool
    action_id: str
    status: str
    current_approvals: List[Dict[str, Any]] = Field(default_factory=list)
    pending_approvals: List[str] = Field(default_factory=list)
    estimated_completion: Optional[datetime] = None
    error: Optional[str] = None


# System Health and Metrics
class LGLHealthResponse(BaseModel):
    """LGL module health status"""
    status: str
    version: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "signature_engine": {"status": "unknown", "signatures_created": 0, "verifications_performed": 0},
        "trust_chain_manager": {"status": "unknown", "active_chains": 0, "verification_rate": 0},
        "module_attestation": {"status": "unknown", "attested_modules": 0, "trust_level_avg": 0},
        "governance_engine": {"status": "unknown", "active_policies": 0, "pending_approvals": 0},
        "audit_system": {"status": "unknown", "events_logged": 0, "compliance_score": 0}
    })
    uptime_seconds: float
    last_health_check: datetime


class LGLMetrics(BaseModel):
    """LGL module metrics"""
    period_start: datetime
    period_end: datetime
    
    # Signature operations
    signatures_created: int
    signatures_verified: int
    signature_success_rate: float
    
    # Trust and attestation
    trust_chains_created: int
    modules_attested: int
    average_trust_level: float
    high_risk_detections: int
    
    # Governance
    governance_requests: int
    policies_enforced: int
    approval_completion_rate: float
    average_approval_time_hours: float
    
    # Audit and compliance
    audit_events_recorded: int
    compliance_violations: int
    audit_integrity_score: float
    
    # Performance
    average_signature_time_ms: float
    average_verification_time_ms: float
    system_load_average: float


# Error Schema
class LGLError(BaseModel):
    """LGL module error response"""
    error_code: str
    error_message: str
    component: str = Field(..., description="signature_engine|trust_chain|module_attestation|governance|audit")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str