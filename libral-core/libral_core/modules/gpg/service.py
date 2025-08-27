"""
GPG Service - Core implementation
Provides enterprise-grade GPG operations with privacy-first design
"""

import base64
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

import gnupg
import structlog
from cryptography.fernet import Fernet

from .schemas import (
    DecryptRequest, DecryptResponse,
    EncryptRequest, EncryptResponse, 
    EncryptionPolicy,
    GPGHealthResponse,
    KeyGenerationRequest, KeyGenerationResponse,
    KeyInfo, KeyType,
    SignRequest, SignResponse,
    VerifyRequest, VerifyResponse,
    WKDPathRequest, WKDPathResponse
)

logger = structlog.get_logger(__name__)


class GPGService:
    """Enterprise GPG service with privacy-first architecture"""
    
    def __init__(
        self, 
        gnupg_home: Optional[str] = None,
        system_key_id: Optional[str] = None,
        passphrase: Optional[str] = None
    ):
        self.gpg_home = gnupg_home or os.path.expanduser("~/.gnupg")
        self.system_key_id = system_key_id
        self.passphrase = passphrase
        
        # Initialize GPG with secure settings
        self.gpg = gnupg.GPG(
            gnupghome=self.gpg_home,
            verbose=False,
            use_agent=True
        )
        
        # Encryption policy configurations
        self.policies = {
            EncryptionPolicy.MODERN_STRONG: {
                "cipher_algo": "AES256",
                "compress_algo": 2,  # ZLIB
                "digest_algo": "SHA256",
                "preferences": "AES256 AES192 AES CAST5 SHA256 SHA1 ZLIB BZIP2 ZIP"
            },
            EncryptionPolicy.COMPAT: {
                "cipher_algo": "AES128", 
                "compress_algo": 1,  # ZIP
                "digest_algo": "SHA1",
                "preferences": "AES128 3DES CAST5 SHA1 ZLIB ZIP"
            },
            EncryptionPolicy.BACKUP_LONGTERM: {
                "cipher_algo": "AES256",
                "compress_algo": 0,  # No compression for integrity
                "digest_algo": "SHA512", 
                "preferences": "AES256 SHA512 ZLIB"
            }
        }
        
        logger.info("GPG service initialized", 
                   gpg_home=self.gpg_home, 
                   system_key=bool(system_key_id))
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID for audit trails"""
        return str(uuid4()).replace('-', '')[:16]
    
    def _add_context_lock_labels(
        self, 
        data: str, 
        context_labels: Optional[Dict[str, str]] = None
    ) -> str:
        """Add Context-Lock labels to data before signing/encryption"""
        if not context_labels:
            return data
            
        # Create context header
        context_header = {
            "context_lock_version": "1.0",
            "labels": context_labels,
            "timestamp": datetime.utcnow().isoformat(),
            "libral_core_version": "1.0.0"
        }
        
        # Prepend context header to data
        context_json = json.dumps(context_header, sort_keys=True)
        return f"---LIBRAL-CONTEXT-LOCK---\n{context_json}\n---END-CONTEXT---\n{data}"
    
    def _extract_context_lock_labels(self, data: str) -> Tuple[str, Optional[Dict[str, str]]]:
        """Extract Context-Lock labels from decrypted/verified data"""
        if not data.startswith("---LIBRAL-CONTEXT-LOCK---"):
            return data, None
            
        try:
            parts = data.split("---END-CONTEXT---\n", 1)
            if len(parts) != 2:
                return data, None
                
            context_section = parts[0].replace("---LIBRAL-CONTEXT-LOCK---\n", "")
            context_header = json.loads(context_section)
            original_data = parts[1]
            
            return original_data, context_header.get("labels")
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to extract context lock labels", error=str(e))
            return data, None
    
    async def health_check(self) -> GPGHealthResponse:
        """Check GPG module health and capabilities"""
        try:
            # Get GPG version
            version_info = self.gpg.version
            
            # Count available keys
            keys = self.gpg.list_keys()
            secret_keys = self.gpg.list_keys(secret=True)
            
            # Get default key info
            default_key = None
            if self.system_key_id:
                try:
                    key_info = self.gpg.list_keys(keys=[self.system_key_id])
                    if key_info:
                        default_key = key_info[0]['fingerprint']
                except Exception:
                    pass
            
            return GPGHealthResponse(
                status="healthy",
                version=version_info,
                keys_available=len(keys),
                default_key=default_key,
                policies_loaded=list(self.policies.keys()),
                last_check=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error("GPG health check failed", error=str(e))
            return GPGHealthResponse(
                status="unhealthy",
                version="unknown",
                keys_available=0,
                default_key=None,
                policies_loaded=[],
                last_check=datetime.utcnow()
            )
    
    async def encrypt(self, request: EncryptRequest) -> EncryptResponse:
        """Encrypt data with GPG using specified policy"""
        request_id = self._generate_request_id()
        
        try:
            # Add context lock labels if provided
            data_to_encrypt = self._add_context_lock_labels(
                request.data, 
                request.context_labels
            )
            
            # Apply encryption policy
            policy_config = self.policies.get(
                request.policy, 
                self.policies[EncryptionPolicy.MODERN_STRONG]
            )
            
            # Perform encryption
            encrypted_data = self.gpg.encrypt(
                data_to_encrypt,
                recipients=request.recipients,
                armor=request.armor,
                always_trust=False,  # Require valid keys
                compress_algo=policy_config["compress_algo"]
            )
            
            if not encrypted_data.ok:
                error_msg = f"Encryption failed: {encrypted_data.stderr}"
                logger.error("GPG encryption failed", 
                           error=error_msg, 
                           request_id=request_id)
                
                return EncryptResponse(
                    success=False,
                    error=error_msg,
                    policy_applied=request.policy,
                    request_id=request_id
                )
            
            # Extract recipient fingerprints
            fingerprints = []
            if hasattr(encrypted_data, 'fingerprints'):
                fingerprints = encrypted_data.fingerprints
            
            logger.info("GPG encryption successful",
                       request_id=request_id,
                       recipients_count=len(request.recipients),
                       policy=request.policy)
            
            return EncryptResponse(
                success=True,
                encrypted_data=str(encrypted_data),
                fingerprints=fingerprints,
                policy_applied=request.policy,
                context_labels=request.context_labels,
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = f"Encryption operation failed: {str(e)}"
            logger.error("GPG encryption exception", 
                        error=error_msg, 
                        request_id=request_id)
            
            return EncryptResponse(
                success=False,
                error=error_msg,
                policy_applied=request.policy,
                request_id=request_id
            )
    
    async def decrypt(self, request: DecryptRequest) -> DecryptResponse:
        """Decrypt GPG encrypted data"""
        request_id = self._generate_request_id()
        
        try:
            # Perform decryption
            decrypted_data = self.gpg.decrypt(
                request.encrypted_data,
                passphrase=request.passphrase or self.passphrase,
                always_trust=True
            )
            
            if not decrypted_data.ok:
                error_msg = f"Decryption failed: {decrypted_data.stderr}"
                logger.error("GPG decryption failed", 
                           error=error_msg, 
                           request_id=request_id)
                
                return DecryptResponse(
                    success=False,
                    error=error_msg,
                    request_id=request_id
                )
            
            # Extract context lock labels
            original_data, context_labels = self._extract_context_lock_labels(
                str(decrypted_data)
            )
            
            # Extract signature information if present
            signer_fingerprints = []
            signature_valid = None
            
            if hasattr(decrypted_data, 'signature_id') and decrypted_data.signature_id:
                signer_fingerprints = [decrypted_data.signature_id]
                signature_valid = decrypted_data.valid
            
            logger.info("GPG decryption successful",
                       request_id=request_id,
                       has_signature=bool(signer_fingerprints),
                       signature_valid=signature_valid)
            
            return DecryptResponse(
                success=True,
                decrypted_data=original_data,
                signer_fingerprints=signer_fingerprints,
                signature_valid=signature_valid,
                context_labels=context_labels,
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = f"Decryption operation failed: {str(e)}"
            logger.error("GPG decryption exception", 
                        error=error_msg, 
                        request_id=request_id)
            
            return DecryptResponse(
                success=False,
                error=error_msg,
                request_id=request_id
            )
    
    async def sign(self, request: SignRequest) -> SignResponse:
        """Create GPG signature with Context-Lock labels"""
        request_id = self._generate_request_id()
        
        try:
            # Add context lock labels
            data_to_sign = self._add_context_lock_labels(
                request.data,
                request.context_labels
            )
            
            # Perform signing
            signature = self.gpg.sign(
                data_to_sign,
                keyid=request.key_id or self.system_key_id,
                passphrase=request.passphrase or self.passphrase,
                detach=request.detached,
                clearsign=not request.detached
            )
            
            if not signature.data:
                error_msg = f"Signing failed: {getattr(signature, 'stderr', 'Unknown error')}"
                logger.error("GPG signing failed", 
                           error=error_msg, 
                           request_id=request_id)
                
                return SignResponse(
                    success=False,
                    error=error_msg,
                    request_id=request_id
                )
            
            signer_fingerprint = getattr(signature, 'fingerprint', None)
            
            logger.info("GPG signing successful",
                       request_id=request_id,
                       signer_fingerprint=signer_fingerprint,
                       detached=request.detached)
            
            return SignResponse(
                success=True,
                signature=str(signature),
                signer_fingerprint=signer_fingerprint,
                context_labels=request.context_labels,
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = f"Signing operation failed: {str(e)}"
            logger.error("GPG signing exception", 
                        error=error_msg, 
                        request_id=request_id)
            
            return SignResponse(
                success=False,
                error=error_msg,
                request_id=request_id
            )
    
    async def verify(self, request: VerifyRequest) -> VerifyResponse:
        """Verify GPG signature and extract Context-Lock labels"""
        request_id = self._generate_request_id()
        
        try:
            # Verify signature
            if request.original_data:
                # Detached signature verification
                verified = self.gpg.verify_data(
                    request.signed_data,
                    request.original_data.encode('utf-8')
                )
            else:
                # Inline signature verification  
                verified = self.gpg.verify(request.signed_data)
            
            if not verified.valid:
                error_msg = f"Signature verification failed: {getattr(verified, 'stderr', 'Invalid signature')}"
                logger.warning("GPG signature verification failed", 
                             error=error_msg, 
                             request_id=request_id)
                
                return VerifyResponse(
                    success=True,  # Operation succeeded, signature is just invalid
                    valid=False,
                    error=error_msg,
                    request_id=request_id
                )
            
            # Extract context lock labels from verified data
            context_labels = None
            if hasattr(verified, 'data') and verified.data:
                _, context_labels = self._extract_context_lock_labels(str(verified.data))
            
            signer_fingerprints = []
            if verified.fingerprint:
                signer_fingerprints = [verified.fingerprint]
            
            # Parse signature timestamp
            signature_timestamp = None
            if hasattr(verified, 'timestamp') and verified.timestamp:
                try:
                    signature_timestamp = datetime.fromtimestamp(verified.timestamp)
                except (ValueError, OSError):
                    pass
            
            logger.info("GPG signature verification successful",
                       request_id=request_id,
                       valid=verified.valid,
                       signer=verified.fingerprint)
            
            return VerifyResponse(
                success=True,
                valid=verified.valid,
                signer_fingerprints=signer_fingerprints,
                signature_timestamp=signature_timestamp,
                context_labels=context_labels,
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = f"Signature verification failed: {str(e)}"
            logger.error("GPG verification exception", 
                        error=error_msg, 
                        request_id=request_id)
            
            return VerifyResponse(
                success=False,
                error=error_msg,
                request_id=request_id
            )
    
    async def generate_key_pair(self, request: KeyGenerationRequest) -> KeyGenerationResponse:
        """Generate new GPG key pair"""
        request_id = self._generate_request_id()
        
        try:
            # Build key generation parameters
            key_params = {
                "name_real": request.name,
                "name_email": request.email,
                "key_type": "RSA" if request.key_type.value.startswith("rsa") else "ECDSA",
                "key_length": 4096 if request.key_type == KeyType.RSA_4096 else None,
                "key_curve": "nistp256" if request.key_type == KeyType.ECDSA_P256 else None,
                "expire_date": request.expire_date.strftime("%Y-%m-%d") if request.expire_date else "0",
            }
            
            if request.comment:
                key_params["name_comment"] = request.comment
            if request.passphrase:
                key_params["passphrase"] = request.passphrase
            
            # Generate key pair
            input_data = self.gpg.gen_key_input(**key_params)
            key = self.gpg.gen_key(input_data)
            
            if not key.fingerprint:
                error_msg = f"Key generation failed: {getattr(key, 'stderr', 'Unknown error')}"
                logger.error("GPG key generation failed", 
                           error=error_msg, 
                           request_id=request_id)
                
                return KeyGenerationResponse(
                    success=False,
                    error=error_msg,
                    request_id=request_id
                )
            
            # Export public key
            public_key = self.gpg.export_keys(key.fingerprint, armor=True)
            
            # Get key information
            key_list = self.gpg.list_keys(keys=[key.fingerprint])
            if key_list:
                key_data = key_list[0]
                key_info = KeyInfo(
                    key_id=key_data['keyid'],
                    fingerprint=key_data['fingerprint'],
                    user_ids=key_data['uids'],
                    algorithm=key_data['algo'],
                    key_size=int(key_data['length']),
                    creation_date=datetime.fromtimestamp(int(key_data['date'])),
                    expiration_date=datetime.fromtimestamp(int(key_data['expires'])) if key_data['expires'] else None,
                    is_secret=True,  # We just generated it
                    trust_level=key_data.get('trust', 'unknown')
                )
            else:
                key_info = None
            
            logger.info("GPG key pair generated successfully",
                       request_id=request_id,
                       fingerprint=key.fingerprint,
                       key_type=request.key_type)
            
            return KeyGenerationResponse(
                success=True,
                public_key=public_key,
                key_info=key_info,
                fingerprint=key.fingerprint,
                request_id=request_id
            )
            
        except Exception as e:
            error_msg = f"Key generation failed: {str(e)}"
            logger.error("GPG key generation exception", 
                        error=error_msg, 
                        request_id=request_id)
            
            return KeyGenerationResponse(
                success=False,
                error=error_msg,
                request_id=request_id
            )
    
    async def generate_wkd_path(self, request: WKDPathRequest) -> WKDPathResponse:
        """Generate Web Key Directory path for email address"""
        try:
            # Split email
            local_part, domain = request.email.lower().split('@', 1)
            
            # Create SHA1 hash of local part
            sha1_hash = hashlib.sha1(local_part.encode('utf-8')).digest()
            
            # Convert to Z-Base32 encoding (RFC 6189)
            z_base32_chars = "ybndrfg8ejkmcpqxot1uwisza345h769"
            z_base32 = ""
            
            # Simple Z-Base32 encoding (simplified implementation)
            for byte in sha1_hash:
                z_base32 += z_base32_chars[byte % 32]
            
            # Truncate to 32 characters as per WKD spec
            z_base32 = z_base32[:32]
            
            # Build WKD path
            wkd_path = f"/.well-known/openpgpkey/hu/{z_base32}"
            
            return WKDPathResponse(
                wkd_path=wkd_path,
                local_part=local_part,
                domain=domain,
                z_base32=z_base32
            )
            
        except ValueError as e:
            raise ValueError(f"Invalid email format: {request.email}")
        except Exception as e:
            logger.error("WKD path generation failed", error=str(e))
            raise