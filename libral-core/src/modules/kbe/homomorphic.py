"""
Homomorphic Aggregator
同型暗号による学習結果集計

学習結果を暗号化したまま中央で集計
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class EncryptedModel:
    """暗号化モデル"""
    model_id: str
    user_id: str
    encrypted_weights: str  # 暗号化された重みデータ
    encryption_scheme: str  # "mock_homomorphic" (実際の実装ではPaillier等)
    timestamp: datetime


@dataclass
class AggregationResult:
    """集約結果"""
    result_id: str
    model_type: str
    aggregated_weights: str  # 暗号化されたまま集約された重み
    contributor_count: int
    timestamp: datetime


class HomomorphicAggregator:
    """
    同型暗号による集約
    
    学習結果を暗号化したまま集計
    実際の実装ではPaillier暗号やFHEを使用
    """
    
    def __init__(self):
        self.encrypted_models: List[EncryptedModel] = []
        self.aggregation_results: List[AggregationResult] = []
    
    def submit_encrypted_model(
        self, 
        user_id: str, 
        encrypted_weights: str, 
        encryption_scheme: str = "mock_homomorphic"
    ) -> str:
        """
        暗号化モデル提出
        
        Args:
            user_id: ユーザーID
            encrypted_weights: 暗号化された重み
            encryption_scheme: 暗号化方式
        
        Returns:
            モデルID
        """
        model = EncryptedModel(
            model_id=generate_random_id(),
            user_id=user_id,
            encrypted_weights=encrypted_weights,
            encryption_scheme=encryption_scheme,
            timestamp=utc_now()
        )
        
        self.encrypted_models.append(model)
        
        # 最新100件のみ保持
        if len(self.encrypted_models) > 100:
            self.encrypted_models = self.encrypted_models[-100:]
        
        return model.model_id
    
    def aggregate_encrypted(self, model_type: str) -> Optional[str]:
        """
        暗号化されたまま集約
        
        実際の実装では同型暗号の加算演算を使用
        
        Args:
            model_type: モデルタイプ
        
        Returns:
            集約結果ID
        """
        if not self.encrypted_models:
            return None
        
        # Mock実装: 実際にはPaillier暗号等で暗号化したまま加算
        # ここでは簡易的にデータを連結
        aggregated_data = "|".join(m.encrypted_weights for m in self.encrypted_models)
        
        result = AggregationResult(
            result_id=generate_random_id(),
            model_type=model_type,
            aggregated_weights=f"AGGREGATED_{len(self.encrypted_models)}_{aggregated_data[:50]}...",
            contributor_count=len(self.encrypted_models),
            timestamp=utc_now()
        )
        
        self.aggregation_results.append(result)
        
        # 最新10件のみ保持
        if len(self.aggregation_results) > 10:
            self.aggregation_results = self.aggregation_results[-10:]
        
        return result.result_id
    
    def get_aggregation_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """集約結果取得"""
        for result in self.aggregation_results:
            if result.result_id == result_id:
                return {
                    "result_id": result.result_id,
                    "model_type": result.model_type,
                    "aggregated_weights": result.aggregated_weights,
                    "contributor_count": result.contributor_count,
                    "timestamp": result.timestamp.isoformat()
                }
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "total_encrypted_models": len(self.encrypted_models),
            "total_aggregations": len(self.aggregation_results),
            "unique_contributors": len(set(m.user_id for m in self.encrypted_models)),
            "encryption_schemes": list(set(m.encryption_scheme for m in self.encrypted_models))
        }


# グローバルインスタンス
homomorphic_aggregator = HomomorphicAggregator()
