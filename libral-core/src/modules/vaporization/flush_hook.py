"""
KBE Flush Hook
KBE知識抽出完了後の即時揮発フック

KBEが知識抽出を完了した直後、関連するキャッシュキーを
TTLに関わらず即時削除するフック（FLUSH_HOOK）
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class FlushEvent:
    """揮発イベント"""
    event_id: str
    trigger: str  # "kbe_extraction_complete" | "manual" | "scheduled"
    keys_flushed: List[str]
    flushed_at: datetime


class KBEFlushHook:
    """
    KBE即時揮発フック
    
    知識抽出完了時にキャッシュを即時削除
    """
    
    def __init__(self):
        self.flush_events: List[FlushEvent] = []
        self.auto_flush_enabled = True
    
    def on_kbe_extraction_complete(self, knowledge_record_id: str, related_keys: List[str]) -> str:
        """
        KBE抽出完了フック
        
        Args:
            knowledge_record_id: 知識記録ID
            related_keys: 関連するRedisキー
        
        Returns:
            イベントID
        """
        if not self.auto_flush_enabled:
            return ""
        
        event = FlushEvent(
            event_id=generate_random_id(),
            trigger="kbe_extraction_complete",
            keys_flushed=related_keys,
            flushed_at=utc_now()
        )
        
        self.flush_events.append(event)
        
        # 最新100件のみ保持
        if len(self.flush_events) > 100:
            self.flush_events = self.flush_events[-100:]
        
        # 実際のRedis削除（Mock実装）
        # redis_client.delete(*related_keys)
        
        return event.event_id
    
    def manual_flush(self, keys: List[str]) -> str:
        """
        手動揮発
        
        Args:
            keys: 削除するキー
        
        Returns:
            イベントID
        """
        event = FlushEvent(
            event_id=generate_random_id(),
            trigger="manual",
            keys_flushed=keys,
            flushed_at=utc_now()
        )
        
        self.flush_events.append(event)
        
        if len(self.flush_events) > 100:
            self.flush_events = self.flush_events[-100:]
        
        return event.event_id
    
    def get_recent_flushes(self, limit: int = 20) -> List[Dict[str, Any]]:
        """最近の揮発イベント取得"""
        recent = self.flush_events[-limit:]
        
        return [
            {
                "event_id": e.event_id,
                "trigger": e.trigger,
                "keys_count": len(e.keys_flushed),
                "flushed_at": e.flushed_at.isoformat()
            }
            for e in recent
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "auto_flush_enabled": self.auto_flush_enabled,
            "total_flush_events": len(self.flush_events),
            "total_keys_flushed": sum(len(e.keys_flushed) for e in self.flush_events),
            "by_trigger": {
                "kbe_extraction_complete": sum(1 for e in self.flush_events if e.trigger == "kbe_extraction_complete"),
                "manual": sum(1 for e in self.flush_events if e.trigger == "manual"),
                "scheduled": sum(1 for e in self.flush_events if e.trigger == "scheduled")
            }
        }


# グローバルインスタンス
kbe_flush_hook = KBEFlushHook()
