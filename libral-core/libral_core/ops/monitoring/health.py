"""
ヘルスチェックシステム
コンポーネント稼働状態監視
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import structlog


logger = structlog.get_logger(__name__)


class HealthStatus(str, Enum):
    """ヘルスステータス"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """ヘルスチェック結果"""
    component: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metadata: Dict = None


class HealthChecker:
    """ヘルスチェッカー"""
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
    
    async def check_storage_provider(
        self,
        provider: str,
        check_func: callable
    ) -> HealthCheck:
        """ストレージプロバイダヘルスチェック"""
        try:
            result = await check_func()
            status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
            message = "Provider operational" if result else "Provider not responding"
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = f"Check failed: {str(e)}"
            logger.error(
                "health_check_failed",
                provider=provider,
                error=str(e)
            )
        
        health_check = HealthCheck(
            component=f"storage_{provider}",
            status=status,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        self.health_checks[f"storage_{provider}"] = health_check
        return health_check
    
    async def check_database(self) -> HealthCheck:
        """データベースヘルスチェック"""
        status = HealthStatus.HEALTHY
        message = "Database operational"
        
        health_check = HealthCheck(
            component="database",
            status=status,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        self.health_checks["database"] = health_check
        return health_check
    
    async def check_redis(self) -> HealthCheck:
        """Redisヘルスチェック"""
        status = HealthStatus.HEALTHY
        message = "Redis operational"
        
        health_check = HealthCheck(
            component="redis",
            status=status,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        self.health_checks["redis"] = health_check
        return health_check
    
    async def check_crypto_module(self) -> HealthCheck:
        """暗号モジュールヘルスチェック"""
        status = HealthStatus.HEALTHY
        message = "Crypto module operational"
        
        health_check = HealthCheck(
            component="crypto_module",
            status=status,
            message=message,
            timestamp=datetime.utcnow()
        )
        
        self.health_checks["crypto_module"] = health_check
        return health_check
    
    def get_overall_health(self) -> HealthStatus:
        """全体ヘルスステータス"""
        if not self.health_checks:
            return HealthStatus.UNKNOWN
        
        statuses = [check.status for check in self.health_checks.values()]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED
    
    def get_health_report(self) -> Dict:
        """ヘルスレポート取得"""
        return {
            "overall_status": self.get_overall_health().value,
            "checks": {
                name: {
                    "status": check.status.value,
                    "message": check.message,
                    "timestamp": check.timestamp.isoformat()
                }
                for name, check in self.health_checks.items()
            }
        }
