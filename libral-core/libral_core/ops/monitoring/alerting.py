"""
アラート管理システム
SAL_OPS_001, SAL_OPS_003実装: エラーレート閾値監視とアラート送信
"""

from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import structlog
import asyncio
from enum import Enum


logger = structlog.get_logger(__name__)


class AlertSeverity(str, Enum):
    """アラート重大度"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """アラート通知チャネル"""
    SLACK = "slack"
    PAGERDUTY = "pagerduty"
    EMAIL = "email"
    TELEGRAM = "telegram"


@dataclass
class Alert:
    """アラート"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    component: str
    timestamp: datetime
    metadata: Dict = None


@dataclass
class AlertThreshold:
    """アラート閾値"""
    metric_name: str
    threshold_value: float
    comparison: str  # ">", "<", ">=", "<=", "=="
    window_seconds: int
    severity: AlertSeverity


class AlertManager:
    """アラート管理"""
    
    def __init__(self):
        self.thresholds: Dict[str, AlertThreshold] = {}
        self.alert_handlers: Dict[AlertChannel, Callable] = {}
        self.alert_history: List[Alert] = []
        self._configure_default_thresholds()
    
    def _configure_default_thresholds(self):
        """デフォルト閾値設定"""
        self.thresholds = {
            "storage_error_rate": AlertThreshold(
                metric_name="storage_provider_errors_total",
                threshold_value=0.005,  # 0.5%
                comparison=">=",
                window_seconds=300,  # 5分
                severity=AlertSeverity.ERROR
            ),
            "storage_latency_p99": AlertThreshold(
                metric_name="storage_provider_latency_seconds",
                threshold_value=5.0,  # 5秒
                comparison=">=",
                window_seconds=300,
                severity=AlertSeverity.WARNING
            ),
            "certificate_expiry": AlertThreshold(
                metric_name="certificate_expiry_days",
                threshold_value=30,  # 30日
                comparison="<=",
                window_seconds=3600,  # 1時間
                severity=AlertSeverity.WARNING
            ),
            "crypto_validation_failures": AlertThreshold(
                metric_name="crypto_validation_errors_total",
                threshold_value=5,
                comparison=">=",
                window_seconds=300,
                severity=AlertSeverity.CRITICAL
            ),
            "system_recovery_time": AlertThreshold(
                metric_name="system_recovery_time_seconds",
                threshold_value=180,  # 3分
                comparison=">=",
                window_seconds=60,
                severity=AlertSeverity.ERROR
            ),
        }
    
    def register_handler(self, channel: AlertChannel, handler: Callable):
        """アラートハンドラ登録"""
        self.alert_handlers[channel] = handler
        logger.info("alert_handler_registered", channel=channel)
    
    async def send_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        component: str,
        channels: Optional[List[AlertChannel]] = None,
        metadata: Optional[Dict] = None
    ):
        """アラート送信"""
        alert = Alert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            severity=severity,
            component=component,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        self.alert_history.append(alert)
        
        target_channels = channels or [
            AlertChannel.SLACK,
            AlertChannel.TELEGRAM
        ]
        
        logger.warning(
            "alert_triggered",
            alert_id=alert.alert_id,
            title=title,
            severity=severity.value,
            component=component
        )
        
        tasks = []
        for channel in target_channels:
            if channel in self.alert_handlers:
                tasks.append(
                    self._send_to_channel(channel, alert)
                )
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_to_channel(self, channel: AlertChannel, alert: Alert):
        """チャネルへのアラート送信"""
        try:
            handler = self.alert_handlers[channel]
            await handler(alert)
            logger.info(
                "alert_sent",
                channel=channel,
                alert_id=alert.alert_id
            )
        except Exception as e:
            logger.error(
                "alert_send_failed",
                channel=channel,
                alert_id=alert.alert_id,
                error=str(e)
            )
    
    async def send_storage_failover_alert(
        self,
        from_provider: str,
        to_provider: str,
        reason: str
    ):
        """ストレージフェイルオーバーアラート"""
        await self.send_alert(
            title="Storage Provider Failover",
            description=f"Switched from {from_provider} to {to_provider}. Reason: {reason}",
            severity=AlertSeverity.WARNING,
            component="storage_layer",
            metadata={
                "from_provider": from_provider,
                "to_provider": to_provider,
                "reason": reason
            }
        )
    
    async def send_crypto_validation_alert(
        self,
        module: str,
        reason: str
    ):
        """暗号検証エラーアラート"""
        await self.send_alert(
            title="Crypto Validation Failure",
            description=f"Module {module} failed validation: {reason}",
            severity=AlertSeverity.CRITICAL,
            component="crypto_module",
            channels=[AlertChannel.SLACK, AlertChannel.PAGERDUTY],
            metadata={
                "module": module,
                "reason": reason
            }
        )
    
    async def send_certificate_expiry_alert(
        self,
        cert_name: str,
        days_remaining: int
    ):
        """証明書有効期限アラート"""
        severity = AlertSeverity.CRITICAL if days_remaining <= 7 else AlertSeverity.WARNING
        
        await self.send_alert(
            title="Certificate Expiry Warning",
            description=f"Certificate '{cert_name}' expires in {days_remaining} days",
            severity=severity,
            component="certificate_manager",
            metadata={
                "certificate_name": cert_name,
                "days_remaining": days_remaining
            }
        )
    
    async def send_chaos_experiment_alert(
        self,
        experiment_type: str,
        status: str,
        recovery_time: Optional[float] = None
    ):
        """カオスエンジニアリング実験アラート"""
        description = f"Chaos experiment '{experiment_type}' {status}"
        if recovery_time:
            description += f" (Recovery time: {recovery_time:.2f}s)"
        
        severity = AlertSeverity.ERROR if recovery_time and recovery_time > 180 else AlertSeverity.INFO
        
        await self.send_alert(
            title="Chaos Engineering Experiment",
            description=description,
            severity=severity,
            component="chaos_engineering",
            metadata={
                "experiment_type": experiment_type,
                "status": status,
                "recovery_time": recovery_time
            }
        )
    
    def get_recent_alerts(self, limit: int = 100) -> List[Alert]:
        """最近のアラート取得"""
        return self.alert_history[-limit:]
