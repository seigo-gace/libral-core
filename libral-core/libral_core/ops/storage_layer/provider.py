"""
ストレージプロバイダインターフェース
SAL_OPS_001実装: 各プロバイダの統一インターフェース
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass
import structlog


logger = structlog.get_logger(__name__)


class StorageProviderType(str, Enum):
    """ストレージプロバイダタイプ"""
    TELEGRAM = "telegram"
    S3 = "s3"
    LOB = "lob"  # Libral Object storage Backend
    LOCAL = "local"


class StorageSecurityLevel(str, Enum):
    """セキュリティレベル"""
    PUBLIC = "public"
    STANDARD = "standard"
    CONFIDENTIAL = "confidential"
    SECRET = "secret"


@dataclass
class StorageMetrics:
    """ストレージメトリクス"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_latency_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_operations == 0:
            return 1.0
        return self.successful_operations / self.total_operations
    
    @property
    def average_latency_ms(self) -> float:
        """平均レイテンシ"""
        if self.total_operations == 0:
            return 0.0
        return self.total_latency_ms / self.total_operations
    
    @property
    def error_rate(self) -> float:
        """エラーレート"""
        return 1.0 - self.success_rate


class IStorageProvider(ABC):
    """ストレージプロバイダインターフェース"""
    
    @abstractmethod
    async def store(self, key: str, data: bytes, metadata: Optional[Dict] = None) -> bool:
        """データ保存"""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[bytes]:
        """データ取得"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """データ削除"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """存在確認"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """ヘルスチェック"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> StorageMetrics:
        """メトリクス取得"""
        pass


class StorageProvider:
    """ストレージプロバイダ実装"""
    
    def __init__(
        self,
        provider_type: StorageProviderType,
        config: Dict[str, Any],
        priority: int = 100
    ):
        self.provider_type = provider_type
        self.config = config
        self.priority = priority
        self.metrics = StorageMetrics()
        self.enabled = True
        logger.info(
            "storage_provider_initialized",
            provider_type=provider_type.value,
            priority=priority
        )
    
    async def store(self, key: str, data: bytes, metadata: Optional[Dict] = None) -> bool:
        """データ保存"""
        self.metrics.total_operations += 1
        try:
            logger.info(
                "storage_store",
                provider=self.provider_type.value,
                key=key,
                size=len(data)
            )
            self.metrics.successful_operations += 1
            return True
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(
                "storage_store_failed",
                provider=self.provider_type.value,
                key=key,
                error=str(e)
            )
            return False
    
    async def retrieve(self, key: str) -> Optional[bytes]:
        """データ取得"""
        self.metrics.total_operations += 1
        try:
            logger.info(
                "storage_retrieve",
                provider=self.provider_type.value,
                key=key
            )
            self.metrics.successful_operations += 1
            return b"mock_data"
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(
                "storage_retrieve_failed",
                provider=self.provider_type.value,
                key=key,
                error=str(e)
            )
            return None
    
    async def delete(self, key: str) -> bool:
        """データ削除"""
        self.metrics.total_operations += 1
        try:
            logger.info(
                "storage_delete",
                provider=self.provider_type.value,
                key=key
            )
            self.metrics.successful_operations += 1
            return True
        except Exception as e:
            self.metrics.failed_operations += 1
            logger.error(
                "storage_delete_failed",
                provider=self.provider_type.value,
                key=key,
                error=str(e)
            )
            return False
    
    async def exists(self, key: str) -> bool:
        """存在確認"""
        return True
    
    async def health_check(self) -> bool:
        """ヘルスチェック"""
        return self.enabled
    
    def get_metrics(self) -> StorageMetrics:
        """メトリクス取得"""
        return self.metrics
    
    def disable(self):
        """プロバイダ無効化"""
        self.enabled = False
        logger.warning(
            "storage_provider_disabled",
            provider=self.provider_type.value
        )
    
    def enable(self):
        """プロバイダ有効化"""
        self.enabled = True
        logger.info(
            "storage_provider_enabled",
            provider=self.provider_type.value
        )
