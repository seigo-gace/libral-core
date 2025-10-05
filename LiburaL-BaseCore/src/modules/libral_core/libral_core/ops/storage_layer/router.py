"""
ストレージルーター
SAL_OPS_002実装: セキュリティレベルに応じた動的ルーティング
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import structlog
from .provider import StorageProvider, StorageProviderType, StorageSecurityLevel


logger = structlog.get_logger(__name__)


@dataclass
class RoutingPolicy:
    """ルーティングポリシー"""
    security_level: StorageSecurityLevel
    primary_provider: StorageProviderType
    fallback_providers: List[StorageProviderType]
    encryption_required: bool = True
    compression_enabled: bool = False


class StorageRouter:
    """ストレージルーター"""
    
    def __init__(self):
        self.policies: Dict[StorageSecurityLevel, RoutingPolicy] = {}
        self._configure_default_policies()
    
    def _configure_default_policies(self):
        """デフォルトポリシー設定"""
        self.policies = {
            StorageSecurityLevel.PUBLIC: RoutingPolicy(
                security_level=StorageSecurityLevel.PUBLIC,
                primary_provider=StorageProviderType.S3,
                fallback_providers=[StorageProviderType.LOB],
                encryption_required=False,
                compression_enabled=True
            ),
            StorageSecurityLevel.STANDARD: RoutingPolicy(
                security_level=StorageSecurityLevel.STANDARD,
                primary_provider=StorageProviderType.S3,
                fallback_providers=[StorageProviderType.LOB, StorageProviderType.LOCAL],
                encryption_required=True,
                compression_enabled=True
            ),
            StorageSecurityLevel.CONFIDENTIAL: RoutingPolicy(
                security_level=StorageSecurityLevel.CONFIDENTIAL,
                primary_provider=StorageProviderType.TELEGRAM,
                fallback_providers=[StorageProviderType.LOB],
                encryption_required=True,
                compression_enabled=False
            ),
            StorageSecurityLevel.SECRET: RoutingPolicy(
                security_level=StorageSecurityLevel.SECRET,
                primary_provider=StorageProviderType.TELEGRAM,
                fallback_providers=[],
                encryption_required=True,
                compression_enabled=False
            ),
        }
        
        logger.info("storage_routing_policies_configured", policies=len(self.policies))
    
    def update_policy(self, policy: RoutingPolicy):
        """ポリシー更新（K8s ConfigMapから）"""
        self.policies[policy.security_level] = policy
        logger.info(
            "storage_policy_updated",
            security_level=policy.security_level.value,
            primary_provider=policy.primary_provider.value
        )
    
    def get_policy(self, security_level: StorageSecurityLevel) -> Optional[RoutingPolicy]:
        """ポリシー取得"""
        return self.policies.get(security_level)
    
    def select_provider(
        self,
        security_level: StorageSecurityLevel,
        available_providers: List[StorageProvider]
    ) -> Optional[StorageProvider]:
        """プロバイダ選択"""
        policy = self.get_policy(security_level)
        if not policy:
            logger.error(
                "no_routing_policy",
                security_level=security_level.value
            )
            return None
        
        # プライマリプロバイダを優先
        for provider in available_providers:
            if (provider.provider_type == policy.primary_provider and
                provider.enabled):
                logger.info(
                    "provider_selected",
                    security_level=security_level.value,
                    provider=provider.provider_type.value,
                    type="primary"
                )
                return provider
        
        # フォールバックプロバイダを試行
        for fallback_type in policy.fallback_providers:
            for provider in available_providers:
                if (provider.provider_type == fallback_type and
                    provider.enabled):
                    logger.warning(
                        "provider_selected",
                        security_level=security_level.value,
                        provider=provider.provider_type.value,
                        type="fallback"
                    )
                    return provider
        
        logger.error(
            "no_available_provider",
            security_level=security_level.value,
            policy=policy
        )
        return None
    
    def should_encrypt(self, security_level: StorageSecurityLevel) -> bool:
        """暗号化必要性"""
        policy = self.get_policy(security_level)
        return policy.encryption_required if policy else True
    
    def should_compress(self, security_level: StorageSecurityLevel) -> bool:
        """圧縮有効性"""
        policy = self.get_policy(security_level)
        return policy.compression_enabled if policy else False
