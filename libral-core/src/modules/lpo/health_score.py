"""
Health Score Calculator
システム健全性スコア計算（0-100）
"""

from typing import Dict, Any
from dataclasses import dataclass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


@dataclass
class HealthMetrics:
    """健全性メトリクス"""
    amm_score: float  # AMMセキュリティスコア
    crad_score: float  # CRAD自動復旧スコア
    system_uptime: float  # システム稼働率スコア
    response_time: float  # API応答時間スコア
    error_rate: float  # エラー率スコア


def calculate_health_score(
    amm_blocked_count: int = 0,
    crad_recovery_success_rate: float = 100.0,
    system_uptime_percentage: float = 100.0,
    avg_response_time_ms: float = 50.0,
    error_rate_percentage: float = 0.0
) -> Dict[str, Any]:
    """
    システム健全性スコア計算
    
    Args:
        amm_blocked_count: AMMブロック数
        crad_recovery_success_rate: CRAD復旧成功率（%）
        system_uptime_percentage: システム稼働率（%）
        avg_response_time_ms: 平均応答時間（ms）
        error_rate_percentage: エラー率（%）
    
    Returns:
        健全性スコアと詳細
    """
    
    # AMM スコア計算（ブロック数が少ないほど高スコア）
    # 0ブロック=100, 10ブロック以上=0
    amm_score = max(0.0, 100.0 - (amm_blocked_count * 10.0))
    
    # CRAD スコア（復旧成功率そのまま）
    crad_score = crad_recovery_success_rate
    
    # システム稼働率スコア
    uptime_score = system_uptime_percentage
    
    # 応答時間スコア（50ms以下=100, 500ms以上=0）
    response_score = max(0.0, 100.0 - ((avg_response_time_ms - 50.0) / 4.5))
    
    # エラー率スコア（0%=100, 10%以上=0）
    error_score = max(0.0, 100.0 - (error_rate_percentage * 10.0))
    
    # 重み付け合計（合計100）
    weights = {
        "amm": 0.20,      # 20%
        "crad": 0.25,     # 25%
        "uptime": 0.25,   # 25%
        "response": 0.15, # 15%
        "error": 0.15     # 15%
    }
    
    total_score = (
        amm_score * weights["amm"] +
        crad_score * weights["crad"] +
        uptime_score * weights["uptime"] +
        response_score * weights["response"] +
        error_score * weights["error"]
    )
    
    # スコア判定
    if total_score >= 90:
        status = "excellent"
        message = "システムは最適な状態です"
    elif total_score >= 75:
        status = "good"
        message = "システムは良好な状態です"
    elif total_score >= 60:
        status = "fair"
        message = "システムに改善の余地があります"
    elif total_score >= 40:
        status = "poor"
        message = "システムに問題が発生しています"
    else:
        status = "critical"
        message = "緊急の対応が必要です"
    
    return {
        "health_score": round(total_score, 2),
        "status": status,
        "message": message,
        "breakdown": {
            "amm_security": round(amm_score, 2),
            "crad_recovery": round(crad_score, 2),
            "system_uptime": round(uptime_score, 2),
            "response_time": round(response_score, 2),
            "error_handling": round(error_score, 2)
        },
        "inputs": {
            "amm_blocked_count": amm_blocked_count,
            "crad_recovery_success_rate": crad_recovery_success_rate,
            "system_uptime_percentage": system_uptime_percentage,
            "avg_response_time_ms": avg_response_time_ms,
            "error_rate_percentage": error_rate_percentage
        },
        "timestamp": utc_now().isoformat()
    }
