"""
鍵管理システム (KMS) マネージャー
CCA_OPS_003実装: HSM/クラウドKMS統合とRBACポリシー
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import structlog


logger = structlog.get_logger(__name__)


class KMSProvider(str, Enum):
    """KMSプロバイダ"""
    AWS_KMS = "aws_kms"
    AZURE_KEY_VAULT = "azure_key_vault"
    GCP_KMS = "gcp_kms"
    HSM = "hsm"
    LOCAL = "local"  # 開発用


class KeyType(str, Enum):
    """鍵タイプ"""
    CONTEXT_LOCK = "context_lock"
    DATA_ENCRYPTION = "data_encryption"
    SIGNING = "signing"
    MASTER_KEY = "master_key"


class KeyStatus(str, Enum):
    """鍵ステータス"""
    ACTIVE = "active"
    ROTATING = "rotating"
    DEPRECATED = "deprecated"
    REVOKED = "revoked"


@dataclass
class KeyMetadata:
    """鍵メタデータ"""
    key_id: str
    key_type: KeyType
    kms_provider: KMSProvider
    created_at: datetime
    last_rotated: Optional[datetime]
    status: KeyStatus
    allowed_services: Set[str]
    allowed_operations: Set[str]
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """辞書変換"""
        return {
            "key_id": self.key_id,
            "key_type": self.key_type.value,
            "kms_provider": self.kms_provider.value,
            "created_at": self.created_at.isoformat(),
            "last_rotated": self.last_rotated.isoformat() if self.last_rotated else None,
            "status": self.status.value,
            "allowed_services": list(self.allowed_services),
            "allowed_operations": list(self.allowed_operations),
            "metadata": self.metadata
        }


class KMSManager:
    """KMSマネージャー"""
    
    def __init__(self, default_provider: KMSProvider = KMSProvider.LOCAL):
        self.default_provider = default_provider
        self.keys: Dict[str, KeyMetadata] = {}
        self.rbac_policies: Dict[str, Dict] = {}
        self._initialize_default_keys()
        logger.info(
            "kms_manager_initialized",
            provider=default_provider.value
        )
    
    def _initialize_default_keys(self):
        """デフォルト鍵初期化"""
        now = datetime.utcnow()
        
        # Context-Lock マスターキー
        self.register_key(KeyMetadata(
            key_id="context_lock_master_001",
            key_type=KeyType.CONTEXT_LOCK,
            kms_provider=self.default_provider,
            created_at=now,
            last_rotated=now,
            status=KeyStatus.ACTIVE,
            allowed_services={"gpg_module", "context_lock_service"},
            allowed_operations={"sign", "verify"},
            metadata={
                "algorithm": "Ed25519",
                "purpose": "Context-Lock signature generation"
            }
        ))
        
        # データ暗号化キー
        self.register_key(KeyMetadata(
            key_id="data_encryption_master_001",
            key_type=KeyType.DATA_ENCRYPTION,
            kms_provider=self.default_provider,
            created_at=now,
            last_rotated=now,
            status=KeyStatus.ACTIVE,
            allowed_services={"storage_layer", "api_hub"},
            allowed_operations={"encrypt", "decrypt"},
            metadata={
                "algorithm": "AES-256-OCB",
                "purpose": "User data encryption"
            }
        ))
        
        # 署名キー
        self.register_key(KeyMetadata(
            key_id="signing_key_001",
            key_type=KeyType.SIGNING,
            kms_provider=self.default_provider,
            created_at=now,
            last_rotated=now,
            status=KeyStatus.ACTIVE,
            allowed_services={"auth_module", "api_hub"},
            allowed_operations={"sign", "verify"},
            metadata={
                "algorithm": "Ed25519",
                "purpose": "API request signing"
            }
        ))
    
    def register_key(self, key_metadata: KeyMetadata):
        """鍵登録"""
        self.keys[key_metadata.key_id] = key_metadata
        logger.info(
            "key_registered",
            key_id=key_metadata.key_id,
            key_type=key_metadata.key_type.value,
            provider=key_metadata.kms_provider.value
        )
    
    def get_key(self, key_id: str) -> Optional[KeyMetadata]:
        """鍵取得"""
        return self.keys.get(key_id)
    
    def check_access(
        self,
        key_id: str,
        service_name: str,
        operation: str
    ) -> bool:
        """アクセスチェック（RBAC）"""
        key = self.get_key(key_id)
        if not key:
            logger.warning("key_not_found", key_id=key_id)
            return False
        
        if key.status != KeyStatus.ACTIVE:
            logger.warning(
                "key_not_active",
                key_id=key_id,
                status=key.status.value
            )
            return False
        
        if service_name not in key.allowed_services:
            logger.warning(
                "service_not_allowed",
                key_id=key_id,
                service=service_name,
                allowed=list(key.allowed_services)
            )
            return False
        
        if operation not in key.allowed_operations:
            logger.warning(
                "operation_not_allowed",
                key_id=key_id,
                operation=operation,
                allowed=list(key.allowed_operations)
            )
            return False
        
        logger.info(
            "access_granted",
            key_id=key_id,
            service=service_name,
            operation=operation
        )
        return True
    
    async def rotate_key(self, key_id: str) -> bool:
        """鍵ローテーション"""
        key = self.get_key(key_id)
        if not key:
            return False
        
        key.status = KeyStatus.ROTATING
        key.last_rotated = datetime.utcnow()
        
        logger.info(
            "key_rotation_started",
            key_id=key_id,
            key_type=key.key_type.value
        )
        
        # ローテーション処理（実装例）
        # 実際のKMSプロバイダAPIを呼び出す
        
        key.status = KeyStatus.ACTIVE
        
        logger.info(
            "key_rotation_completed",
            key_id=key_id,
            rotated_at=key.last_rotated.isoformat()
        )
        
        return True
    
    def revoke_key(self, key_id: str):
        """鍵失効"""
        key = self.get_key(key_id)
        if key:
            key.status = KeyStatus.REVOKED
            logger.warning(
                "key_revoked",
                key_id=key_id,
                key_type=key.key_type.value
            )
    
    def set_rbac_policy(
        self,
        key_id: str,
        allowed_services: Set[str],
        allowed_operations: Set[str]
    ):
        """RBACポリシー設定"""
        key = self.get_key(key_id)
        if key:
            key.allowed_services = allowed_services
            key.allowed_operations = allowed_operations
            logger.info(
                "rbac_policy_updated",
                key_id=key_id,
                services=list(allowed_services),
                operations=list(allowed_operations)
            )
    
    def get_keys_by_type(self, key_type: KeyType) -> List[KeyMetadata]:
        """タイプ別鍵取得"""
        return [k for k in self.keys.values() if k.key_type == key_type]
    
    def get_active_keys(self) -> List[KeyMetadata]:
        """アクティブ鍵取得"""
        return [k for k in self.keys.values() if k.status == KeyStatus.ACTIVE]
    
    def get_kms_summary(self) -> Dict:
        """KMSサマリー"""
        return {
            "total_keys": len(self.keys),
            "active_keys": len(self.get_active_keys()),
            "keys_by_type": {
                key_type.value: len(self.get_keys_by_type(key_type))
                for key_type in KeyType
            },
            "keys_by_provider": {
                provider.value: len([
                    k for k in self.keys.values()
                    if k.kms_provider == provider
                ])
                for provider in KMSProvider
            },
            "keys": [k.to_dict() for k in self.keys.values()]
        }
