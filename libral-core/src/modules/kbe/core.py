"""
KBE Core Service
ナレッジ・ブースター・エンジンのコアサービス
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class KnowledgeRecord:
    """知識記録"""
    record_id: str
    user_id: str
    knowledge_type: str
    encrypted_data: str
    timestamp: datetime


class KBECore:
    """
    KBE Core Service
    
    プライバシー保護型集合知システム
    """
    
    def __init__(self):
        self.knowledge_records: List[KnowledgeRecord] = []
        self.privacy_mode = True
    
    def submit_knowledge(self, user_id: str, knowledge_type: str, encrypted_data: str) -> str:
        """
        知識提出
        
        Args:
            user_id: ユーザーID（匿名化可能）
            knowledge_type: 知識タイプ
            encrypted_data: 暗号化された知識データ
        
        Returns:
            記録ID
        """
        record = KnowledgeRecord(
            record_id=generate_random_id(),
            user_id=user_id if not self.privacy_mode else f"anon_{hash(user_id) % 10000}",
            knowledge_type=knowledge_type,
            encrypted_data=encrypted_data,
            timestamp=utc_now()
        )
        
        self.knowledge_records.append(record)
        
        # 最新1000件のみ保持
        if len(self.knowledge_records) > 1000:
            self.knowledge_records = self.knowledge_records[-1000:]
        
        return record.record_id
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        knowledge_by_type: Dict[str, int] = {}
        
        for record in self.knowledge_records:
            knowledge_by_type[record.knowledge_type] = knowledge_by_type.get(record.knowledge_type, 0) + 1
        
        return {
            "total_knowledge_records": len(self.knowledge_records),
            "privacy_mode": self.privacy_mode,
            "knowledge_by_type": knowledge_by_type,
            "unique_contributors": len(set(r.user_id for r in self.knowledge_records))
        }


# グローバルインスタンス
kbe_core = KBECore()
