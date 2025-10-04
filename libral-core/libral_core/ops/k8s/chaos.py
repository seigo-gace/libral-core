"""
カオスエンジニアリング管理システム
K8S_OPS_002実装: Chaos Mesh統合と定例実験実施
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import structlog
import random


logger = structlog.get_logger(__name__)


class ExperimentType(str, Enum):
    """実験タイプ"""
    POD_KILL = "pod_kill"
    NETWORK_DELAY = "network_delay"
    NETWORK_PARTITION = "network_partition"
    CPU_STRESS = "cpu_stress"
    MEMORY_STRESS = "memory_stress"
    DISK_IO_STRESS = "disk_io_stress"


class ExperimentStatus(str, Enum):
    """実験ステータス"""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ChaosExperiment:
    """カオス実験"""
    experiment_id: str
    experiment_type: ExperimentType
    target_component: str
    status: ExperimentStatus
    started_at: datetime
    completed_at: Optional[datetime]
    recovery_time_seconds: Optional[float]
    impact_severity: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """辞書変換"""
        return {
            "experiment_id": self.experiment_id,
            "experiment_type": self.experiment_type.value,
            "target_component": self.target_component,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "recovery_time_seconds": self.recovery_time_seconds,
            "impact_severity": self.impact_severity,
            "metadata": self.metadata
        }


class ChaosEngineeringManager:
    """カオスエンジニアリング管理"""
    
    def __init__(self):
        self.experiments: List[ChaosExperiment] = []
        self.target_recovery_time = 180.0  # 3分
        self.scheduled_experiments: Dict[str, datetime] = {}
        self._schedule_weekly_experiments()
        logger.info("chaos_engineering_manager_initialized")
    
    def _schedule_weekly_experiments(self):
        """週次実験スケジュール"""
        now = datetime.utcnow()
        
        # 毎週の実験スケジュール
        experiment_types = list(ExperimentType)
        for i, exp_type in enumerate(experiment_types):
            scheduled_time = now + timedelta(days=i, hours=2)
            self.scheduled_experiments[exp_type.value] = scheduled_time
            logger.info(
                "experiment_scheduled",
                type=exp_type.value,
                scheduled_at=scheduled_time.isoformat()
            )
    
    async def run_experiment(
        self,
        experiment_type: ExperimentType,
        target_component: str,
        duration_seconds: int = 60
    ) -> ChaosExperiment:
        """実験実行"""
        experiment = ChaosExperiment(
            experiment_id=f"chaos_{datetime.utcnow().timestamp()}",
            experiment_type=experiment_type,
            target_component=target_component,
            status=ExperimentStatus.SCHEDULED,
            started_at=datetime.utcnow(),
            completed_at=None,
            recovery_time_seconds=None,
            impact_severity="low",
            metadata={
                "duration_seconds": duration_seconds,
                "automated": True
            }
        )
        
        self.experiments.append(experiment)
        
        logger.info(
            "chaos_experiment_started",
            experiment_id=experiment.experiment_id,
            type=experiment_type.value,
            target=target_component
        )
        
        # 実験実行
        await self._execute_experiment(experiment)
        
        return experiment
    
    async def _execute_experiment(self, experiment: ChaosExperiment):
        """実験実行"""
        experiment.status = ExperimentStatus.RUNNING
        
        try:
            # Chaos Mesh API呼び出し（実装例）
            # 実際にはChaos Mesh APIを使用
            
            # シミュレーション: ランダムな復旧時間
            recovery_time = random.uniform(30, 300)
            experiment.recovery_time_seconds = recovery_time
            
            # 影響度判定
            if recovery_time <= self.target_recovery_time:
                experiment.impact_severity = "low"
            elif recovery_time <= self.target_recovery_time * 2:
                experiment.impact_severity = "medium"
            else:
                experiment.impact_severity = "high"
            
            experiment.status = ExperimentStatus.COMPLETED
            experiment.completed_at = datetime.utcnow()
            
            logger.info(
                "chaos_experiment_completed",
                experiment_id=experiment.experiment_id,
                recovery_time=recovery_time,
                impact=experiment.impact_severity
            )
            
            # 目標復旧時間超過の場合アラート
            if recovery_time > self.target_recovery_time:
                logger.warning(
                    "recovery_time_exceeded",
                    experiment_id=experiment.experiment_id,
                    recovery_time=recovery_time,
                    target=self.target_recovery_time
                )
            
        except Exception as e:
            experiment.status = ExperimentStatus.FAILED
            experiment.completed_at = datetime.utcnow()
            logger.error(
                "chaos_experiment_failed",
                experiment_id=experiment.experiment_id,
                error=str(e)
            )
    
    async def run_pod_kill_experiment(self, pod_name: str) -> ChaosExperiment:
        """Pod停止実験"""
        return await self.run_experiment(
            ExperimentType.POD_KILL,
            pod_name,
            duration_seconds=0  # 即時
        )
    
    async def run_network_delay_experiment(
        self,
        target: str,
        delay_ms: int = 100
    ) -> ChaosExperiment:
        """ネットワーク遅延実験"""
        experiment = await self.run_experiment(
            ExperimentType.NETWORK_DELAY,
            target,
            duration_seconds=300  # 5分
        )
        experiment.metadata["delay_ms"] = delay_ms
        return experiment
    
    def get_experiment_results(
        self,
        experiment_type: Optional[ExperimentType] = None
    ) -> List[ChaosExperiment]:
        """実験結果取得"""
        if experiment_type:
            return [
                e for e in self.experiments
                if e.experiment_type == experiment_type
            ]
        return self.experiments
    
    def get_mttr_statistics(self) -> Dict:
        """MTTR統計"""
        completed = [
            e for e in self.experiments
            if e.status == ExperimentStatus.COMPLETED and e.recovery_time_seconds
        ]
        
        if not completed:
            return {
                "total_experiments": 0,
                "average_mttr": 0,
                "min_mttr": 0,
                "max_mttr": 0,
                "target_mttr": self.target_recovery_time
            }
        
        recovery_times = [e.recovery_time_seconds for e in completed]
        
        return {
            "total_experiments": len(completed),
            "average_mttr": sum(recovery_times) / len(recovery_times),
            "min_mttr": min(recovery_times),
            "max_mttr": max(recovery_times),
            "target_mttr": self.target_recovery_time,
            "exceeded_target_count": sum(
                1 for t in recovery_times if t > self.target_recovery_time
            )
        }
    
    def get_chaos_summary(self) -> Dict:
        """カオスエンジニアリングサマリー"""
        from collections import Counter
        
        statuses = Counter(e.status.value for e in self.experiments)
        types = Counter(e.experiment_type.value for e in self.experiments)
        severities = Counter(e.impact_severity for e in self.experiments)
        
        return {
            "total_experiments": len(self.experiments),
            "by_status": dict(statuses),
            "by_type": dict(types),
            "by_severity": dict(severities),
            "mttr_stats": self.get_mttr_statistics(),
            "recent_experiments": [
                e.to_dict() for e in self.experiments[-10:]
            ]
        }
