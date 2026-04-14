"""
Autonomous Moderator Module (AMM)
自律モデレーター - セキュリティポリシー自動執行

KMSアクセス制御とGitOps操作ブロックを自動実行
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Component層インポート
sys.path.insert(0, str(Path(__file__).parent.parent))
from library.components import config_loader, utc_now, is_business_hours


class SecurityDomain(Enum):
    """セキュリティドメイン"""
    KMS_ACCESS = "KMS_ACCESS"
    GIT_POLICY = "GIT_POLICY"


class ActionType(Enum):
    """アクション種別"""
    BLOCK_ACCESS_FOR_30M = "BLOCK_ACCESS_FOR_30M"
    REQUIRE_2FA_REAUTH = "REQUIRE_2FA_REAUTH"
    LOG_AND_BLOCK = "LOG_AND_BLOCK"


@dataclass
class SecurityRule:
    """セキュリティルール"""
    rule_id: str
    domain: SecurityDomain
    metric: Optional[str]
    condition: Optional[str]
    threshold: Optional[float]
    action: ActionType
    severity: str
    description: str


@dataclass
class AccessBlock:
    """アクセスブロック記録"""
    pod_id: str
    blocked_at: datetime
    blocked_until: datetime
    reason: str
    rule_id: str


class AutonomousModerator:
    """自律モデレーター"""
    
    def __init__(self):
        """初期化"""
        # ポリシーファイル読み込み
        self.policy = config_loader.load_policy("security_policy_amm")
        self.rules = self._parse_rules()
        
        # アクセス追跡
        self.kms_access_log: Dict[str, List[datetime]] = {}
        self.blocked_pods: List[AccessBlock] = []
        
        # GitOps設定
        self.manual_ops_blocked = True
    
    def _parse_rules(self) -> List[SecurityRule]:
        """ルール解析"""
        rules = []
        
        for domain_data in self.policy["security_domains"]:
            domain = SecurityDomain(domain_data["domain"])
            
            for rule_data in domain_data["rules"]:
                rule = SecurityRule(
                    rule_id=rule_data["rule_id"],
                    domain=domain,
                    metric=rule_data.get("metric"),
                    condition=rule_data.get("condition"),
                    threshold=rule_data.get("threshold"),
                    action=ActionType(rule_data["action"]),
                    severity=rule_data["severity"],
                    description=rule_data["description"]
                )
                rules.append(rule)
        
        return rules
    
    def check_kms_access(self, pod_id: str, operation: str) -> Dict[str, Any]:
        """
        KMSアクセスチェック
        
        Args:
            pod_id: Pod ID
            operation: 操作種別
        
        Returns:
            チェック結果
        """
        now = utc_now()
        
        # KMS-R-001: アクセス頻度チェック（3回/秒制限）
        if pod_id not in self.kms_access_log:
            self.kms_access_log[pod_id] = []
        
        # 過去1秒のアクセスをカウント
        one_second_ago = now - timedelta(seconds=1)
        recent_accesses = [
            t for t in self.kms_access_log[pod_id]
            if t > one_second_ago
        ]
        
        if len(recent_accesses) >= 3:
            # 30分間ブロック
            block = AccessBlock(
                pod_id=pod_id,
                blocked_at=now,
                blocked_until=now + timedelta(minutes=30),
                reason="KMSアクセス頻度超過（3回/秒）",
                rule_id="KMS-R-001"
            )
            self.blocked_pods.append(block)
            
            return {
                "allowed": False,
                "reason": "アクセス頻度超過",
                "blocked_until": block.blocked_until.isoformat(),
                "rule_id": "KMS-R-001",
                "severity": "CRITICAL"
            }
        
        # KMS-R-002: 営業時間外チェック
        if not is_business_hours(now):
            return {
                "allowed": False,
                "reason": "営業時間外（UTC 22:00-07:00）",
                "action_required": "2FA再認証が必要",
                "rule_id": "KMS-R-002",
                "severity": "HIGH"
            }
        
        # アクセス記録
        self.kms_access_log[pod_id].append(now)
        
        # 古い記録を削除（メモリ節約）
        self.kms_access_log[pod_id] = [
            t for t in self.kms_access_log[pod_id]
            if t > now - timedelta(hours=1)
        ]
        
        return {
            "allowed": True,
            "pod_id": pod_id,
            "operation": operation,
            "timestamp": now.isoformat()
        }
    
    def check_kubectl_operation(self, user: str, operation: str, target: str) -> Dict[str, Any]:
        """
        kubectl操作チェック（GIT-R-001）
        
        Args:
            user: ユーザー名
            operation: 操作（exec/delete/apply）
            target: 対象リソース
        
        Returns:
            チェック結果
        """
        blocked_ops = ["exec", "delete", "apply"]
        
        if self.manual_ops_blocked and operation in blocked_ops:
            return {
                "allowed": False,
                "reason": "GitOpsが有効な場合、手動kubectl操作はブロックされます",
                "rule_id": "GIT-R-001",
                "severity": "CRITICAL",
                "user": user,
                "operation": operation,
                "target": target,
                "logged": True
            }
        
        return {
            "allowed": True,
            "user": user,
            "operation": operation,
            "target": target
        }
    
    def get_blocked_pods(self) -> List[Dict[str, Any]]:
        """ブロックされたPod一覧"""
        now = utc_now()
        
        # 有効なブロックのみ
        active_blocks = [
            b for b in self.blocked_pods
            if b.blocked_until > now
        ]
        
        return [
            {
                "pod_id": b.pod_id,
                "blocked_at": b.blocked_at.isoformat(),
                "blocked_until": b.blocked_until.isoformat(),
                "reason": b.reason,
                "rule_id": b.rule_id
            }
            for b in active_blocks
        ]
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """ポリシーサマリー"""
        return {
            "policy_name": self.policy["policy_name"],
            "policy_version": self.policy["policy_version"],
            "total_rules": len(self.rules),
            "rules_by_domain": {
                "KMS_ACCESS": len([r for r in self.rules if r.domain == SecurityDomain.KMS_ACCESS]),
                "GIT_POLICY": len([r for r in self.rules if r.domain == SecurityDomain.GIT_POLICY])
            },
            "manual_ops_blocked": self.manual_ops_blocked,
            "active_blocks": len(self.get_blocked_pods())
        }


# グローバルインスタンス
autonomous_moderator = AutonomousModerator()
