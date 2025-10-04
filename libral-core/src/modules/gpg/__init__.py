"""
GPG Module - Week 1 Implementation
Foundation security module for all other modules

Features:
- .env.gpg encryption/decryption  
- Database field-level encryption
- Module inter-communication encryption
- Context-Lock signatures (SEIPDv2/AES-256-OCB)
- OpenPGP v6 key support
- WKD (Web Key Directory) support
"""

from .service import GPGService
from .schemas import (
    EncryptRequest, 
    EncryptResponse, 
    DecryptRequest, 
    DecryptResponse,
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse,
    KeyGenerationRequest,
    KeyGenerationResponse
)

__all__ = [
    "GPGService",
    "EncryptRequest",
    "EncryptResponse", 
    "DecryptRequest",
    "DecryptResponse",
    "SignRequest",
    "SignResponse",
    "VerifyRequest", 
    "VerifyResponse",
    "KeyGenerationRequest",
    "KeyGenerationResponse"
]