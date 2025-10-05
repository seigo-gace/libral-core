"""
Vaporization API Router
キャッシュ揮発プロトコル APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from .core import vaporization_core
from .redis_ttl import redis_ttl_enforcer
from .flush_hook import kbe_flush_hook

router = APIRouter(prefix="/vaporization", tags=["vaporization"])


# === Request/Response Models ===

class TTLEnforceRequest(BaseModel):
    """TTL強制リクエスト"""
    key: str
    custom_ttl: Optional[int] = None


class FlushRequest(BaseModel):
    """揮発リクエスト"""
    keys: List[str]


class KBEExtractionCompleteRequest(BaseModel):
    """KBE抽出完了通知"""
    knowledge_record_id: str
    related_keys: List[str]


# === Core Endpoints ===

@router.get("/stats")
async def get_vaporization_stats():
    """揮発統計取得"""
    try:
        return vaporization_core.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Redis TTL Enforcer Endpoints ===

@router.post("/ttl/enforce")
async def enforce_ttl(request: TTLEnforceRequest):
    """TTL強制設定"""
    try:
        result = redis_ttl_enforcer.enforce_ttl(request.key, request.custom_ttl)
        
        if result["enforced"]:
            vaporization_core.update_stats(ttl_enforced=1)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ttl/check/{key}")
async def check_ttl_requirement(key: str):
    """TTL強制要否チェック"""
    try:
        should_enforce = redis_ttl_enforcer.should_enforce_ttl(key)
        return {
            "key": key,
            "should_enforce_ttl": should_enforce,
            "reason": "Matches personal data pattern" if should_enforce else "Does not match personal data patterns"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ttl/summary")
async def get_ttl_summary():
    """TTLサマリー"""
    try:
        return redis_ttl_enforcer.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Flush Hook Endpoints ===

@router.post("/flush/kbe-extraction-complete")
async def on_kbe_extraction_complete(request: KBEExtractionCompleteRequest):
    """KBE抽出完了フック"""
    try:
        event_id = kbe_flush_hook.on_kbe_extraction_complete(
            request.knowledge_record_id,
            request.related_keys
        )
        
        vaporization_core.update_stats(flush_executed=len(request.related_keys))
        
        return {
            "event_id": event_id,
            "keys_flushed": len(request.related_keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flush/manual")
async def manual_flush(request: FlushRequest):
    """手動揮発"""
    try:
        event_id = kbe_flush_hook.manual_flush(request.keys)
        
        vaporization_core.update_stats(flush_executed=len(request.keys))
        
        return {
            "event_id": event_id,
            "keys_flushed": len(request.keys)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flush/recent")
async def get_recent_flushes(limit: int = 20):
    """最近の揮発イベント取得"""
    try:
        return {"flush_events": kbe_flush_hook.get_recent_flushes(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flush/summary")
async def get_flush_summary():
    """揮発サマリー"""
    try:
        return kbe_flush_hook.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Dashboard Endpoint ===

@router.get("/dashboard")
async def get_vaporization_dashboard():
    """揮発プロトコル統合ダッシュボード"""
    try:
        return {
            "vaporization_version": "1.0.0",
            "core_stats": vaporization_core.get_stats(),
            "ttl_enforcer": redis_ttl_enforcer.get_summary(),
            "flush_hook": kbe_flush_hook.get_summary(),
            "privacy_guarantees": {
                "max_retention": "24 hours maximum",
                "auto_flush": "Immediate deletion after KBE extraction",
                "patterns_protected": redis_ttl_enforcer.personal_data_patterns
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
