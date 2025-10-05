"""
Libral Governance Layer (LGL) - FastAPI Router
Revolutionary API endpoints for digital signatures, trust chains, and governance
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .schemas import (
    AuditEvent, ComplianceReport, DigitalSignature, GovernancePolicy,
    GovernanceRequest, GovernanceResponse, LGLHealthResponse, LGLMetrics,
    ModuleAttestation, SignatureRequest, SignatureResponse,
    TrustChain, VerificationRequest, VerificationResponse
)
from .service import LibralGovernanceLayer

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2/governance", tags=["Libral Governance Layer"])

# Initialize LGL service
lgl_service = LibralGovernanceLayer()

# Security
security = HTTPBearer()


# Dependency for authenticated requests
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from access token"""
    token = credentials.credentials
    
    if not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    session_id = token.replace("access_token_", "")
    return f"user_{session_id}"


# Health and Status Endpoints
@router.get("/health", response_model=LGLHealthResponse)
async def get_health():
    """Get LGL module health status"""
    return await lgl_service.get_health()


@router.get("/metrics", response_model=LGLMetrics)
async def get_metrics(period_hours: int = 24):
    """Get LGL module metrics"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=period_hours)
    
    return await lgl_service.get_metrics(start_time, end_time)


# Digital Signature Endpoints
@router.post("/signatures/create", response_model=SignatureResponse)
async def create_signature(
    request: SignatureRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create digital signature"""
    try:
        logger.info("Signature creation request", 
                   algorithm=request.algorithm,
                   signature_type=request.signature_type,
                   user_id=user_id)
        
        response = await lgl_service.signature_engine.create_signature(request, user_id)
        
        if response.success:
            lgl_service.metrics["signatures_created"] += 1
            logger.info("Signature created successfully", 
                       signature_id=response.signature_id,
                       user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Signature creation endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signature creation failed"
        )


@router.post("/signatures/verify", response_model=VerificationResponse)
async def verify_signature(request: VerificationRequest):
    """Verify digital signature (public endpoint)"""
    try:
        logger.info("Signature verification request", 
                   signature_id=request.signature.signature_id,
                   algorithm=request.signature.algorithm)
        
        response = await lgl_service.signature_engine.verify_signature(request)
        
        lgl_service.metrics["signatures_verified"] += 1
        
        logger.info("Signature verification completed", 
                   signature_id=request.signature.signature_id,
                   valid=response.valid,
                   trust_level=response.trust_level)
        
        return response
        
    except Exception as e:
        logger.error("Signature verification error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signature verification failed"
        )


