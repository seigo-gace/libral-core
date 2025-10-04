"""
Storage Abstraction Layer Manager
SAL統合管理
"""

from typing import Dict, List, Optional
from .provider import StorageProvider, StorageProviderType, StorageSecurityLevel
from .router import StorageRouter
from .audit import StorageAuditLogger
from ..monitoring.metrics import metrics_registry
from ..monitoring.alerting import AlertManager, AlertSeverity
import structlog
import asyncio


logger = structlog.get_logger(__name__)


class StorageAbstractionLayer:
    """ストレージ抽象化レイヤー"""
    
    def __init__(self):
        self.providers: Dict[StorageProviderType, StorageProvider] = {}
        self.router = StorageRouter()
        self.audit_logger = StorageAuditLogger()
        self.alert_manager = AlertManager()
        self._initialize_providers()
        logger.info("storage_abstraction_layer_initialized")
    
    def _initialize_providers(self):
        """プロバイダ初期化"""
        self.providers = {
            StorageProviderType.TELEGRAM: StorageProvider(
                StorageProviderType.TELEGRAM,
                {"api_token": "mock"},
                priority=100
            ),
            StorageProviderType.S3: StorageProvider(
                StorageProviderType.S3,
                {"bucket": "libral-storage"},
                priority=90
            ),
            StorageProviderType.LOB: StorageProvider(
                StorageProviderType.LOB,
                {"endpoint": "localhost:9000"},
                priority=80
            ),
            StorageProviderType.LOCAL: StorageProvider(
                StorageProviderType.LOCAL,
                {"path": "/var/lib/libral/storage"},
                priority=70
            ),
        }
    
    @metrics_registry.track_storage_operation("sal", "store")
    async def store(
        self,
        key: str,
        data: bytes,
        security_level: StorageSecurityLevel = StorageSecurityLevel.STANDARD,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """データ保存"""
        provider = self.router.select_provider(
            security_level,
            list(self.providers.values())
        )
        
        if not provider:
            logger.error("no_provider_available", security_level=security_level.value)
            return False
        
        # 暗号化処理（必要な場合）
        if self.router.should_encrypt(security_level):
            await self.audit_logger.log_encryption_event(
                "encrypt", key, "AES-256-OCB", True, user_id
            )
        
        # ストレージ操作
        success = await provider.store(key, data, metadata)
        
        # 監査ログ記録
        await self.audit_logger.log_access_attempt(
            key, "store", provider.provider_type.value, success, user_id
        )
        
        # メトリクス更新
        if success:
            metrics = provider.get_metrics()
            metrics_registry.update_success_rate(
                provider.provider_type.value,
                metrics.success_rate
            )
        
        # エラーレート監視
        await self._check_error_threshold(provider)
        
        return success
    
    @metrics_registry.track_storage_operation("sal", "retrieve")
    async def retrieve(
        self,
        key: str,
        security_level: StorageSecurityLevel = StorageSecurityLevel.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[bytes]:
        """データ取得"""
        provider = self.router.select_provider(
            security_level,
            list(self.providers.values())
        )
        
        if not provider:
            logger.error("no_provider_available", security_level=security_level.value)
            return None
        
        # ストレージ操作
        data = await provider.retrieve(key)
        
        # 監査ログ記録
        await self.audit_logger.log_access_attempt(
            key, "retrieve", provider.provider_type.value, data is not None, user_id
        )
        
        # 復号化処理（必要な場合）
        if data and self.router.should_encrypt(security_level):
            await self.audit_logger.log_encryption_event(
                "decrypt", key, "AES-256-OCB", True, user_id
            )
        
        return data
    
    async def failover_to_backup(
        self,
        original_provider: StorageProvider,
        security_level: StorageSecurityLevel,
        reason: str
    ) -> Optional[StorageProvider]:
        """バックアッププロバイダへフェイルオーバー"""
        original_provider.disable()
        
        backup_provider = self.router.select_provider(
            security_level,
            list(self.providers.values())
        )
        
        if not backup_provider:
            logger.error("failover_failed_no_backup")
            await self.alert_manager.send_alert(
                title="Storage Failover Failed",
                description=f"No backup provider available for {original_provider.provider_type.value}",
                severity=AlertSeverity.CRITICAL,
                component="storage_layer"
            )
            return None
        
        # フェイルオーバーイベント記録
        await self.audit_logger.log_failover(
            original_provider.provider_type.value,
            backup_provider.provider_type.value,
            reason,
            True
        )
        
        # メトリクス記録
        metrics_registry.record_failover(
            original_provider.provider_type.value,
            backup_provider.provider_type.value
        )
        
        # アラート送信
        await self.alert_manager.send_storage_failover_alert(
            original_provider.provider_type.value,
            backup_provider.provider_type.value,
            reason
        )
        
        logger.info(
            "storage_failover_completed",
            from_provider=original_provider.provider_type.value,
            to_provider=backup_provider.provider_type.value
        )
        
        return backup_provider
    
    async def _check_error_threshold(self, provider: StorageProvider):
        """エラーレート閾値チェック"""
        metrics = provider.get_metrics()
        
        # エラーレートが0.5%以上の場合アラート
        if metrics.error_rate >= 0.005:
            await self.alert_manager.send_alert(
                title="High Storage Error Rate",
                description=f"Provider {provider.provider_type.value} error rate: {metrics.error_rate*100:.2f}%",
                severity=AlertSeverity.ERROR,
                component="storage_layer",
                metadata={
                    "provider": provider.provider_type.value,
                    "error_rate": metrics.error_rate,
                    "threshold": 0.005
                }
            )
    
    async def health_check_all(self) -> Dict[str, bool]:
        """全プロバイダヘルスチェック"""
        results = {}
        for provider_type, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                results[provider_type.value] = is_healthy
            except Exception as e:
                logger.error(
                    "health_check_failed",
                    provider=provider_type.value,
                    error=str(e)
                )
                results[provider_type.value] = False
        
        return results
    
    def get_metrics_summary(self) -> Dict:
        """メトリクスサマリー取得"""
        summary = {}
        for provider_type, provider in self.providers.items():
            metrics = provider.get_metrics()
            summary[provider_type.value] = {
                "total_operations": metrics.total_operations,
                "success_rate": metrics.success_rate,
                "error_rate": metrics.error_rate,
                "average_latency_ms": metrics.average_latency_ms,
                "enabled": provider.enabled
            }
        
        return summary
    
    def get_audit_summary(self) -> Dict:
        """監査サマリー取得"""
        return self.audit_logger.get_summary()
