"""
Libral Identity Core (LIC) - FastAPI Router
Unified API endpoints for GPG + Authentication + ZKP + DID
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .schemas import (
    AuthenticationRequest, AuthenticationResponse,
    DIDCreateRequest, DIDDocument, DIDResolveRequest, DIDUpdateRequest,
    GPGOperation, GPGResponse,
    IdentityProfile, LICHealthResponse,
    SessionInfo, ZKPCircuit, ZKPProof, ZKPProofRequest, ZKPVerifyRequest
)
from .service import LibralIdentityCore

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2/identity", tags=["Libral Identity Core"])

# Initialize LIC service (in production, this would be dependency injected)
lic_service = LibralIdentityCore()

# Security
security = HTTPBearer()


# Dependency for authenticated requests
async def get_current_session(credentials: HTTPAuthorizationCredentials = Depends(security)) -> SessionInfo:
    """Get current authenticated session"""
    token = credentials.credentials
    
    # Extract session ID from token (simplified)
    if not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    session_id = token.replace("access_token_", "")
    
    if session_id not in lic_service.sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )
    
    session = lic_service.sessions[session_id]
    
    # Check if session is expired
    if session.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Update last activity
    session.last_activity = datetime.utcnow()
    
    return session


# Health and Status Endpoints
@router.get("/health", response_model=LICHealthResponse)
async def get_health():
    """Get LIC module health status"""
    return await lic_service.get_health()


# Authentication Endpoints
@router.post("/auth", response_model=AuthenticationResponse)
async def authenticate(request: AuthenticationRequest, http_request: Request):
    """Unified authentication endpoint"""
    try:
        logger.info("Authentication request", 
                   provider=request.provider,
                   client_ip=http_request.client.host if http_request.client else "unknown")
        
        response = await lic_service.authenticate(request)
        
        if response.success:
            logger.info("Authentication successful", 
                       provider=request.provider,
                       user_id=response.user_profile.user_id if response.user_profile else None)
        else:
            logger.warning("Authentication failed", 
                          provider=request.provider,
                          error=response.error)
        
        return response
        
    except Exception as e:
        logger.error("Authentication endpoint error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.get("/session", response_model=SessionInfo)
async def get_session_info(session: SessionInfo = Depends(get_current_session)):
    """Get current session information"""
    return session


@router.post("/session/refresh")
async def refresh_session(session: SessionInfo = Depends(get_current_session)):
    """Refresh access token"""
    # Generate new access token
    new_token = await lic_service._generate_access_token(session)
    
    return {
        "success": True,
        "access_token": new_token,
        "expires_at": session.expires_at.isoformat()
    }


@router.delete("/session")
async def logout(session: SessionInfo = Depends(get_current_session)):
    """Logout and revoke session"""
    session.status = "revoked"
    
    logger.info("Session revoked", session_id=session.session_id, user_id=session.user_id)
    
    return {"success": True, "message": "Session revoked"}


# GPG Operations Endpoints
@router.post("/gpg", response_model=GPGResponse)
async def gpg_operation(
    operation: GPGOperation,
    session: SessionInfo = Depends(get_current_session)
):
    """Execute GPG operation (encrypt, decrypt, sign, verify)"""
    try:
        logger.info("GPG operation request", 
                   operation=operation.operation,
                   user_id=session.user_id)
        
        response = await lic_service.gpg_core.process_operation(operation)
        
        logger.info("GPG operation completed", 
                   operation=operation.operation,
                   success=response.success,
                   user_id=session.user_id)
        
        return response
        
    except Exception as e:
        logger.error("GPG operation error", error=str(e), operation=operation.operation)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GPG operation failed"
        )


# DID Management Endpoints
@router.post("/did/create", response_model=Dict[str, Any])
async def create_did(
    request: DIDCreateRequest,
    session: SessionInfo = Depends(get_current_session)
):
    """Create new DID document"""
    try:
        did, document = await lic_service.did_manager.create_did(request)
        
        logger.info("DID created", did=did, user_id=session.user_id)
        
        return {
            "success": True,
            "did": did,
            "document": document.dict()
        }
        
    except Exception as e:
        logger.error("DID creation error", error=str(e), user_id=session.user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DID creation failed: {str(e)}"
        )


@router.get("/did/resolve/{did:path}", response_model=DIDDocument)
async def resolve_did(did: str):
    """Resolve DID document (public endpoint)"""
    try:
        request = DIDResolveRequest(did=did)
        document = await lic_service.did_manager.resolve_did(request)
        
        logger.info("DID resolved", did=did)
        return document
        
    except Exception as e:
        logger.error("DID resolution error", error=str(e), did=did)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"DID not found: {did}"
        )


@router.put("/did/update", response_model=DIDDocument)
async def update_did(
    request: DIDUpdateRequest,
    session: SessionInfo = Depends(get_current_session)
):
    """Update DID document"""
    try:
        document = await lic_service.did_manager.update_did(request)
        
        logger.info("DID updated", did=request.did, user_id=session.user_id)
        return document
        
    except Exception as e:
        logger.error("DID update error", error=str(e), did=request.did)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DID update failed: {str(e)}"
        )


# ZKP Endpoints
@router.post("/zkp/circuit/register")
async def register_zkp_circuit(
    circuit: ZKPCircuit,
    session: SessionInfo = Depends(get_current_session)
):
    """Register ZKP circuit"""
    try:
        await lic_service.zkp_engine.register_circuit(circuit)
        
        logger.info("ZKP circuit registered", 
                   circuit_id=circuit.circuit_id,
                   user_id=session.user_id)
        
        return {
            "success": True,
            "circuit_id": circuit.circuit_id,
            "message": "Circuit registered successfully"
        }
        
    except Exception as e:
        logger.error("ZKP circuit registration error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Circuit registration failed: {str(e)}"
        )


@router.post("/zkp/proof/generate", response_model=ZKPProof)
async def generate_zkp_proof(
    request: ZKPProofRequest,
    session: SessionInfo = Depends(get_current_session)
):
    """Generate zero knowledge proof"""
    try:
        proof = await lic_service.zkp_engine.generate_proof(request)
        
        logger.info("ZKP proof generated", 
                   circuit_id=request.circuit_id,
                   user_id=session.user_id)
        
        return proof
        
    except Exception as e:
        logger.error("ZKP proof generation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proof generation failed: {str(e)}"
        )


@router.post("/zkp/proof/verify")
async def verify_zkp_proof(request: ZKPVerifyRequest):
    """Verify zero knowledge proof (public endpoint)"""
    try:
        is_valid = await lic_service.zkp_engine.verify_proof(request)
        
        logger.info("ZKP proof verified", 
                   circuit_id=request.proof.circuit_id,
                   valid=is_valid)
        
        return {
            "success": True,
            "valid": is_valid,
            "circuit_id": request.proof.circuit_id,
            "verification_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("ZKP proof verification error", error=str(e))
        return {
            "success": False,
            "valid": False,
            "error": str(e)
        }


# Personal Log Server Management
@router.get("/personal-log-server")
async def get_personal_log_server(session: SessionInfo = Depends(get_current_session)):
    """Get personal log server status"""
    if session.user_id in lic_service.personal_log_servers:
        server = lic_service.personal_log_servers[session.user_id]
        return {
            "success": True,
            "server": server.dict()
        }
    else:
        return {
            "success": False,
            "message": "Personal log server not configured"
        }


@router.post("/personal-log-server/setup")
async def setup_personal_log_server(session: SessionInfo = Depends(get_current_session)):
    """Setup personal log server"""
    try:
        server = await lic_service._setup_personal_log_server(session.user_id)
        
        logger.info("Personal log server setup initiated", user_id=session.user_id)
        
        return {
            "success": True,
            "server": server.dict(),
            "message": "Personal log server setup completed"
        }
        
    except Exception as e:
        logger.error("Personal log server setup error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Setup failed: {str(e)}"
        )


# User Profile Management
@router.get("/profile", response_model=IdentityProfile)
async def get_user_profile(session: SessionInfo = Depends(get_current_session)):
    """Get user identity profile"""
    # In a real implementation, this would fetch from database
    # For now, create a basic profile from session
    profile = IdentityProfile(
        user_id=session.user_id,
        display_name="User",
        created_at=session.created_at,
        last_active=session.last_activity
    )
    
    return profile


@router.put("/profile")
async def update_user_profile(
    updates: Dict[str, Any],
    session: SessionInfo = Depends(get_current_session)
):
    """Update user profile"""
    # In a real implementation, this would update the database
    logger.info("Profile update requested", 
               user_id=session.user_id,
               updates=list(updates.keys()))
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "updated_fields": list(updates.keys())
    }


# Admin and Debug Endpoints (would be restricted in production)
@router.get("/admin/sessions")
async def list_sessions(session: SessionInfo = Depends(get_current_session)):
    """List all active sessions (admin only)"""
    # In production, this would check admin permissions
    sessions_info = []
    for sess_id, sess in lic_service.sessions.items():
        sessions_info.append({
            "session_id": sess_id,
            "user_id": sess.user_id,
            "provider": sess.provider,
            "status": sess.status,
            "created_at": sess.created_at.isoformat(),
            "expires_at": sess.expires_at.isoformat(),
            "last_activity": sess.last_activity.isoformat()
        })
    
    return {
        "success": True,
        "sessions": sessions_info,
        "total_count": len(sessions_info)
    }


@router.get("/admin/stats")
async def get_statistics():
    """Get LIC module statistics"""
    return {
        "success": True,
        "statistics": {
            "active_sessions": len(lic_service.sessions),
            "cached_did_documents": len(lic_service.did_manager.documents_cache),
            "registered_zkp_circuits": len(lic_service.zkp_engine.circuits_cache),
            "cached_zkp_proofs": len(lic_service.zkp_engine.proofs_cache),
            "personal_log_servers": len(lic_service.personal_log_servers),
            "gpg_keys_available": len(lic_service.gpg_core.gpg.list_keys()) if lic_service.gpg_core.gpg else 0
        },
        "timestamp": datetime.utcnow().isoformat()
    }