@router.get("/signatures/{signature_id}")
async def get_signature(
    signature_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get signature details"""
    try:
        if signature_id in lgl_service.signature_engine.signature_cache:
            signature = lgl_service.signature_engine.signature_cache[signature_id]
            
            return {
                "success": True,
                "signature": signature.dict()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signature not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Signature retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signature retrieval failed"
        )


# Trust Chain Endpoints
@router.post("/trust-chains/create")
async def create_trust_chain(
    root_authority: str,
    subject: str,
    chain_links: List[Dict[str, Any]],
    user_id: str = Depends(get_current_user_id)
):
    """Create trust chain"""
    try:
        trust_chain = await lgl_service.trust_chain_manager.create_trust_chain(
            root_authority, subject, chain_links
        )
        
        logger.info("Trust chain created", 
                   chain_id=trust_chain.chain_id,
                   verified=trust_chain.verified,
                   user_id=user_id)
        
        return {
            "success": True,
            "trust_chain": trust_chain.dict()
        }
        
    except Exception as e:
        logger.error("Trust chain creation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trust chain creation failed"
        )


@router.get("/trust-chains/{chain_id}")
async def get_trust_chain(chain_id: str):
    """Get trust chain (public endpoint)"""
    try:
        if chain_id in lgl_service.trust_chain_manager.trust_chains:
            chain = lgl_service.trust_chain_manager.trust_chains[chain_id]
            
            return {
                "success": True,
                "trust_chain": chain.dict()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trust chain not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Trust chain retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trust chain retrieval failed"
        )


# Module Attestation Endpoints
@router.post("/modules/attest")
async def attest_module(
    module_id: str,
    module_name: str,
    module_version: str,
    code_hash: str,
    dependencies_hash: str,
    configuration_hash: str,
    developer_signature: Dict[str, Any],
    user_id: str = Depends(get_current_user_id)
):
    """Attest module integrity"""
    try:
        # Convert dict to DigitalSignature object
        dev_sig = DigitalSignature(**developer_signature)
        
        attestation = await lgl_service.module_attestation_manager.attest_module(
            module_id, module_name, module_version,
            code_hash, dependencies_hash, configuration_hash,
            dev_sig, user_id
        )
        
        lgl_service.metrics["modules_attested"] += 1
        
        logger.info("Module attested", 
                   module_id=module_id,
                   trust_level=attestation.trust_level,
                   user_id=user_id)
        
        return {
            "success": True,
            "attestation": attestation.dict()
        }
        
    except Exception as e:
        logger.error("Module attestation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Module attestation failed"
        )


@router.get("/modules/{module_id}/attestation")
async def get_module_attestation(module_id: str):
    """Get module attestation (public endpoint)"""
    try:
        if module_id in lgl_service.module_attestation_manager.attestations:
            attestation = lgl_service.module_attestation_manager.attestations[module_id]
            
            return {
                "success": True,
                "attestation": attestation.dict()
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module attestation not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Module attestation retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Attestation retrieval failed"
        )


# Governance Endpoints
@router.post("/policies/create")
async def create_governance_policy(
    policy: GovernancePolicy,
    user_id: str = Depends(get_current_user_id)
):
    """Create governance policy"""
    try:
        success = await lgl_service.governance_engine.create_policy(policy)
        
        if success:
            logger.info("Governance policy created", 
                       policy_id=policy.policy_id,
                       name=policy.name,
                       user_id=user_id)
            
            return {
                "success": True,
                "policy_id": policy.policy_id,
                "message": "Policy created successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Policy creation failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Policy creation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Policy creation failed"
        )


@router.post("/requests/submit", response_model=GovernanceResponse)
async def submit_governance_request(
    request: GovernanceRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Submit governance request"""
    try:
        # Set requestor ID
        request.requestor_id = user_id
        
        response = await lgl_service.governance_engine.submit_request(request)
        
        if response.success:
            lgl_service.metrics["governance_requests"] += 1
            
            logger.info("Governance request submitted", 
                       action_id=response.action_id,
                       action=request.action,
                       user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Governance request error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Governance request failed"
        )


@router.get("/requests/{action_id}")
async def get_governance_request(
    action_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get governance request status"""
    try:
        if action_id in lgl_service.governance_engine.requests:
            request_data = lgl_service.governance_engine.requests[action_id]
            
            return {
                "success": True,
                "action_id": action_id,
                "status": request_data["status"],
                "created_at": request_data["created_at"].isoformat(),
                "updated_at": request_data["updated_at"].isoformat(),
                "approvals": request_data["approvals"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Governance request not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Governance request retrieval error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Request retrieval failed"
        )


@router.get("/policies")
async def list_governance_policies(
    user_id: str = Depends(get_current_user_id)
):
    """List governance policies"""
    try:
        policies = []
        for policy in lgl_service.governance_engine.policies.values():
            policies.append({
                "policy_id": policy.policy_id,
                "name": policy.name,
                "description": policy.description,
                "active": policy.active,
                "created_at": policy.created_at.isoformat(),
                "version": policy.version
            })
        
        return {
            "success": True,
            "policies": policies,
            "total_count": len(policies)
        }
        
    except Exception as e:
        logger.error("Policy listing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Policy listing failed"
        )


# Audit and Compliance Endpoints
@router.post("/audit/log-event")
async def log_audit_event(
    event_type: str,
    target_resource: str,
    action_performed: str,
    action_result: str,
    event_category: str,
    user_id: str = Depends(get_current_user_id)
):
    """Log audit event"""
    try:
        from .schemas import AttestationType
        
        # Convert string to enum
        category = AttestationType(event_category)
        
        audit_event = await lgl_service.audit_system.log_event(
            event_type, user_id, target_resource, action_performed, action_result, category
        )
        
        lgl_service.metrics["audit_events"] += 1
        
        logger.info("Audit event logged", 
                   event_id=audit_event.event_id,
                   event_type=event_type,
                   user_id=user_id)
        
        return {
            "success": True,
            "event_id": audit_event.event_id,
            "message": "Event logged successfully"
        }
        
    except Exception as e:
        logger.error("Audit logging error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit logging failed"
        )


@router.post("/compliance/generate-report")
async def generate_compliance_report(
    report_type: str,
    period_start: datetime,
    period_end: datetime,
    user_id: str = Depends(get_current_user_id)
):
    """Generate compliance report"""
    try:
        report = await lgl_service.audit_system.generate_compliance_report(
            report_type, period_start, period_end, user_id
        )
        
        logger.info("Compliance report generated", 
                   report_id=report.report_id,
                   compliance_score=report.compliance_score,
                   user_id=user_id)
        
        return {
            "success": True,
            "report": report.dict()
        }
        
    except Exception as e:
        logger.error("Compliance report generation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Compliance report generation failed"
        )


@router.get("/audit/events")
async def list_audit_events(
    limit: int = 100,
    offset: int = 0,
    event_type: Optional[str] = None,
    user_id: str = Depends(get_current_user_id)
):
    """List audit events"""
    try:
        events = []
        all_events = list(lgl_service.audit_system.audit_events.values())
        
        # Filter by event type if specified
        if event_type:
            all_events = [e for e in all_events if e.event_type == event_type]
        
        # Sort by timestamp (newest first)
        all_events.sort(key=lambda x: x.event_time, reverse=True)
        
        # Pagination
        paginated_events = all_events[offset:offset + limit]
        
        for event in paginated_events:
            events.append({
                "event_id": event.event_id,
                "event_type": event.event_type,
                "actor_id": event.actor_id,
                "target_resource": event.target_resource,
                "action_performed": event.action_performed,
                "action_result": event.action_result,
                "event_time": event.event_time.isoformat(),
                "compliance_status": event.compliance_status
            })
        
        return {
            "success": True,
            "events": events,
            "total_count": len(all_events),
            "has_more": (offset + limit) < len(all_events)
        }
        
    except Exception as e:
        logger.error("Audit events listing error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audit events listing failed"
        )


# Admin and Debug Endpoints
@router.get("/admin/stats")
async def get_detailed_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed LGL statistics"""
    try:
        return {
            "success": True,
            "statistics": {
                **lgl_service.metrics,
                "signature_cache_size": len(lgl_service.signature_engine.signature_cache),
                "trust_chains": len(lgl_service.trust_chain_manager.trust_chains),
                "attested_modules": len(lgl_service.module_attestation_manager.attestations),
                "governance_policies": len(lgl_service.governance_engine.policies),
                "pending_requests": len([r for r in lgl_service.governance_engine.requests.values() if r["status"] == "pending"]),
                "audit_events": len(lgl_service.audit_system.audit_events)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Detailed stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statistics retrieval failed"
        )


@router.get("/admin/system-integrity")
async def check_system_integrity(
    user_id: str = Depends(get_current_user_id)
):
    """Check system integrity and security status"""
    try:
        # Check signature engine integrity
        signature_integrity = len(lgl_service.signature_engine.signature_cache) > 0
        
        # Check trust chain validity
        valid_chains = sum(1 for chain in lgl_service.trust_chain_manager.trust_chains.values() if chain.verified)
        trust_chain_integrity = valid_chains == len(lgl_service.trust_chain_manager.trust_chains)
        
        # Check audit system integrity
        audit_integrity = all(event.tamper_evident for event in lgl_service.audit_system.audit_events.values())
        
        overall_integrity = signature_integrity and trust_chain_integrity and audit_integrity
        
        return {
            "success": True,
            "overall_integrity": overall_integrity,
            "components": {
                "signature_engine": {
                    "integrity_status": "healthy" if signature_integrity else "warning",
                    "cached_signatures": len(lgl_service.signature_engine.signature_cache)
                },
                "trust_chains": {
                    "integrity_status": "healthy" if trust_chain_integrity else "warning",
                    "total_chains": len(lgl_service.trust_chain_manager.trust_chains),
                    "verified_chains": valid_chains
                },
                "audit_system": {
                    "integrity_status": "healthy" if audit_integrity else "critical",
                    "total_events": len(lgl_service.audit_system.audit_events),
                    "tamper_evident": audit_integrity
                }
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("System integrity check error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System integrity check failed"
        )