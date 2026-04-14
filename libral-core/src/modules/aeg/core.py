"""
AEG Core Service
自動進化ゲートウェイのコアサービス
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


@dataclass
class EvolutionTask:
    """進化タスク"""
    task_id: str
    priority: int  # 1-10
    category: str
    description: str
    auto_generated: bool
    status: str  # "pending" | "in_progress" | "completed"
    created_at: datetime


class AEGCore:
    """
    AEG Core Service
    
    プラットフォームの自動進化を管理
    """
    
    def __init__(self):
        self.evolution_tasks: List[EvolutionTask] = []
        self.auto_evolution_enabled = True
    
    def create_evolution_task(
        self, 
        priority: int, 
        category: str, 
        description: str,
        auto_generated: bool = True
    ) -> str:
        """進化タスク作成"""
        from library.components import generate_random_id
        
        task = EvolutionTask(
            task_id=generate_random_id(),
            priority=priority,
            category=category,
            description=description,
            auto_generated=auto_generated,
            status="pending",
            created_at=utc_now()
        )
        
        self.evolution_tasks.append(task)
        return task.task_id
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "auto_evolution_enabled": self.auto_evolution_enabled,
            "total_tasks": len(self.evolution_tasks),
            "pending": sum(1 for t in self.evolution_tasks if t.status == "pending"),
            "in_progress": sum(1 for t in self.evolution_tasks if t.status == "in_progress"),
            "completed": sum(1 for t in self.evolution_tasks if t.status == "completed")
        }


# グローバルインスタンス
aeg_core = AEGCore()
