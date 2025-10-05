"""
RBAC Abstraction
Role-Based Access Control 抽象化プロバイダー

LPOの権限チェックを抽象化し、単体モジュールとしての汎用性を確保
"""

from typing import Dict, Any, List, Optional, Protocol
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


class Permission(str, Enum):
    """権限定義"""
    # LPO権限
    LPO_READ = "lpo:read"
    LPO_WRITE = "lpo:write"
    LPO_ADMIN = "lpo:admin"
    
    # AMM権限
    AMM_CHECK = "amm:check"
    AMM_CONFIGURE = "amm:configure"
    
    # CRAD権限
    CRAD_TRIGGER = "crad:trigger"
    CRAD_CONFIGURE = "crad:configure"
    
    # 財務権限
    FINANCE_READ = "finance:read"
    FINANCE_WRITE = "finance:write"


class Role(str, Enum):
    """ロール定義"""
    SYSTEM_ADMIN = "system_admin"
    SECURITY_OPERATOR = "security_operator"
    DEVELOPER = "developer"
    VIEWER = "viewer"


@dataclass
class User:
    """ユーザー"""
    user_id: str
    roles: List[Role]
    custom_permissions: List[Permission]


class IRBACProvider(Protocol):
    """RBAC Provider インターフェース"""
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """権限チェック"""
        ...
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """ユーザー権限取得"""
        ...


class LPORBACProvider:
    """
    LPO RBAC Provider
    
    ロールベースアクセスコントロール実装
    """
    
    # ロールと権限のマッピング
    ROLE_PERMISSIONS: Dict[Role, List[Permission]] = {
        Role.SYSTEM_ADMIN: [
            Permission.LPO_READ,
            Permission.LPO_WRITE,
            Permission.LPO_ADMIN,
            Permission.AMM_CHECK,
            Permission.AMM_CONFIGURE,
            Permission.CRAD_TRIGGER,
            Permission.CRAD_CONFIGURE,
            Permission.FINANCE_READ,
            Permission.FINANCE_WRITE,
        ],
        Role.SECURITY_OPERATOR: [
            Permission.LPO_READ,
            Permission.AMM_CHECK,
            Permission.AMM_CONFIGURE,
            Permission.CRAD_TRIGGER,
            Permission.FINANCE_READ,
        ],
        Role.DEVELOPER: [
            Permission.LPO_READ,
            Permission.AMM_CHECK,
            Permission.CRAD_TRIGGER,
            Permission.FINANCE_READ,
        ],
        Role.VIEWER: [
            Permission.LPO_READ,
            Permission.FINANCE_READ,
        ]
    }
    
    def __init__(self):
        self.users: Dict[str, User] = {}
    
    def register_user(self, user_id: str, roles: List[Role], custom_permissions: Optional[List[Permission]] = None):
        """ユーザー登録"""
        self.users[user_id] = User(
            user_id=user_id,
            roles=roles,
            custom_permissions=custom_permissions or []
        )
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        権限チェック
        
        Args:
            user_id: ユーザーID
            permission: チェック対象権限
        
        Returns:
            権限があればTrue
        """
        user = self.users.get(user_id)
        if not user:
            return False
        
        # カスタム権限チェック
        if permission in user.custom_permissions:
            return True
        
        # ロールベース権限チェック
        for role in user.roles:
            if permission in self.ROLE_PERMISSIONS.get(role, []):
                return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        ユーザー権限取得
        
        Args:
            user_id: ユーザーID
        
        Returns:
            権限リスト
        """
        user = self.users.get(user_id)
        if not user:
            return []
        
        permissions = set(user.custom_permissions)
        
        for role in user.roles:
            permissions.update(self.ROLE_PERMISSIONS.get(role, []))
        
        return list(permissions)
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "total_users": len(self.users),
            "users": [
                {
                    "user_id": user.user_id,
                    "roles": [r.value for r in user.roles],
                    "total_permissions": len(self.get_user_permissions(user.user_id))
                }
                for user in self.users.values()
            ]
        }


# グローバルインスタンス
rbac_provider = LPORBACProvider()
