"""
LPO Core Service
単体自律監視の中核サービス
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

# Component層インポート
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, config_loader

# Governance層インポート
from governance import autonomous_moderator, context_aware_debugger


@dataclass
class LPOStatus:
    """LPOシステムステータス"""
    health_score: float
    amm_status: str
    crad_status: str
    active_alerts: int
    auto_recovery_count: int
    last_check: datetime


class LPOCore:
    """
    LPO Core Service
    
    AMM/CRADを統合し、単体自律監視を提供
    """
    
    def __init__(self):
        self.autonomous_moderator = autonomous_moderator
        self.context_aware_debugger = context_aware_debugger
        self.status = LPOStatus(
            health_score=100.0,
            amm_status="active",
            crad_status="active",
            active_alerts=0,
            auto_recovery_count=0,
            last_check=utc_now()
        )
    
    def get_status(self) -> Dict[str, Any]:
        """LPOステータス取得"""
        return {
            "lpo_version": "1.0.0",
            "health_score": self.status.health_score,
            "components": {
                "amm": {
                    "status": self.status.amm_status,
                    "policy_summary": self.autonomous_moderator.get_policy_summary()
                },
                "crad": {
                    "status": self.status.crad_status,
                    "summary": self.context_aware_debugger.get_crad_summary()
                }
            },
            "active_alerts": self.status.active_alerts,
            "auto_recovery_count": self.status.auto_recovery_count,
            "last_check": self.status.last_check.isoformat()
        }
    
    def integrate_amm_check(self, check_type: str, **kwargs) -> Dict[str, Any]:
        """
        AMM統合チェック
        
        Args:
            check_type: "kms_access" | "kubectl"
            **kwargs: チェックパラメータ
        """
        if check_type == "kms_access":
            return self.autonomous_moderator.check_kms_access(
                kwargs.get("pod_id"),
                kwargs.get("operation")
            )
        elif check_type == "kubectl":
            return self.autonomous_moderator.check_kubectl_operation(
                kwargs.get("user"),
                kwargs.get("operation"),
                kwargs.get("target")
            )
        else:
            return {"allowed": False, "reason": "Unknown check type"}
    
    async def integrate_crad_recovery(self, alert_name: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        CRAD統合リカバリ
        
        Args:
            alert_name: アラート名
            alert_data: アラートデータ
        """
        execution = await self.context_aware_debugger.handle_alert(alert_name, alert_data)
        self.status.auto_recovery_count += 1
        self.status.last_check = utc_now()
        
        return {
            "execution_id": execution.execution_id,
            "alert_name": execution.alert_name,
            "status": execution.status.value,
            "steps_executed": execution.steps_executed,
            "recovery_time_seconds": execution.recovery_time_seconds
        }
    
    def update_health_score(self, new_score: float):
        """健全性スコア更新"""
        self.status.health_score = max(0.0, min(100.0, new_score))
        self.status.last_check = utc_now()


# グローバルLPOインスタンス
lpo_core = LPOCore()
