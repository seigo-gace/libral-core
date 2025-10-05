"""
Vaporization Core Service
キャッシュ揮発プロトコルのコアサービス
"""

from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


@dataclass
class VaporizationStats:
    """揮発統計"""
    total_keys_monitored: int
    ttl_enforced_count: int
    flush_executed_count: int
    last_check: datetime


class VaporizationCore:
    """
    揮発プロトコルコアサービス
    
    個人関連データの揮発を管理
    """
    
    def __init__(self):
        self.stats = VaporizationStats(
            total_keys_monitored=0,
            ttl_enforced_count=0,
            flush_executed_count=0,
            last_check=utc_now()
        )
        self.max_ttl_seconds = 86400  # 24時間
        self.vaporization_enabled = True
    
    def get_stats(self) -> Dict[str, Any]:
        """統計取得"""
        return {
            "vaporization_enabled": self.vaporization_enabled,
            "max_ttl_hours": self.max_ttl_seconds / 3600,
            "total_keys_monitored": self.stats.total_keys_monitored,
            "ttl_enforced_count": self.stats.ttl_enforced_count,
            "flush_executed_count": self.stats.flush_executed_count,
            "last_check": self.stats.last_check.isoformat()
        }
    
    def update_stats(self, ttl_enforced: int = 0, flush_executed: int = 0):
        """統計更新"""
        self.stats.ttl_enforced_count += ttl_enforced
        self.stats.flush_executed_count += flush_executed
        self.stats.last_check = utc_now()


# グローバルインスタンス
vaporization_core = VaporizationCore()
