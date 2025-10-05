"""
Libral Identity Core (LIC) - Unified Service
Combines GPG + Authentication + ZKP + DID functionality
"""

import asyncio
import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from uuid import uuid4
import urllib.parse

import httpx
import structlog
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, rsa, ec
import gnupg

from .schemas import (
    AuthenticationRequest, AuthenticationResponse,
    DIDCreateRequest, DIDDocument, DIDResolveRequest, DIDUpdateRequest,
    EncryptionPolicy, GPGOperation, GPGResponse,
    IdentityProfile, IdentityProvider, KeyType,
    LICHealthResponse, PersonalLogServer,
    SessionInfo, SessionStatus,
    TelegramAuthData, ZKPCircuit, ZKPProof, ZKPProofRequest, ZKPVerifyRequest
)

logger = structlog.get_logger(__name__)


class GPGCore:
    """Enhanced GPG operations with DID and ZKP integration"""
    
    def __init__(self, gnupg_home: Optional[str] = None):
        self.gpg_home = gnupg_home or "~/.gnupg"
        self.gpg = gnupg.GPG(gnupghome=self.gpg_home, use_agent=True)
        
        # Encryption policies with ZKP and DID support
        self.policies = {
            EncryptionPolicy.MODERN_STRONG: {
                "cipher_algo": "AES256",
                "compress_algo": 2,
                "digest_algo": "SHA256"
            },
            EncryptionPolicy.ZKP_OPTIMIZED: {
                "cipher_algo": "AES256",
                "compress_algo": 0,  # No compression for ZKP compatibility
                "digest_algo": "SHA256"
            },
            EncryptionPolicy.DID_COMPLIANT: {
                "cipher_algo": "AES256",
                "compress_algo": 1,
                "digest_algo": "SHA256"
            }
        }
    
    async def process_operation(self, operation: GPGOperation) -> GPGResponse:
        """Process unified GPG operation"""
        request_id = str(uuid4())
        
        try:
            if operation.operation == "encrypt":
                result = await self._encrypt_data(
                    operation.data, 
                    operation.recipients or [],
                    operation.policy
                )
            elif operation.operation == "decrypt":
                result = await self._decrypt_data(operation.data)
            elif operation.operation == "sign":
                result = await self._sign_data(
                    operation.data,
                    operation.key_id,
                    operation.context_labels
                )
            elif operation.operation == "verify":
                result = await self._verify_signature(operation.data)
            else:
                raise ValueError(f"Unsupported operation: {operation.operation}")
            
            return GPGResponse(
                success=True,
                result=result.get("data"),
                fingerprints=result.get("fingerprints", []),
                context_labels=operation.context_labels,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error("GPG operation failed", 
                        operation=operation.operation,
                        error=str(e),
                        request_id=request_id)
            
            return GPGResponse(
                success=False,
                error=str(e),
                request_id=request_id
            )
    
    async def _encrypt_data(self, data: str, recipients: List[str], policy: EncryptionPolicy) -> Dict[str, Any]:
        """Encrypt data with specified policy"""
        policy_config = self.policies[policy]
        
        encrypted = self.gpg.encrypt(
            data,
            recipients,
            armor=True,
            cipher_algo=policy_config["cipher_algo"],
            compress_algo=policy_config["compress_algo"]
        )
        
        if not encrypted.ok:
            raise Exception(f"Encryption failed: {encrypted.stderr}")
        
        return {
            "data": str(encrypted),
            "fingerprints": encrypted.fingerprints
        }
    
    async def _decrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """Decrypt GPG encrypted data"""
        decrypted = self.gpg.decrypt(encrypted_data)
        
        if not decrypted.ok:
            raise Exception(f"Decryption failed: {decrypted.stderr}")
        
        return {
            "data": str(decrypted),
            "fingerprints": [decrypted.fingerprint] if decrypted.fingerprint else []
        }
    
    async def _sign_data(self, data: str, key_id: Optional[str], context_labels: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Sign data with context labels"""
        # Add context labels to data if provided
        if context_labels:
            context_data = json.dumps(context_labels, sort_keys=True)
            data_to_sign = f"{data}\n---CONTEXT---\n{context_data}"
        else:
            data_to_sign = data
        
        signed = self.gpg.sign(
            data_to_sign,
            keyid=key_id,
            detach=True
        )
        
        if not signed.data:
            raise Exception("Signing failed")
        
        return {
            "data": str(signed),
            "fingerprints": [signed.fingerprint] if signed.fingerprint else []
        }
    
    async def _verify_signature(self, signed_data: str) -> Dict[str, Any]:
        """Verify GPG signature"""
        verified = self.gpg.verify(signed_data)
        
        return {
            "data": f"Valid: {verified.valid}",
            "fingerprints": [verified.fingerprint] if verified.fingerprint else []
        }


class DIDManager:
    """Decentralized Identity Document management"""
    
    def __init__(self):
        self.documents_cache: Dict[str, DIDDocument] = {}
        self.key_cache: Dict[str, Any] = {}
    
    async def create_did(self, request: DIDCreateRequest) -> Tuple[str, DIDDocument]:
        """Create a new DID document"""
        try:
            # Generate DID identifier
            if request.method.value == "libral":
                did_suffix = secrets.token_urlsafe(32)
                did = f"did:libral:{did_suffix}"
            elif request.method.value == "key":
                # Generate key and create did:key
                key = await self._generate_key(request.key_type)
                public_key_bytes = await self._get_public_key_bytes(key)
                did = f"did:key:{base64.urlsafe_b64encode(public_key_bytes).decode().rstrip('=')}"
            else:
                raise ValueError(f"Unsupported DID method: {request.method}")
            
            # Create verification method
            verification_method = {
                "id": f"{did}#key-1",
                "type": self._get_verification_method_type(request.key_type),
                "controller": did,
                "publicKeyMultibase": await self._encode_public_key(key)
            }
            
            # Create DID document
            document = DIDDocument(
                id=did,
                controller=request.controller or did,
                verification_method=[verification_method],
                authentication=[verification_method["id"]],
                assertion_method=[verification_method["id"]],
                service=request.services or [],
                created=datetime.utcnow()
            )
            
            # Cache the document
            self.documents_cache[did] = document
            self.key_cache[did] = key
            
            logger.info("DID created", did=did, method=request.method)
            return did, document
            
        except Exception as e:
            logger.error("DID creation failed", error=str(e), method=request.method)
            raise
    
    async def resolve_did(self, request: DIDResolveRequest) -> DIDDocument:
        """Resolve DID document"""
        did = request.did
        
        # Check cache first
        if did in self.documents_cache:
            return self.documents_cache[did]
        
        # Try to resolve externally
        if did.startswith("did:web:"):
            return await self._resolve_did_web(did)
        elif did.startswith("did:key:"):
            return await self._resolve_did_key(did)
        elif did.startswith("did:libral:"):
            return await self._resolve_did_libral(did)
        else:
            raise ValueError(f"Unsupported DID method: {did}")
    
    async def update_did(self, request: DIDUpdateRequest) -> DIDDocument:
        """Update DID document"""
        # Verify update authorization
        if not await self._verify_update_proof(request.did, request.proof):
            raise ValueError("Invalid update authorization")
        
        # Update document
        request.document.updated = datetime.utcnow()
        self.documents_cache[request.did] = request.document
        
        logger.info("DID updated", did=request.did)
        return request.document
    
    async def _generate_key(self, key_type: KeyType) -> Any:
        """Generate cryptographic key"""
        if key_type == KeyType.ED25519:
            return ed25519.Ed25519PrivateKey.generate()
        elif key_type == KeyType.RSA_4096:
            return rsa.generate_private_key(
                public_exponent=65537,
                key_size=4096
            )
        elif key_type == KeyType.ECDSA_P256:
            return ec.generate_private_key(ec.SECP256R1())
        elif key_type == KeyType.ECDSA_SECP256K1:
            return ec.generate_private_key(ec.SECP256K1())
        else:
            raise ValueError(f"Unsupported key type: {key_type}")
    
    async def _get_public_key_bytes(self, private_key: Any) -> bytes:
        """Extract public key bytes"""
        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    async def _encode_public_key(self, private_key: Any) -> str:
        """Encode public key as multibase"""
        public_key_bytes = await self._get_public_key_bytes(private_key)
        # Simple base64url encoding for now
        return base64.urlsafe_b64encode(public_key_bytes).decode().rstrip('=')
    
    def _get_verification_method_type(self, key_type: KeyType) -> str:
        """Get verification method type for key type"""
        if key_type == KeyType.ED25519:
            return "Ed25519VerificationKey2020"
        elif key_type == KeyType.RSA_4096:
            return "RsaVerificationKey2018"
        elif key_type in [KeyType.ECDSA_P256, KeyType.ECDSA_SECP256K1]:
            return "EcdsaSecp256k1VerificationKey2019"
        else:
            return "JsonWebKey2020"
    
    async def _resolve_did_web(self, did: str) -> DIDDocument:
        """Resolve did:web DID"""
        # Implement did:web resolution
        raise NotImplementedError("did:web resolution not implemented")
    
    async def _resolve_did_key(self, did: str) -> DIDDocument:
        """Resolve did:key DID"""
        # Implement did:key resolution
        raise NotImplementedError("did:key resolution not implemented")
    
    async def _resolve_did_libral(self, did: str) -> DIDDocument:
        """Resolve did:libral DID"""
        # Implement Libral DID resolution
        raise NotImplementedError("did:libral resolution not implemented")
    
    async def _verify_update_proof(self, did: str, proof: Dict[str, Any]) -> bool:
        """Verify DID update authorization proof"""
        # Implement proof verification
        return True  # Placeholder


class ZKPEngine:
    """Zero Knowledge Proof processing engine"""
    
    def __init__(self):
        self.circuits_cache: Dict[str, ZKPCircuit] = {}
        self.proofs_cache: Dict[str, ZKPProof] = {}
    
    async def register_circuit(self, circuit: ZKPCircuit):
        """Register a ZKP circuit"""
        self.circuits_cache[circuit.circuit_id] = circuit
        logger.info("ZKP circuit registered", circuit_id=circuit.circuit_id, scheme=circuit.scheme)
    
    async def generate_proof(self, request: ZKPProofRequest) -> ZKPProof:
        """Generate zero knowledge proof"""
        try:
            if request.circuit_id not in self.circuits_cache:
                raise ValueError(f"Circuit not found: {request.circuit_id}")
            
            circuit = self.circuits_cache[request.circuit_id]
            
            # Generate proof (placeholder implementation)
            proof_data = await self._generate_proof_data(
                circuit,
                request.public_inputs,
                request.private_inputs,
                request.scheme
            )
            
            proof = ZKPProof(
                circuit_id=request.circuit_id,
                scheme=request.scheme,
                proof_data=proof_data,
                public_inputs=request.public_inputs,
                verification_key=await self._get_verification_key(circuit),
                created_at=datetime.utcnow(),
                context_labels=request.context_labels
            )
            
            # Cache the proof
            proof_id = f"{request.circuit_id}-{uuid4().hex[:8]}"
            self.proofs_cache[proof_id] = proof
            
            logger.info("ZKP proof generated", circuit_id=request.circuit_id, proof_id=proof_id)
            return proof
            
        except Exception as e:
            logger.error("ZKP proof generation failed", error=str(e), circuit_id=request.circuit_id)
            raise
    
    async def verify_proof(self, request: ZKPVerifyRequest) -> bool:
        """Verify zero knowledge proof"""
        try:
            proof = request.proof
            
            if proof.circuit_id not in self.circuits_cache:
                raise ValueError(f"Circuit not found: {proof.circuit_id}")
            
            # Verify proof (placeholder implementation)
            is_valid = await self._verify_proof_data(
                proof.proof_data,
                proof.verification_key,
                proof.public_inputs,
                proof.scheme
            )
            
            # Check expected public inputs if provided
            if request.expected_public_inputs:
                inputs_match = proof.public_inputs == request.expected_public_inputs
                is_valid = is_valid and inputs_match
            
            logger.info("ZKP proof verified", 
                       circuit_id=proof.circuit_id,
                       valid=is_valid,
                       scheme=proof.scheme)
            
            return is_valid
            
        except Exception as e:
            logger.error("ZKP proof verification failed", error=str(e))
            return False
    
    async def _generate_proof_data(self, circuit: ZKPCircuit, public_inputs: Dict[str, Any], 
                                  private_inputs: Dict[str, Any], scheme: str) -> str:
        """Generate proof data (placeholder)"""
        # This would integrate with actual ZKP libraries like arkworks, circom, etc.
        combined_data = {
            "circuit": circuit.circuit_id,
            "public": public_inputs,
            "private": hashlib.sha256(json.dumps(private_inputs, sort_keys=True).encode()).hexdigest()
        }
        return base64.b64encode(json.dumps(combined_data).encode()).decode()
    
    async def _get_verification_key(self, circuit: ZKPCircuit) -> str:
        """Get verification key for circuit"""
        # Generate verification key based on circuit
        key_data = {
            "circuit_id": circuit.circuit_id,
            "scheme": circuit.scheme.value,
            "constraints": hashlib.sha256(json.dumps(circuit.constraints, sort_keys=True).encode()).hexdigest()
        }
        return base64.b64encode(json.dumps(key_data).encode()).decode()
    
    async def _verify_proof_data(self, proof_data: str, verification_key: str, 
                                public_inputs: Dict[str, Any], scheme: str) -> bool:
        """Verify proof data (placeholder)"""
        # This would integrate with actual ZKP verification libraries
        try:
            decoded_proof = json.loads(base64.b64decode(proof_data).decode())
            decoded_key = json.loads(base64.b64decode(verification_key).decode())
            
            # Simple validation - in reality this would be cryptographic verification
            return (decoded_proof.get("public") == public_inputs and
                   decoded_key.get("scheme") == scheme)
        except:
            return False


class LibralIdentityCore:
    """Unified Libral Identity Core service"""
    
    def __init__(self, gpg_home: Optional[str] = None, telegram_bot_token: Optional[str] = None):
        self.gpg_core = GPGCore(gnupg_home=gpg_home)
        self.did_manager = DIDManager()
        self.zkp_engine = ZKPEngine()
        
        # Authentication components
        self.sessions: Dict[str, SessionInfo] = {}
        self.personal_log_servers: Dict[str, PersonalLogServer] = {}
        
        # Telegram integration
        self.telegram_bot = Bot(token=telegram_bot_token) if telegram_bot_token else None
        
        logger.info("Libral Identity Core initialized")
    
    async def authenticate(self, request: AuthenticationRequest) -> AuthenticationResponse:
        """Unified authentication across all providers"""
        request_id = str(uuid4())
        
        try:
            if request.provider == IdentityProvider.TELEGRAM:
                return await self._authenticate_telegram(request, request_id)
            elif request.provider == IdentityProvider.GPG_KEY:
                return await self._authenticate_gpg(request, request_id)
            elif request.provider == IdentityProvider.DID:
                return await self._authenticate_did(request, request_id)
            elif request.provider == IdentityProvider.ZKP:
                return await self._authenticate_zkp(request, request_id)
            else:
                raise ValueError(f"Unsupported provider: {request.provider}")
        
        except Exception as e:
            logger.error("Authentication failed", 
                        provider=request.provider,
                        error=str(e),
                        request_id=request_id)
            
            return AuthenticationResponse(
                success=False,
                error=str(e),
                request_id=request_id
            )
    
    async def _authenticate_telegram(self, request: AuthenticationRequest, request_id: str) -> AuthenticationResponse:
        """Authenticate via Telegram OAuth"""
        if not request.telegram_data:
            raise ValueError("Telegram data required")
        
        # Verify Telegram auth hash
        if not await self._verify_telegram_auth(request.telegram_data):
            raise ValueError("Invalid Telegram authentication")
        
        # Create or update user profile
        user_profile = await self._create_or_update_profile(
            provider=IdentityProvider.TELEGRAM,
            telegram_id=request.telegram_data.id,
            display_name=request.telegram_data.first_name
        )
        
        # Setup personal log server if requested
        personal_log_server = None
        if request.create_personal_log_server and self.telegram_bot:
            personal_log_server = await self._setup_personal_log_server(user_profile.user_id)
        
        # Create session
        session = await self._create_session(user_profile, IdentityProvider.TELEGRAM, request.context_labels)
        
        return AuthenticationResponse(
            success=True,
            access_token=await self._generate_access_token(session),
            refresh_token=await self._generate_refresh_token(session),
            user_profile=user_profile,
            personal_log_server=personal_log_server,
            session_expires_at=session.expires_at,
            request_id=request_id
        )
    
    async def _authenticate_gpg(self, request: AuthenticationRequest, request_id: str) -> AuthenticationResponse:
        """Authenticate via GPG signature"""
        # Implement GPG signature authentication
        raise NotImplementedError("GPG authentication not implemented")
    
    async def _authenticate_did(self, request: AuthenticationRequest, request_id: str) -> AuthenticationResponse:
        """Authenticate via DID proof"""
        # Implement DID proof authentication  
        raise NotImplementedError("DID authentication not implemented")
    
    async def _authenticate_zkp(self, request: AuthenticationRequest, request_id: str) -> AuthenticationResponse:
        """Authenticate via Zero Knowledge Proof"""
        # Implement ZKP authentication
        raise NotImplementedError("ZKP authentication not implemented")
    
    async def _verify_telegram_auth(self, telegram_data: TelegramAuthData) -> bool:
        """Verify Telegram OAuth authentication data"""
        # Implement Telegram auth verification
        return True  # Placeholder
    
    async def _create_or_update_profile(self, provider: IdentityProvider, **kwargs) -> IdentityProfile:
        """Create or update user identity profile"""
        user_id = str(uuid4())
        
        profile = IdentityProfile(
            user_id=user_id,
            display_name=kwargs.get('display_name', 'Anonymous User'),
            telegram_id=kwargs.get('telegram_id'),
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow()
        )
        
        return profile
    
    async def _setup_personal_log_server(self, user_id: str) -> PersonalLogServer:
        """Setup personal log server in Telegram"""
        # Implement personal log server setup
        server = PersonalLogServer(
            user_id=user_id,
            setup_completed_at=datetime.utcnow()
        )
        
        self.personal_log_servers[user_id] = server
        return server
    
    async def _create_session(self, profile: IdentityProfile, provider: IdentityProvider, 
                            context_labels: Optional[Dict[str, str]]) -> SessionInfo:
        """Create authentication session"""
        session = SessionInfo(
            session_id=str(uuid4()),
            user_id=profile.user_id,
            provider=provider,
            status=SessionStatus.ACTIVE,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            last_activity=datetime.utcnow(),
            ip_address="0.0.0.0",  # Would be set from request
            user_agent="Unknown",  # Would be set from request
            context_labels=context_labels
        )
        
        self.sessions[session.session_id] = session
        return session
    
    async def _generate_access_token(self, session: SessionInfo) -> str:
        """Generate JWT access token"""
        # Implement JWT token generation
        return f"access_token_{session.session_id}"
    
    async def _generate_refresh_token(self, session: SessionInfo) -> str:
        """Generate refresh token"""
        return f"refresh_token_{session.session_id}"
    
    async def get_health(self) -> LICHealthResponse:
        """Get LIC module health status"""
        return LICHealthResponse(
            status="healthy",
            version="2.0.0",
            components={
                "gpg": {"status": "healthy", "keys_available": len(self.gpg_core.gpg.list_keys())},
                "authentication": {"status": "healthy", "active_sessions": len(self.sessions)},
                "did": {"status": "healthy", "documents_cached": len(self.did_manager.documents_cache)},
                "zkp": {"status": "healthy", "circuits_loaded": len(self.zkp_engine.circuits_cache)},
                "personal_log_servers": {"status": "healthy", "active_servers": len(self.personal_log_servers)}
            },
            uptime_seconds=0.0,  # Would track actual uptime
            last_health_check=datetime.utcnow()
        )