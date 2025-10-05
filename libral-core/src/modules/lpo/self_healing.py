"""
Self-Healing AI
自己修復AI - CRADの実行ログを分析し、動的に修復シーケンスを提案
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class RecoverySuggestion:
    """リカバリ提案"""
    suggestion_id: str
    alert_pattern: str
    suggested_steps: List[str]
    confidence: float  # 0.0-1.0
    based_on_executions: int
    created_at: datetime


class SelfHealingAI:
    """
    自己修復AI
    
    CRADの実行ログを分析し、recovery_runbook_crad.jsonの
    修復シーケンスを動的に提案/修正
    """
    
    def __init__(self):
        self.execution_history: List[Dict[str, Any]] = []
        self.suggestions: Dict[str, RecoverySuggestion] = {}
        self.learning_enabled = True
    
    def record_execution(self, execution_data: Dict[str, Any]):
        """
        CRAD実行を記録
        
        Args:
            execution_data: 実行データ（alert_name, status, recovery_time等）
        """
        self.execution_history.append({
            "timestamp": utc_now().isoformat(),
            **execution_data
        })
        
        # 100件を超えたら古いものを削除
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
        
        # 学習実行
        if self.learning_enabled:
            self._learn_from_history()
    
    def _learn_from_history(self):
        """実行履歴から学習"""
        # アラートパターンごとに成功率を分析
        alert_stats: Dict[str, Dict[str, Any]] = {}
        
        for execution in self.execution_history:
            alert_name = execution.get("alert_name")
            status = execution.get("status")
            recovery_time = execution.get("recovery_time_seconds", 0)
            
            if alert_name not in alert_stats:
                alert_stats[alert_name] = {
                    "total": 0,
                    "success": 0,
                    "avg_time": 0,
                    "times": []
                }
            
            alert_stats[alert_name]["total"] += 1
            if status == "completed":
                alert_stats[alert_name]["success"] += 1
            alert_stats[alert_name]["times"].append(recovery_time)
        
        # 成功率が低いアラートに対して提案を生成
        for alert_name, stats in alert_stats.items():
            if stats["total"] >= 3:  # 最低3回の実行が必要
                success_rate = stats["success"] / stats["total"]
                avg_time = sum(stats["times"]) / len(stats["times"])
                
                # 成功率が80%未満または平均時間が180秒超の場合
                if success_rate < 0.8 or avg_time > 180:
                    self._generate_suggestion(alert_name, stats, success_rate)
    
    def _generate_suggestion(self, alert_name: str, stats: Dict[str, Any], success_rate: float):
        """提案生成"""
        # AIベースの提案（現在は簡易版）
        suggested_steps = []
        
        if success_rate < 0.5:
            suggested_steps.append("既存の修復手順を見直し、より効果的な代替手段を検討")
            suggested_steps.append("外部専門家への自動エスカレーションを追加")
        elif success_rate < 0.8:
            suggested_steps.append("修復手順の実行タイムアウトを延長")
            suggested_steps.append("事前チェック手順を追加して失敗率を低減")
        
        avg_time = sum(stats["times"]) / len(stats["times"])
        if avg_time > 180:
            suggested_steps.append(f"平均復旧時間({avg_time:.1f}秒)がMTTRターゲット(180秒)を超過")
            suggested_steps.append("並列実行可能な手順を特定し、復旧時間を短縮")
        
        suggestion = RecoverySuggestion(
            suggestion_id=generate_random_id(),
            alert_pattern=alert_name,
            suggested_steps=suggested_steps,
            confidence=success_rate,
            based_on_executions=stats["total"],
            created_at=utc_now()
        )
        
        self.suggestions[alert_name] = suggestion
    
    def get_suggestions(self) -> List[Dict[str, Any]]:
        """提案リスト取得"""
        return [
            {
                "suggestion_id": s.suggestion_id,
                "alert_pattern": s.alert_pattern,
                "suggested_steps": s.suggested_steps,
                "confidence": round(s.confidence, 2),
                "based_on_executions": s.based_on_executions,
                "created_at": s.created_at.isoformat()
            }
            for s in self.suggestions.values()
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "learning_enabled": self.learning_enabled,
            "execution_history_count": len(self.execution_history),
            "active_suggestions": len(self.suggestions),
            "suggestions": self.get_suggestions()
        }


# グローバルインスタンス
self_healing_ai = SelfHealingAI()
