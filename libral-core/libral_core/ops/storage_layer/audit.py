"""
ストレージ監査ロガー
SAL_OPS_003実装: ストレージ切替の暗号化監査ログ
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import structlog
import json


logger = structlog.get_logger(__name__)


class AuditEventType(str, Enum):
    """監査イベントタイプ"""
    STORAGE_FAILOVER = "storage_failover"
    PROVIDER_SWITCH = "provider_switch"
    ACCESS_ATTEMPT = "access_attempt"
    POLICY_CHANGE = "policy_change"
    ENCRYPTION_APPLIED = "encryption_applied"
    DECRYPTION_APPLIED = "decryption_applied"


@dataclass
class AuditEvent:
    """監査イベント"""
    event_id: str
    event_type: AuditEventType
    timestamp: datetime
    component: str
    user_id: Optional[str]
    details: Dict
    encrypted: bool = True
    
    def to_dict(self) -> Dict:
        """辞書変換"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "component": self.component,
            "user_id": self.user_id,
            "details": self.details,
            "encrypted": self.encrypted
        }


class StorageAuditLogger:
    """ストレージ監査ロガー"""
    
    def __init__(self, encryption_enabled: bool = True):
        self.encryption_enabled = encryption_enabled
        self.audit_trail: List[AuditEvent] = []
        logger.info(
            "audit_logger_initialized",
            encryption_enabled=encryption_enabled
        )
    
    async def log_failover(
        self,
        from_provider: str,
        to_provider: str,
        reason: str,
        success: bool,
        user_id: Optional[str] = None
    ):
        """フェイルオーバーイベント記録"""
        event = AuditEvent(
            event_id=f"failover_{datetime.utcnow().timestamp()}",
            event_type=AuditEventType.STORAGE_FAILOVER,
            timestamp=datetime.utcnow(),
            component="storage_layer",
            user_id=user_id,
            details={
                "from_provider": from_provider,
                "to_provider": to_provider,
                "reason": reason,
                "success": success
            },
            encrypted=self.encryption_enabled
        )
        
        self.audit_trail.append(event)
        
        logger.info(
            "audit_log_failover",
            event_id=event.event_id,
            from_provider=from_provider,
            to_provider=to_provider,
            success=success
        )
    
    async def log_provider_switch(
        self,
        previous_provider: str,
        new_provider: str,
        security_level: str,
        user_id: Optional[str] = None
    ):
        """プロバイダ切替記録"""
        event = AuditEvent(
            event_id=f"switch_{datetime.utcnow().timestamp()}",
            event_type=AuditEventType.PROVIDER_SWITCH,
            timestamp=datetime.utcnow(),
            component="storage_layer",
            user_id=user_id,
            details={
                "previous_provider": previous_provider,
                "new_provider": new_provider,
                "security_level": security_level
            },
            encrypted=self.encryption_enabled
        )
        
        self.audit_trail.append(event)
        
        logger.info(
            "audit_log_switch",
            event_id=event.event_id,
            previous=previous_provider,
            new=new_provider
        )
    
    async def log_access_attempt(
        self,
        key: str,
        operation: str,
        provider: str,
        success: bool,
        user_id: Optional[str] = None
    ):
        """アクセス試行記録"""
        event = AuditEvent(
            event_id=f"access_{datetime.utcnow().timestamp()}",
            event_type=AuditEventType.ACCESS_ATTEMPT,
            timestamp=datetime.utcnow(),
            component="storage_layer",
            user_id=user_id,
            details={
                "key": key,
                "operation": operation,
                "provider": provider,
                "success": success
            },
            encrypted=self.encryption_enabled
        )
        
        self.audit_trail.append(event)
    
    async def log_policy_change(
        self,
        security_level: str,
        old_policy: Dict,
        new_policy: Dict,
        changed_by: Optional[str] = None
    ):
        """ポリシー変更記録"""
        event = AuditEvent(
            event_id=f"policy_{datetime.utcnow().timestamp()}",
            event_type=AuditEventType.POLICY_CHANGE,
            timestamp=datetime.utcnow(),
            component="storage_router",
            user_id=changed_by,
            details={
                "security_level": security_level,
                "old_policy": old_policy,
                "new_policy": new_policy
            },
            encrypted=self.encryption_enabled
        )
        
        self.audit_trail.append(event)
        
        logger.warning(
            "audit_log_policy_change",
            event_id=event.event_id,
            security_level=security_level,
            changed_by=changed_by
        )
    
    async def log_encryption_event(
        self,
        operation: str,
        key: str,
        algorithm: str,
        success: bool,
        user_id: Optional[str] = None
    ):
        """暗号化イベント記録"""
        event_type = (AuditEventType.ENCRYPTION_APPLIED 
                     if operation == "encrypt" 
                     else AuditEventType.DECRYPTION_APPLIED)
        
        event = AuditEvent(
            event_id=f"crypto_{datetime.utcnow().timestamp()}",
            event_type=event_type,
            timestamp=datetime.utcnow(),
            component="crypto_module",
            user_id=user_id,
            details={
                "operation": operation,
                "key": key,
                "algorithm": algorithm,
                "success": success
            },
            encrypted=self.encryption_enabled
        )
        
        self.audit_trail.append(event)
    
    def get_audit_trail(
        self,
        event_type: Optional[AuditEventType] = None,
        limit: int = 100
    ) -> List[Dict]:
        """監査ログ取得"""
        filtered = self.audit_trail
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        
        return [event.to_dict() for event in filtered[-limit:]]
    
    def export_audit_log(self, filepath: str):
        """監査ログエクスポート"""
        audit_data = [event.to_dict() for event in self.audit_trail]
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)
        
        logger.info(
            "audit_log_exported",
            filepath=filepath,
            event_count=len(audit_data)
        )
    
    def get_summary(self) -> Dict:
        """監査サマリー取得"""
        from collections import Counter
        
        event_types = Counter(e.event_type.value for e in self.audit_trail)
        
        return {
            "total_events": len(self.audit_trail),
            "event_types": dict(event_types),
            "earliest_event": (
                self.audit_trail[0].timestamp.isoformat()
                if self.audit_trail else None
            ),
            "latest_event": (
                self.audit_trail[-1].timestamp.isoformat()
                if self.audit_trail else None
            ),
            "encryption_enabled": self.encryption_enabled
        }
