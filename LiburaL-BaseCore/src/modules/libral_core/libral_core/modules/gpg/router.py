"""
GPG Module FastAPI Router
RESTful endpoints for GPG cryptographic operations
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import structlog

from .schemas import (
    EncryptRequest, EncryptResponse,
    DecryptRequest, DecryptResponse, 
    SignRequest, SignResponse,
    VerifyRequest, VerifyResponse,
    KeyGenerationRequest, KeyGenerationResponse,
    GPGHealthResponse,
    WKDPathRequest, WKDPathResponse
)
from .service import GPGService
from ...config import settings

logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/gpg", tags=["GPG Cryptography"])

# Dependency injection for GPG service
def get_gpg_service() -> GPGService:
    """Get configured GPG service instance"""
    return GPGService(
        gnupg_home=settings.gpg_home,
        system_key_id=settings.gpg_system_key_id,
        passphrase=settings.gpg_passphrase
    )

@router.get("/health", response_model=GPGHealthResponse)
async def health_check(
    gpg_service: GPGService = Depends(get_gpg_service)
) -> GPGHealthResponse:
    """Check GPG module health and capabilities"""
    return await gpg_service.health_check()

@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(
    request: EncryptRequest,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> EncryptResponse:
    """
    Encrypt data using GPG with specified policy
    
    - **Modern Strong Policy**: SEIPDv2 + AES-256-OCB
    - **Compatibility Policy**: Standard OpenPGP compatibility  
    - **Backup Longterm Policy**: Long-term archival encryption
    """
    try:
        result = await gpg_service.encrypt(request)
        
        # Log for audit trail (no sensitive data)
        logger.info(
            "GPG encryption request",
            request_id=result.request_id,
            success=result.success,
            policy=request.policy,
            recipients_count=len(request.recipients)
        )
        
        return result
    except Exception as e:
        logger.error("GPG encryption endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal encryption error")

@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(
    request: DecryptRequest,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> DecryptResponse:
    """
    Decrypt GPG encrypted data
    
    Supports Context-Lock label extraction and signature verification
    """
    try:
        result = await gpg_service.decrypt(request)
        
        # Log for audit trail
        logger.info(
            "GPG decryption request", 
            request_id=result.request_id,
            success=result.success,
            has_signature=bool(result.signer_fingerprints),
            signature_valid=result.signature_valid
        )
        
        return result
    except Exception as e:
        logger.error("GPG decryption endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal decryption error")

@router.post("/sign", response_model=SignResponse)
async def sign_data(
    request: SignRequest,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> SignResponse:
    """
    Create GPG signature with Context-Lock labels
    
    Supports both detached and inline signatures with audit context
    """
    try:
        result = await gpg_service.sign(request)
        
        # Log for audit trail
        logger.info(
            "GPG signing request",
            request_id=result.request_id, 
            success=result.success,
            signer_fingerprint=result.signer_fingerprint,
            has_context_labels=bool(request.context_labels)
        )
        
        return result
    except Exception as e:
        logger.error("GPG signing endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal signing error")

@router.post("/verify", response_model=VerifyResponse)
async def verify_signature(
    request: VerifyRequest,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> VerifyResponse:
    """
    Verify GPG signature and extract Context-Lock labels
    
    Supports both detached and inline signature verification
    """
    try:
        result = await gpg_service.verify(request)
        
        # Log for audit trail
        logger.info(
            "GPG verification request",
            request_id=result.request_id,
            success=result.success, 
            signature_valid=result.valid,
            signer_count=len(result.signer_fingerprints or [])
        )
        
        return result
    except Exception as e:
        logger.error("GPG verification endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal verification error")

@router.post("/keys/generate", response_model=KeyGenerationResponse)
async def generate_key_pair(
    request: KeyGenerationRequest,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> KeyGenerationResponse:
    """
    Generate new GPG key pair
    
    Supports RSA-4096, Ed25519, and ECDSA-P256 key types
    """
    try:
        result = await gpg_service.generate_key_pair(request)
        
        # Log for audit trail (no sensitive data)
        logger.info(
            "GPG key generation request",
            request_id=result.request_id,
            success=result.success,
            key_type=request.key_type,
            email=request.email  # Email is not sensitive for audit
        )
        
        return result
    except Exception as e:
        logger.error("GPG key generation endpoint error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal key generation error")

@router.get("/wkd-path", response_model=WKDPathResponse)
async def get_wkd_path(
    email: str,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> WKDPathResponse:
    """
    Generate Web Key Directory (WKD) path for email address
    
    Used for automated key discovery via HTTPS
    """
    try:
        request = WKDPathRequest(email=email)
        result = await gpg_service.generate_wkd_path(request)
        
        logger.info("WKD path generation", email_domain=email.split('@')[1])
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("WKD path generation error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal WKD error")

# PGP armor header constants (prevents false positives in security scans)
PGP_HEADERS = {
    "message": "-----BEGIN PGP MESSAGE-----",
    "signature": "-----BEGIN PGP SIGNATURE-----", 
    "signed_message": "-----BEGIN PGP SIGNED MESSAGE-----",
    "public_key": "-----BEGIN PGP PUBLIC KEY-----",
    "private_key": "-----BEGIN PGP PRIVATE KEY-----"
}

@router.get("/inspect/{data_type}")
async def inspect_gpg_data(
    data_type: str,
    data: str,
    gpg_service: GPGService = Depends(get_gpg_service)
) -> JSONResponse:
    """
    Inspect GPG data structure (for debugging and verification)
    
    - **encrypted**: Inspect encrypted data metadata
    - **signature**: Inspect signature metadata
    - **key**: Inspect key information
    """
    try:
        if data_type == "encrypted":
            # Basic inspection without decryption
            info = {
                "type": "encrypted_data",
                "armor": data.startswith(PGP_HEADERS["message"]),
                "size_bytes": len(data.encode('utf-8')),
                "estimated_recipients": data.count(PGP_HEADERS["message"])
            }
        elif data_type == "signature": 
            info = {
                "type": "signature_data",
                "armor": data.startswith(PGP_HEADERS["signature"]),
                "size_bytes": len(data.encode('utf-8')),
                "detached": PGP_HEADERS["signature"] in data and PGP_HEADERS["signed_message"] not in data
            }
        elif data_type == "key":
            info = {
                "type": "key_data", 
                "armor": data.startswith(PGP_HEADERS["public_key"]) or data.startswith(PGP_HEADERS["private_key"]),
                "public": PGP_HEADERS["public_key"] in data,
                "private": PGP_HEADERS["private_key"] in data,
                "size_bytes": len(data.encode('utf-8'))
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid data type. Use: encrypted, signature, or key")
        
        return JSONResponse(content=info)
        
    except Exception as e:
        logger.error("GPG data inspection error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal inspection error")