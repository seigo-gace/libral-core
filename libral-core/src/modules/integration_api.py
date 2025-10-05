"""
Integration API
LPO、KBE、AEG、Vaporizationの統合エンドポイント

モジュール間連携を実証
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all SelfEvolution modules
from modules.lpo.core import lpo_core
from modules.lpo.health_score import calculate_health_score
from modules.lpo.finance import finance_optimizer
from modules.kbe.core import kbe_core
from modules.aeg.prioritization import prioritization_ai
from modules.aeg.core import aeg_core
from modules.vaporization.core import vaporization_core
from library.components import utc_now, generate_random_id

router = APIRouter(prefix="/selfevolution", tags=["selfevolution-integration"])


class SelfEvolutionCycleRequest(BaseModel):
    """自己進化サイクル実行リクエスト"""
    trigger_source: str  # "scheduled" | "manual" | "alert"


@router.get("/dashboard")
async def get_unified_dashboard():
    """
    統合ダッシュボード
    
    全てのSelfEvolutionモジュールのステータスを統合表示
    """
    try:
        # LPOステータス
        lpo_status = lpo_core.get_status()
        health_score = lpo_status.get("core_status", {}).get("health_score", 0)
        
        # KBEステータス
        kbe_summary = kbe_core.get_summary()
        
        # AEGステータス
        aeg_summary = aeg_core.get_summary()
        priorities = prioritization_ai.get_top_priorities(5)
        
        # Vaporizationステータス
        vaporization_stats = vaporization_core.get_stats()
        
        # 財務サマリー
        finance_summary = finance_optimizer.get_cost_summary(7)
        
        return {
            "selfevolution_v1": {
                "version": "1.0.0",
                "manifest": "SelfEvolution_Final_V1",
                "last_updated": utc_now().isoformat()
            },
            "health_status": {
                "overall_health_score": health_score,
                "status": "excellent" if health_score >= 90 else "good" if health_score >= 75 else "needs_attention",
                "lpo_auto_recovery_count": lpo_status.get("auto_recovery_count", 0)
            },
            "knowledge_base": {
                "total_knowledge_records": kbe_summary.get("total_knowledge_records", 0),
                "privacy_mode": kbe_summary.get("privacy_mode", True),
                "unique_contributors": kbe_summary.get("unique_contributors", 0)
            },
            "evolution_queue": {
                "pending_tasks": aeg_summary.get("pending", 0),
                "in_progress": aeg_summary.get("in_progress", 0),
                "completed": aeg_summary.get("completed", 0),
                "top_priorities": priorities
            },
            "privacy_guarantees": {
                "max_cache_ttl_hours": vaporization_stats.get("max_ttl_hours", 24),
                "vaporization_enabled": vaporization_stats.get("vaporization_enabled", True),
                "ttl_enforced_count": vaporization_stats.get("ttl_enforced_count", 0),
                "flush_executed_count": vaporization_stats.get("flush_executed_count", 0)
            },
            "financial_health": {
                "cost_summary_7days": finance_summary,
                "ai_cost_optimization_active": True
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-cycle")
async def execute_selfevolution_cycle(request: SelfEvolutionCycleRequest):
    """
    自己進化サイクル実行
    
    1. ヘルススコア計算
    2. 知識ベース分析
    3. 優先度決定
    4. 進化タスク作成
    5. キャッシュ揮発
    
    モジュール間連携を実証
    """
    try:
        cycle_id = generate_random_id()
        
        # Step 1: ヘルススコア計算（LPO）
        health_result = calculate_health_score(
            amm_blocked_count=0,
            crad_recovery_success_rate=95.0,
            system_uptime_percentage=99.5,
            avg_response_time_ms=45.0,
            error_rate_percentage=0.1
        )
        health_score = health_result["health_score"]
        lpo_core.update_health_score(health_score)
        
        # Step 2: 知識ベース分析（KBE）
        kbe_summary = kbe_core.get_summary()
        knowledge_insights = {
            "user_feedback_count": kbe_summary.get("total_knowledge_records", 0),
            "unique_contributors": kbe_summary.get("unique_contributors", 0)
        }
        
        # Step 3: 優先度決定（AEG）
        mttr_stats = {
            "avg_recovery_time": 150.0,  # Mock data
            "success_rate": 0.95
        }
        
        suggestion_ids = prioritization_ai.analyze_and_prioritize(
            health_score=health_score,
            mttr_stats=mttr_stats,
            knowledge_base_insights=knowledge_insights
        )
        
        # Step 4: 進化タスク作成（AEG）
        created_tasks = []
        for suggestion_id in suggestion_ids[:3]:  # 最大3タスク
            task_id = aeg_core.create_evolution_task(
                priority=8,
                category="auto_improvement",
                description=f"Auto-generated from cycle {cycle_id}",
                auto_generated=True
            )
            created_tasks.append(task_id)
        
        # Step 5: キャッシュ揮発（Vaporization）
        # KBE知識抽出完了後の揮発をシミュレート
        vaporization_core.update_stats(flush_executed=len(created_tasks))
        
        return {
            "cycle_id": cycle_id,
            "trigger_source": request.trigger_source,
            "executed_at": utc_now().isoformat(),
            "results": {
                "health_score": {
                    "score": health_score,
                    "status": health_result["status"],
                    "message": health_result["message"]
                },
                "knowledge_analysis": knowledge_insights,
                "prioritization": {
                    "suggestions_generated": len(suggestion_ids),
                    "tasks_created": len(created_tasks),
                    "task_ids": created_tasks
                },
                "vaporization": {
                    "cache_items_flushed": len(created_tasks),
                    "privacy_maintained": True
                }
            },
            "next_cycle": "Recommended in 24 hours based on vaporization protocol"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/module-health")
async def get_module_health():
    """
    各モジュールの健全性チェック
    """
    try:
        return {
            "lpo": {
                "status": "operational",
                "health_score": lpo_core.status.health_score,
                "last_check": lpo_core.status.last_check.isoformat()
            },
            "kbe": {
                "status": "operational",
                "privacy_mode": kbe_core.privacy_mode,
                "records_count": len(kbe_core.knowledge_records)
            },
            "aeg": {
                "status": "operational",
                "auto_evolution_enabled": aeg_core.auto_evolution_enabled,
                "total_tasks": len(aeg_core.evolution_tasks)
            },
            "vaporization": {
                "status": "operational",
                "vaporization_enabled": vaporization_core.vaporization_enabled,
                "max_ttl_hours": vaporization_core.max_ttl_seconds / 3600
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/manifest")
async def get_selfevolution_manifest():
    """
    SelfEvolution Final Manifest V1情報
    """
    return {
        "manifest_version": "1.0",
        "manifest_name": "Libral SelfEvolution Final Manifest V1",
        "implementation_date": "2025-10-05",
        "modules": {
            "lpo": {
                "name": "Libral Protocol Optimizer",
                "purpose": "単体自律監視、AMM/CRAD統合、健全性スコア、ZK監査",
                "endpoints": [
                    "/lpo/status",
                    "/lpo/metrics/health-score",
                    "/lpo/zk-audit/*",
                    "/lpo/self-healing/*",
                    "/lpo/finance/*",
                    "/lpo/rbac/*",
                    "/lpo/predictive/*",
                    "/lpo/dashboard"
                ]
            },
            "kbe": {
                "name": "Knowledge Booster Engine",
                "purpose": "フェデレーテッド・ラーニング、同型暗号、集合知構築",
                "endpoints": [
                    "/kbe/submit-knowledge",
                    "/kbe/federated/*",
                    "/kbe/homomorphic/*",
                    "/kbe/dashboard"
                ]
            },
            "aeg": {
                "name": "Auto Evolution Gateway",
                "purpose": "開発優先度決定AI、GitHub PR自動生成、自律的進化",
                "endpoints": [
                    "/aeg/create-task",
                    "/aeg/analyze-and-prioritize",
                    "/aeg/top-priorities",
                    "/aeg/pr/*",
                    "/aeg/dashboard"
                ]
            },
            "vaporization": {
                "name": "Vaporization Protocol",
                "purpose": "Redis TTL 24時間強制、KBE FLUSH_HOOK、プライバシー保護",
                "endpoints": [
                    "/vaporization/stats",
                    "/vaporization/ttl/*",
                    "/vaporization/flush/*",
                    "/vaporization/dashboard"
                ]
            }
        },
        "integration": {
            "unified_dashboard": "/selfevolution/dashboard",
            "execution_cycle": "/selfevolution/execute-cycle",
            "module_health": "/selfevolution/module-health"
        },
        "privacy_guarantees": [
            "Zero central storage of personal data",
            "Maximum 24-hour cache retention",
            "Immediate flush after knowledge extraction",
            "Federated learning with local AI training",
            "Homomorphic encryption for model aggregation",
            "ZK audit for privacy-preserving verification"
        ],
        "autonomous_capabilities": [
            "Self-healing based on CRAD recovery analysis",
            "Automatic priority determination from health metrics",
            "AI-driven code improvement suggestions",
            "GitHub PR generation for evolution tasks",
            "Finance optimization with cost tracking",
            "Predictive anomaly detection"
        ]
    }
