"""
LPO API Router
Libral Protocol Optimizer APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# LPOモジュールインポート
from .core import lpo_core
from .health_score import calculate_health_score
from .zk_audit import zk_audit_gateway
from .self_healing import self_healing_ai
from .finance import finance_optimizer
from .rbac import rbac_provider, Role, Permission
from .predictive import predictive_monitor

router = APIRouter(prefix="/lpo", tags=["lpo"])


# === Request/Response Models ===

class HealthScoreRequest(BaseModel):
    """健全性スコア計算リクエスト"""
    amm_blocked_count: int = 0
    crad_recovery_success_rate: float = 100.0
    system_uptime_percentage: float = 100.0
    avg_response_time_ms: float = 50.0
    error_rate_percentage: float = 0.0


class ZKProofRequest(BaseModel):
    """ZK証明リクエスト"""
    claim_data: str
    secret: str


class ZKVerifyRequest(BaseModel):
    """ZK検証リクエスト"""
    proof_id: str
    claim_data: str
    secret: str


class CostRecordRequest(BaseModel):
    """コスト記録リクエスト"""
    service: str
    cost_usd: float
    tokens_used: int
    record_id: str


class RevenueRecordRequest(BaseModel):
    """収益記録リクエスト"""
    plugin_id: str
    revenue_usd: float
    transaction_count: int
    record_id: str


class UserRegistrationRequest(BaseModel):
    """ユーザー登録リクエスト"""
    user_id: str
    roles: List[str]
    custom_permissions: Optional[List[str]] = None


class PermissionCheckRequest(BaseModel):
    """権限チェックリクエスト"""
    user_id: str
    permission: str


class MetricRecordRequest(BaseModel):
    """メトリクス記録リクエスト"""
    metric_name: str
    value: float


# === Core Endpoints ===

@router.get("/status")
async def get_lpo_status():
    """LPOシステムステータス取得"""
    try:
        return lpo_core.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Health Score Endpoints ===

@router.post("/metrics/health-score")
async def calculate_system_health_score(request: HealthScoreRequest):
    """
    システム健全性スコア計算
    
    0-100のスコアでシステムの健全性を評価
    """
    try:
        result = calculate_health_score(
            amm_blocked_count=request.amm_blocked_count,
            crad_recovery_success_rate=request.crad_recovery_success_rate,
            system_uptime_percentage=request.system_uptime_percentage,
            avg_response_time_ms=request.avg_response_time_ms,
            error_rate_percentage=request.error_rate_percentage
        )
        
        # LPOコアの健全性スコア更新
        lpo_core.update_health_score(result["health_score"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/health-score")
async def get_current_health_score():
    """現在の健全性スコア取得"""
    try:
        return {
            "health_score": lpo_core.status.health_score,
            "last_updated": lpo_core.status.last_check.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === ZK Audit Endpoints ===

@router.post("/zk-audit/create-proof")
async def create_zk_proof(request: ZKProofRequest):
    """ゼロ知識証明作成"""
    try:
        proof = zk_audit_gateway.create_proof(request.claim_data, request.secret)
        return {
            "proof_id": proof.proof_id,
            "claim_hash": proof.claim,
            "created_at": proof.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zk-audit/verify-proof")
async def verify_zk_proof(request: ZKVerifyRequest):
    """ゼロ知識証明検証"""
    try:
        verified = zk_audit_gateway.verify_proof(
            request.proof_id,
            request.claim_data,
            request.secret
        )
        return {
            "proof_id": request.proof_id,
            "verified": verified
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zk-audit/log")
async def get_zk_audit_log():
    """ZK監査ログ取得"""
    try:
        return zk_audit_gateway.get_audit_log()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Self-Healing AI Endpoints ===

@router.get("/self-healing/suggestions")
async def get_healing_suggestions():
    """自己修復AI提案取得"""
    try:
        return self_healing_ai.get_suggestions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/self-healing/summary")
async def get_healing_summary():
    """自己修復AIサマリー"""
    try:
        return self_healing_ai.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Finance Optimizer Endpoints ===

@router.post("/finance/record-cost")
async def record_ai_cost(request: CostRecordRequest):
    """外部AIコスト記録"""
    try:
        result = finance_optimizer.record_ai_cost(
            request.service,
            request.cost_usd,
            request.tokens_used,
            request.record_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/finance/record-revenue")
async def record_plugin_revenue(request: RevenueRecordRequest):
    """プラグイン収益記録"""
    try:
        finance_optimizer.record_plugin_revenue(
            request.plugin_id,
            request.revenue_usd,
            request.transaction_count,
            request.record_id
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/cost-summary")
async def get_cost_summary(days: int = 30):
    """コストサマリー取得"""
    try:
        return finance_optimizer.get_cost_summary(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/finance/revenue-summary")
async def get_revenue_summary(days: int = 30):
    """収益サマリー取得"""
    try:
        return finance_optimizer.get_revenue_summary(days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === RBAC Endpoints ===

@router.post("/rbac/register-user")
async def register_user(request: UserRegistrationRequest):
    """ユーザー登録"""
    try:
        roles = [Role(r) for r in request.roles]
        custom_perms = [Permission(p) for p in request.custom_permissions] if request.custom_permissions else None
        
        rbac_provider.register_user(
            request.user_id,
            roles,
            custom_perms
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rbac/check-permission")
async def check_permission(request: PermissionCheckRequest):
    """権限チェック"""
    try:
        allowed = rbac_provider.check_permission(
            request.user_id,
            Permission(request.permission)
        )
        return {"allowed": allowed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rbac/summary")
async def get_rbac_summary():
    """RBACサマリー"""
    try:
        return rbac_provider.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Predictive Monitor Endpoints ===

@router.post("/predictive/record-metric")
async def record_metric(request: MetricRecordRequest):
    """メトリクス記録と異常検知"""
    try:
        anomaly = predictive_monitor.record_metric(
            request.metric_name,
            request.value
        )
        
        if anomaly:
            return {
                "anomaly_detected": True,
                "detection_id": anomaly.detection_id,
                "severity": anomaly.severity,
                "deviation": round(anomaly.deviation, 2)
            }
        else:
            return {"anomaly_detected": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictive/anomalies")
async def get_recent_anomalies(hours: int = 24):
    """最近の異常検知取得"""
    try:
        return predictive_monitor.get_recent_anomalies(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictive/forecast/{metric_name}")
async def get_metric_forecast(metric_name: str):
    """メトリクス予測"""
    try:
        forecast = predictive_monitor.get_metric_forecast(metric_name)
        if not forecast:
            raise HTTPException(status_code=404, detail="Metric not found or insufficient data")
        return forecast
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predictive/summary")
async def get_predictive_summary():
    """予測監視サマリー"""
    try:
        return predictive_monitor.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Dashboard Endpoint ===

@router.get("/dashboard")
async def get_lpo_dashboard():
    """
    LPO統合ダッシュボード
    
    全機能の統合情報
    """
    try:
        return {
            "lpo_version": "1.0.0",
            "core_status": lpo_core.get_status(),
            "health_score": {
                "current": lpo_core.status.health_score,
                "last_updated": lpo_core.status.last_check.isoformat()
            },
            "zk_audit": zk_audit_gateway.get_audit_log(),
            "self_healing": self_healing_ai.get_summary(),
            "finance": {
                "cost_summary": finance_optimizer.get_cost_summary(30),
                "revenue_summary": finance_optimizer.get_revenue_summary(30)
            },
            "rbac": rbac_provider.get_summary(),
            "predictive": predictive_monitor.get_summary(),
            "api_endpoints": {
                "health_score": "POST /lpo/metrics/health-score, GET /lpo/metrics/health-score",
                "zk_audit": "POST /lpo/zk-audit/create-proof, POST /lpo/zk-audit/verify-proof, GET /lpo/zk-audit/log",
                "self_healing": "GET /lpo/self-healing/suggestions, GET /lpo/self-healing/summary",
                "finance": "POST /lpo/finance/record-cost, POST /lpo/finance/record-revenue, GET /lpo/finance/cost-summary, GET /lpo/finance/revenue-summary",
                "rbac": "POST /lpo/rbac/register-user, POST /lpo/rbac/check-permission, GET /lpo/rbac/summary",
                "predictive": "POST /lpo/predictive/record-metric, GET /lpo/predictive/anomalies, GET /lpo/predictive/forecast/{metric_name}, GET /lpo/predictive/summary"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
