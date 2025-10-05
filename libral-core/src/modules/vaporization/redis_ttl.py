"""
Redis TTL Enforcer
Redis TTL 24時間強制設定

Redisへの書き込み時、個人関連情報を含む全てのキーに
TTL 24時間を自動設定
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class TTLRecord:
    """TTL記録"""
    record_id: str
    key_pattern: str
    ttl_seconds: int
    enforced_at: datetime


class RedisTTLEnforcer:
    """
    Redis TTL強制設定
    
    個人関連データキーに自動的にTTLを設定
    """
    
    def __init__(self, default_ttl_seconds: int = 86400):
        """
        Args:
            default_ttl_seconds: デフォルトTTL（秒）、デフォルト24時間
        """
        self.default_ttl_seconds = default_ttl_seconds
        self.ttl_records: List[TTLRecord] = []
        self.personal_data_patterns = [
            "user:*",
            "session:*",
            "personal:*",
            "telegram:*:data",
            "kbe:knowledge:*"
        ]
    
    def should_enforce_ttl(self, key: str) -> bool:
        """
        TTL強制が必要か判定
        
        Args:
            key: Redisキー
        
        Returns:
            強制が必要ならTrue
        """
        import fnmatch
        
        for pattern in self.personal_data_patterns:
            if fnmatch.fnmatch(key, pattern):
                return True
        return False
    
    def enforce_ttl(self, key: str, custom_ttl: Optional[int] = None) -> Dict[str, Any]:
        """
        TTL強制設定（Mock実装）
        
        Args:
            key: Redisキー
            custom_ttl: カスタムTTL（秒）
        
        Returns:
            設定結果
        """
        if not self.should_enforce_ttl(key):
            return {
                "enforced": False,
                "reason": "Key does not match personal data patterns"
            }
        
        ttl = custom_ttl if custom_ttl else self.default_ttl_seconds
        
        # TTL記録
        record = TTLRecord(
            record_id=generate_random_id(),
            key_pattern=key,
            ttl_seconds=ttl,
            enforced_at=utc_now()
        )
        
        self.ttl_records.append(record)
        
        # 最新100件のみ保持
        if len(self.ttl_records) > 100:
            self.ttl_records = self.ttl_records[-100:]
        
        return {
            "enforced": True,
            "key": key,
            "ttl_seconds": ttl,
            "ttl_hours": ttl / 3600,
            "expires_at": (utc_now().timestamp() + ttl)
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "default_ttl_hours": self.default_ttl_seconds / 3600,
            "personal_data_patterns": self.personal_data_patterns,
            "total_ttl_enforcements": len(self.ttl_records),
            "recent_enforcements": [
                {
                    "key_pattern": r.key_pattern,
                    "ttl_hours": r.ttl_seconds / 3600,
                    "enforced_at": r.enforced_at.isoformat()
                }
                for r in self.ttl_records[-10:]  # 最新10件
            ]
        }


# グローバルインスタンス
redis_ttl_enforcer = RedisTTLEnforcer()
