"""
Governance API Router
AMM/CRAD APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Governance層インポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from governance import autonomous_moderator, context_aware_debugger

router = APIRouter(prefix="/governance", tags=["governance"])


# === Request/Response Models ===

class KMSAccessRequest(BaseModel):
    """KMSアクセスリクエスト"""
    pod_id: str
    operation: str


class KubectlOperationRequest(BaseModel):
    """kubectl操作リクエスト"""
    user: str
    operation: str
    target: str


class AlertRequest(BaseModel):
    """アラートリクエスト"""
    alert_name: str
    alert_data: Dict[str, Any]


# === AMM Endpoints ===

@router.post("/amm/check-kms-access")
async def check_kms_access(request: KMSAccessRequest):
    """
    KMSアクセスチェック
    
    KMS-R-001: アクセス頻度制限（3回/秒）
    KMS-R-002: 営業時間外制御
    """
    try:
        result = autonomous_moderator.check_kms_access(
            request.pod_id,
            request.operation
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/amm/check-kubectl")
async def check_kubectl_operation(request: KubectlOperationRequest):
    """
    kubectl操作チェック
    
    GIT-R-001: GitOps強制（手動操作ブロック）
    """
    try:
        result = autonomous_moderator.check_kubectl_operation(
            request.user,
            request.operation,
            request.target
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/amm/blocked-pods")
async def get_blocked_pods():
    """ブロック中Pod一覧"""
    try:
        return {
            "blocked_pods": autonomous_moderator.get_blocked_pods()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/amm/policy-summary")
async def get_amm_policy_summary():
    """AMMポリシーサマリー"""
    try:
        return autonomous_moderator.get_policy_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === CRAD Endpoints ===

@router.post("/crad/handle-alert")
async def handle_alert(request: AlertRequest):
    """
    アラート処理
    
    リカバリプロトコル自動実行
    MTTRターゲット: 180秒
    """
    try:
        execution = await context_aware_debugger.handle_alert(
            request.alert_name,
            request.alert_data
        )
        return {
            "execution_id": execution.execution_id,
            "alert_name": execution.alert_name,
            "status": execution.status.value,
            "steps_executed": execution.steps_executed,
            "recovery_time_seconds": execution.recovery_time_seconds,
            "result": execution.result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crad/mttr-stats")
async def get_mttr_stats():
    """MTTR統計"""
    try:
        return context_aware_debugger.get_mttr_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crad/summary")
async def get_crad_summary():
    """CRADサマリー"""
    try:
        return context_aware_debugger.get_crad_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Unified Dashboard ===

@router.get("/dashboard")
async def get_governance_dashboard():
    """
    ガバナンス統合ダッシュボード
    
    AMM + CRAD の統合情報
    """
    try:
        return {
            "pcgp_version": "1.0",
            "governance_layer": {
                "amm": {
                    "name": "Autonomous Moderator Module",
                    "status": "active",
                    "summary": autonomous_moderator.get_policy_summary()
                },
                "crad": {
                    "name": "Context-Aware Recovery & Auto Debugger",
                    "status": "active",
                    "summary": context_aware_debugger.get_crad_summary()
                }
            },
            "policies": {
                "security_policy": "policies/security_policy_amm.json",
                "recovery_runbook": "policies/recovery_runbook_crad.json"
            },
            "api_endpoints": {
                "amm": [
                    "POST /governance/amm/check-kms-access",
                    "POST /governance/amm/check-kubectl",
                    "GET /governance/amm/blocked-pods",
                    "GET /governance/amm/policy-summary"
                ],
                "crad": [
                    "POST /governance/crad/handle-alert",
                    "GET /governance/crad/mttr-stats",
                    "GET /governance/crad/summary"
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
