"""
Federated Learning Interface
フェデレーテッド・ラーニング・インターフェース

個人ログサーバー側でAI学習を実行可能にする
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class LearningTask:
    """学習タスク"""
    task_id: str
    model_type: str
    parameters: Dict[str, Any]
    status: str  # "pending" | "running" | "completed" | "failed"
    created_at: datetime
    completed_at: Optional[datetime] = None


@dataclass
class LocalModel:
    """ローカルモデル"""
    model_id: str
    user_id: str
    model_type: str
    weights: List[float]  # 簡易的な重みリスト
    accuracy: float
    timestamp: datetime


class FederatedLearningInterface:
    """
    フェデレーテッド・ラーニング・インターフェース
    
    個人ログサーバーでAI学習を実行し、
    モデルパラメータのみを中央に送信
    """
    
    def __init__(self):
        self.learning_tasks: Dict[str, LearningTask] = {}
        self.local_models: List[LocalModel] = []
    
    def create_learning_task(self, model_type: str, parameters: Dict[str, Any]) -> str:
        """
        学習タスク作成
        
        Args:
            model_type: モデルタイプ（"text_classification", "sentiment_analysis"等）
            parameters: 学習パラメータ
        
        Returns:
            タスクID
        """
        task = LearningTask(
            task_id=generate_random_id(),
            model_type=model_type,
            parameters=parameters,
            status="pending",
            created_at=utc_now()
        )
        
        self.learning_tasks[task.task_id] = task
        return task.task_id
    
    def submit_local_model(
        self, 
        user_id: str, 
        model_type: str, 
        weights: List[float], 
        accuracy: float
    ) -> str:
        """
        ローカルモデル提出
        
        ユーザーのログサーバーで学習したモデルパラメータを提出
        
        Args:
            user_id: ユーザーID
            model_type: モデルタイプ
            weights: モデル重み
            accuracy: 精度
        
        Returns:
            モデルID
        """
        model = LocalModel(
            model_id=generate_random_id(),
            user_id=user_id,
            model_type=model_type,
            weights=weights,
            accuracy=accuracy,
            timestamp=utc_now()
        )
        
        self.local_models.append(model)
        
        # 最新100件のみ保持
        if len(self.local_models) > 100:
            self.local_models = self.local_models[-100:]
        
        return model.model_id
    
    def get_aggregated_weights(self, model_type: str) -> Optional[List[float]]:
        """
        集約モデル重み取得
        
        同じmodel_typeのローカルモデルを精度加重平均で集約
        
        Args:
            model_type: モデルタイプ
        
        Returns:
            集約された重み
        """
        relevant_models = [m for m in self.local_models if m.model_type == model_type]
        
        if not relevant_models:
            return None
        
        # 精度加重平均
        total_accuracy = sum(m.accuracy for m in relevant_models)
        if total_accuracy == 0:
            return None
        
        # 重みの次元数を最初のモデルから取得
        weight_dim = len(relevant_models[0].weights)
        
        aggregated = [0.0] * weight_dim
        for model in relevant_models:
            weight = model.accuracy / total_accuracy
            for i in range(min(weight_dim, len(model.weights))):
                aggregated[i] += model.weights[i] * weight
        
        return aggregated
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        model_types = set(m.model_type for m in self.local_models)
        
        return {
            "total_tasks": len(self.learning_tasks),
            "pending_tasks": sum(1 for t in self.learning_tasks.values() if t.status == "pending"),
            "completed_tasks": sum(1 for t in self.learning_tasks.values() if t.status == "completed"),
            "total_local_models": len(self.local_models),
            "model_types": list(model_types),
            "unique_contributors": len(set(m.user_id for m in self.local_models))
        }


# グローバルインスタンス
federated_learning = FederatedLearningInterface()
