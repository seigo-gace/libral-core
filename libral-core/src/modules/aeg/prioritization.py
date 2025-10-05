"""
Development Prioritization AI
開発優先度決定AI

KBデータとCRADのMTTR統計を分析し、コード改善の優先度を決定
"""

from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class ImprovementSuggestion:
    """改善提案"""
    suggestion_id: str
    priority_score: float  # 0.0-10.0
    category: str
    title: str
    description: str
    impact_estimate: str  # "high" | "medium" | "low"
    effort_estimate: str  # "high" | "medium" | "low"
    created_at: datetime


class DevelopmentPrioritizationAI:
    """
    開発優先度決定AI
    
    システムメトリクスと集合知から改善優先度を計算
    """
    
    def __init__(self):
        self.suggestions: List[ImprovementSuggestion] = []
    
    def analyze_and_prioritize(
        self,
        health_score: float,
        mttr_stats: Dict[str, Any],
        knowledge_base_insights: Dict[str, Any]
    ) -> List[str]:
        """
        分析と優先度決定
        
        Args:
            health_score: システム健全性スコア
            mttr_stats: MTTR統計
            knowledge_base_insights: KBインサイト
        
        Returns:
            生成された提案IDリスト
        """
        generated_ids = []
        
        # ヘルススコアが低い場合
        if health_score < 75:
            suggestion_id = self._create_suggestion(
                priority_score=9.0,
                category="system_health",
                title="システム健全性の改善が必要",
                description=f"現在のヘルススコア {health_score:.1f} を改善するための施策が必要",
                impact_estimate="high",
                effort_estimate="medium"
            )
            generated_ids.append(suggestion_id)
        
        # MTTR統計から優先度判定
        if mttr_stats.get("avg_recovery_time", 0) > 180:
            suggestion_id = self._create_suggestion(
                priority_score=8.5,
                category="crad_optimization",
                title="CRAD復旧時間の最適化",
                description=f"平均復旧時間 {mttr_stats.get('avg_recovery_time')} 秒をターゲット180秒以下に短縮",
                impact_estimate="high",
                effort_estimate="medium"
            )
            generated_ids.append(suggestion_id)
        
        # KBインサイトから提案
        if knowledge_base_insights.get("user_feedback_count", 0) > 10:
            suggestion_id = self._create_suggestion(
                priority_score=7.0,
                category="user_experience",
                title="ユーザーフィードバックに基づく改善",
                description="集合知から得られたユーザー要望を実装",
                impact_estimate="medium",
                effort_estimate="low"
            )
            generated_ids.append(suggestion_id)
        
        return generated_ids
    
    def _create_suggestion(
        self,
        priority_score: float,
        category: str,
        title: str,
        description: str,
        impact_estimate: str,
        effort_estimate: str
    ) -> str:
        """提案作成"""
        suggestion = ImprovementSuggestion(
            suggestion_id=generate_random_id(),
            priority_score=priority_score,
            category=category,
            title=title,
            description=description,
            impact_estimate=impact_estimate,
            effort_estimate=effort_estimate,
            created_at=utc_now()
        )
        
        self.suggestions.append(suggestion)
        
        # 最新50件のみ保持
        if len(self.suggestions) > 50:
            self.suggestions = self.suggestions[-50:]
        
        return suggestion.suggestion_id
    
    def get_top_priorities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """優先度上位の提案取得"""
        sorted_suggestions = sorted(
            self.suggestions,
            key=lambda s: s.priority_score,
            reverse=True
        )[:limit]
        
        return [
            {
                "suggestion_id": s.suggestion_id,
                "priority_score": round(s.priority_score, 2),
                "category": s.category,
                "title": s.title,
                "description": s.description,
                "impact_estimate": s.impact_estimate,
                "effort_estimate": s.effort_estimate,
                "created_at": s.created_at.isoformat()
            }
            for s in sorted_suggestions
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "total_suggestions": len(self.suggestions),
            "by_category": {
                "system_health": sum(1 for s in self.suggestions if s.category == "system_health"),
                "crad_optimization": sum(1 for s in self.suggestions if s.category == "crad_optimization"),
                "user_experience": sum(1 for s in self.suggestions if s.category == "user_experience")
            }
        }


# グローバルインスタンス
prioritization_ai = DevelopmentPrioritizationAI()
