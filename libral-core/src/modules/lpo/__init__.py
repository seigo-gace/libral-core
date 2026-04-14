"""
LPO (Libral Protocol Optimizer)
単体自律監視モジュール

AMM/CRADを統合し、以下の機能を提供：
- ZK監査ゲートウェイ（ゼロ知識証明ベース）
- 自己修復AI（CRAD動的修復提案）
- 財務最適化（AIコスト追跡、プラグイン収益監査）
- RBAC抽象化
- システム健全性スコア（0-100）
- 予測型異常検知
"""

from .core import LPOCore, lpo_core
from .health_score import calculate_health_score
from .zk_audit import ZKAuditGateway
from .self_healing import SelfHealingAI
from .finance import FinanceOptimizer
from .rbac import IRBACProvider
from .predictive import PredictiveMonitor

__all__ = [
    'LPOCore',
    'lpo_core',
    'calculate_health_score',
    'ZKAuditGateway',
    'SelfHealingAI',
    'FinanceOptimizer',
    'IRBACProvider',
    'PredictiveMonitor'
]

__version__ = "1.0.0"
