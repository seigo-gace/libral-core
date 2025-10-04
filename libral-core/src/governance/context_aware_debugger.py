"""
Context-Aware Recovery & Auto Debugger (CRAD)
コンテキスト認識型自動リカバリ・デバッガー

Prometheusアラートに基づく自動リカバリ実行
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path
import asyncio

# Component層インポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from library.components import config_loader, utc_now, generate_random_id


class ActionType(Enum):
    """アクション種別"""
    K8S_SCALE_OUT = "K8S_SCALE_OUT"
    CHAOS_EXPERIMENT_RUN = "CHAOS_EXPERIMENT_RUN"
    HA_TRIGGER_FAILOVER = "HA_TRIGGER_FAILOVER"
    DRP_PITR_TEST = "DRP_PITR_TEST"


class RecoveryStatus(Enum):
    """リカバリステータス"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RecoveryStep:
    """リカバリステップ"""
    step_id: int
    action_type: ActionType
    target_component: str
    params: Dict[str, Any]
    condition: Optional[str] = None


@dataclass
class RecoveryProtocol:
    """リカバリプロトコル"""
    alert_name: str
    threshold: float
    severity: str
    steps: List[RecoveryStep]


@dataclass
class RecoveryExecution:
    """リカバリ実行記録"""
    execution_id: str
    alert_name: str
    started_at: str
    completed_at: Optional[str]
    status: RecoveryStatus
    steps_executed: int
    recovery_time_seconds: Optional[float]
    result: Optional[str]


