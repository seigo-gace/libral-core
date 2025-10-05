"""
Finance Optimizer
財務最適化 - 外部AIコスト追跡とプラグイン収益監査
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


@dataclass
class CostRecord:
    """コスト記録"""
    record_id: str
    service: str  # "openai", "anthropic", etc.
    cost_usd: Decimal
    tokens_used: int
    timestamp: datetime


@dataclass
class RevenueRecord:
    """収益記録"""
    record_id: str
    plugin_id: str
    revenue_usd: Decimal
    transaction_count: int
    timestamp: datetime


class FinanceOptimizer:
    """
    財務最適化
    
    外部AIコスト追跡、プラグイン収益監査、予測コスト制限
    """
    
    def __init__(self):
        self.cost_records: List[CostRecord] = []
        self.revenue_records: List[RevenueRecord] = []
        self.cost_limit_usd = Decimal("100.0")  # デフォルト制限
        self.alert_threshold = 0.8  # 80%でアラート
    
    def record_ai_cost(self, service: str, cost_usd: float, tokens_used: int, record_id: str):
        """
        外部AIコスト記録
        
        Args:
            service: サービス名（"openai", "anthropic"等）
            cost_usd: コスト（USD）
            tokens_used: 使用トークン数
            record_id: 記録ID
        """
        record = CostRecord(
            record_id=record_id,
            service=service,
            cost_usd=Decimal(str(cost_usd)),
            tokens_used=tokens_used,
            timestamp=utc_now()
        )
        self.cost_records.append(record)
        
        # 100件を超えたら古いものを削除
        if len(self.cost_records) > 100:
            self.cost_records = self.cost_records[-100:]
        
        # コスト制限チェック
        return self._check_cost_limit()
    
    def record_plugin_revenue(self, plugin_id: str, revenue_usd: float, transaction_count: int, record_id: str):
        """
        プラグイン収益記録
        
        Args:
            plugin_id: プラグインID
            revenue_usd: 収益（USD）
            transaction_count: 取引数
            record_id: 記録ID
        """
        record = RevenueRecord(
            record_id=record_id,
            plugin_id=plugin_id,
            revenue_usd=Decimal(str(revenue_usd)),
            transaction_count=transaction_count,
            timestamp=utc_now()
        )
        self.revenue_records.append(record)
        
        if len(self.revenue_records) > 100:
            self.revenue_records = self.revenue_records[-100:]
    
    def _check_cost_limit(self) -> Dict[str, Any]:
        """コスト制限チェック"""
        # 過去30日間のコスト集計
        thirty_days_ago = utc_now() - timedelta(days=30)
        recent_costs = [
            r for r in self.cost_records 
            if r.timestamp >= thirty_days_ago
        ]
        
        total_cost = sum(r.cost_usd for r in recent_costs)
        usage_ratio = float(total_cost / self.cost_limit_usd)
        
        alert = False
        message = ""
        
        if usage_ratio >= 1.0:
            alert = True
            message = f"コスト制限超過: ${total_cost:.2f} / ${self.cost_limit_usd:.2f}"
        elif usage_ratio >= self.alert_threshold:
            alert = True
            message = f"コスト警告: ${total_cost:.2f} / ${self.cost_limit_usd:.2f} ({usage_ratio*100:.1f}%)"
        
        return {
            "alert": alert,
            "message": message,
            "total_cost_usd": float(total_cost),
            "cost_limit_usd": float(self.cost_limit_usd),
            "usage_ratio": round(usage_ratio, 2)
        }
    
    def get_cost_summary(self, days: int = 30) -> Dict[str, Any]:
        """コストサマリー取得"""
        cutoff = utc_now() - timedelta(days=days)
        recent_costs = [r for r in self.cost_records if r.timestamp >= cutoff]
        
        # サービス別集計
        by_service: Dict[str, Dict[str, Any]] = {}
        for record in recent_costs:
            if record.service not in by_service:
                by_service[record.service] = {
                    "cost_usd": Decimal("0"),
                    "tokens_used": 0,
                    "count": 0
                }
            by_service[record.service]["cost_usd"] += record.cost_usd
            by_service[record.service]["tokens_used"] += record.tokens_used
            by_service[record.service]["count"] += 1
        
        total_cost = sum(r.cost_usd for r in recent_costs)
        total_tokens = sum(r.tokens_used for r in recent_costs)
        
        return {
            "period_days": days,
            "total_cost_usd": float(total_cost),
            "total_tokens_used": total_tokens,
            "by_service": {
                service: {
                    "cost_usd": float(data["cost_usd"]),
                    "tokens_used": data["tokens_used"],
                    "api_calls": data["count"]
                }
                for service, data in by_service.items()
            },
            "cost_limit_status": self._check_cost_limit()
        }
    
    def get_revenue_summary(self, days: int = 30) -> Dict[str, Any]:
        """収益サマリー取得"""
        cutoff = utc_now() - timedelta(days=days)
        recent_revenue = [r for r in self.revenue_records if r.timestamp >= cutoff]
        
        # プラグイン別集計
        by_plugin: Dict[str, Dict[str, Any]] = {}
        for record in recent_revenue:
            if record.plugin_id not in by_plugin:
                by_plugin[record.plugin_id] = {
                    "revenue_usd": Decimal("0"),
                    "transactions": 0
                }
            by_plugin[record.plugin_id]["revenue_usd"] += record.revenue_usd
            by_plugin[record.plugin_id]["transactions"] += record.transaction_count
        
        total_revenue = sum(r.revenue_usd for r in recent_revenue)
        total_transactions = sum(r.transaction_count for r in recent_revenue)
        
        return {
            "period_days": days,
            "total_revenue_usd": float(total_revenue),
            "total_transactions": total_transactions,
            "by_plugin": {
                plugin_id: {
                    "revenue_usd": float(data["revenue_usd"]),
                    "transactions": data["transactions"]
                }
                for plugin_id, data in by_plugin.items()
            }
        }


# グローバルインスタンス
finance_optimizer = FinanceOptimizer()