class ContextAwareAutoDebugger:
    """コンテキスト認識型自動デバッガー"""
    
    def __init__(self):
        """初期化"""
        # ランブックファイル読み込み
        self.runbook = config_loader.load_policy("recovery_runbook_crad")
        self.protocols = self._parse_protocols()
        
        # MTTRターゲット
        self.mttr_target = self.runbook["mttr_target_seconds"]
        
        # 実行履歴
        self.executions: List[RecoveryExecution] = []
    
    def _parse_protocols(self) -> Dict[str, RecoveryProtocol]:
        """プロトコル解析"""
        protocols = {}
        
        for alert_data in self.runbook["alert_to_action_map"]:
            steps = []
            
            for step_data in alert_data["protocol"]:
                params = {
                    k: v for k, v in step_data.items()
                    if k not in ["step_id", "action_type", "target_component", "condition"]
                }
                
                step = RecoveryStep(
                    step_id=step_data["step_id"],
                    action_type=ActionType(step_data["action_type"]),
                    target_component=step_data["target_component"],
                    params=params,
                    condition=step_data.get("condition")
                )
                steps.append(step)
            
            protocol = RecoveryProtocol(
                alert_name=alert_data["alert_name"],
                threshold=alert_data.get("threshold_ms") or alert_data.get("threshold_seconds", 0),
                severity=alert_data["severity"],
                steps=steps
            )
            protocols[alert_data["alert_name"]] = protocol
        
        return protocols
    
    async def handle_alert(self, alert_name: str, alert_data: Dict[str, Any]) -> RecoveryExecution:
        """
        アラート処理
        
        Args:
            alert_name: アラート名
            alert_data: アラートデータ
        
        Returns:
            実行記録
        """
        if alert_name not in self.protocols:
            return RecoveryExecution(
                execution_id=generate_random_id(),
                alert_name=alert_name,
                started_at=utc_now().isoformat(),
                completed_at=None,
                status=RecoveryStatus.FAILED,
                steps_executed=0,
                recovery_time_seconds=None,
                result="対応プロトコルが見つかりません"
            )
        
        protocol = self.protocols[alert_name]
        execution_id = generate_random_id()
        started_at = utc_now()
        
        execution = RecoveryExecution(
            execution_id=execution_id,
            alert_name=alert_name,
            started_at=started_at.isoformat(),
            completed_at=None,
            status=RecoveryStatus.IN_PROGRESS,
            steps_executed=0,
            recovery_time_seconds=None,
            result=None
        )
        
        # ステップ実行
        try:
            for step in protocol.steps:
                # 条件チェック
                if step.condition and not self._check_condition(step.condition, alert_data):
                    continue
                
                # アクション実行
                await self._execute_action(step, alert_data)
                execution.steps_executed += 1
            
            completed_at = utc_now()
            recovery_time = (completed_at - started_at).total_seconds()
            
            execution.completed_at = completed_at.isoformat()
            execution.status = RecoveryStatus.COMPLETED
            execution.recovery_time_seconds = recovery_time
            execution.result = f"{execution.steps_executed}ステップ実行完了"
            
        except Exception as e:
            execution.status = RecoveryStatus.FAILED
            execution.result = f"エラー: {str(e)}"
        
        self.executions.append(execution)
        return execution
    
    def _check_condition(self, condition: str, alert_data: Dict[str, Any]) -> bool:
        """条件チェック"""
        # 簡易実装：条件文字列を評価
        if "IF_LATENCY_PERSISTS" in condition:
            return alert_data.get("latency_persists", False)
        elif "IF_FAILOVER_FAILS" in condition:
            return alert_data.get("failover_failed", False)
        return True
    
    async def _execute_action(self, step: RecoveryStep, alert_data: Dict[str, Any]):
        """
        アクション実行
        
        Args:
            step: リカバリステップ
            alert_data: アラートデータ
        """
        # OPSモジュールとの統合（将来実装）
        if step.action_type == ActionType.K8S_SCALE_OUT:
            # K8Sスケールアウト
            print(f"[CRAD] K8Sスケールアウト: {step.target_component} (+{step.params.get('scale_factor', 1)})")
            await asyncio.sleep(0.1)  # シミュレーション
        
        elif step.action_type == ActionType.CHAOS_EXPERIMENT_RUN:
            # カオス実験実行
            print(f"[CRAD] カオス実験: {step.params.get('experiment_type')} on {step.target_component}")
            await asyncio.sleep(0.1)
        
        elif step.action_type == ActionType.HA_TRIGGER_FAILOVER:
            # HAフェイルオーバー
            print(f"[CRAD] HAフェイルオーバー: {step.target_component}")
            await asyncio.sleep(0.1)
        
        elif step.action_type == ActionType.DRP_PITR_TEST:
            # PITR復旧テスト
            print(f"[CRAD] PITR復旧: {step.target_component} → {step.params.get('target_time')}")
            await asyncio.sleep(0.1)
    
    def get_mttr_stats(self) -> Dict[str, Any]:
        """MTTR統計"""
        completed = [e for e in self.executions if e.status == RecoveryStatus.COMPLETED]
        
        if not completed:
            return {
                "total_recoveries": 0,
                "average_mttr": 0,
                "mttr_target": self.mttr_target,
                "within_target": 0,
                "beyond_target": 0
            }
        
        recovery_times = [e.recovery_time_seconds for e in completed if e.recovery_time_seconds]
        avg_mttr = sum(recovery_times) / len(recovery_times) if recovery_times else 0
        
        within_target = len([t for t in recovery_times if t <= self.mttr_target])
        beyond_target = len([t for t in recovery_times if t > self.mttr_target])
        
        return {
            "total_recoveries": len(completed),
            "average_mttr": round(avg_mttr, 2),
            "mttr_target": self.mttr_target,
            "within_target": within_target,
            "beyond_target": beyond_target,
            "success_rate": round(within_target / len(recovery_times) * 100, 1) if recovery_times else 0
        }
    
    def get_crad_summary(self) -> Dict[str, Any]:
        """CRADサマリー"""
        return {
            "runbook_name": self.runbook["runbook_name"],
            "mttr_target_seconds": self.mttr_target,
            "total_protocols": len(self.protocols),
            "total_executions": len(self.executions),
            "mttr_stats": self.get_mttr_stats(),
            "recent_executions": [
                {
                    "execution_id": e.execution_id,
                    "alert_name": e.alert_name,
                    "status": e.status.value,
                    "recovery_time": e.recovery_time_seconds
                }
                for e in self.executions[-5:]
            ]
        }


# グローバルインスタンス
context_aware_debugger = ContextAwareAutoDebugger()
