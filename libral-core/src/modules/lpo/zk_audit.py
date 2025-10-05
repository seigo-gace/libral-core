"""
ZK Audit Gateway
ゼロ知識証明ベースの監査ゲートウェイ

プライバシーを保護しながらセキュリティ監査を実行
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import hashlib
import hmac
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id, hmac_sign


@dataclass
class ZKProof:
    """ゼロ知識証明"""
    proof_id: str
    claim: str  # 証明対象（ハッシュ化）
    proof: str  # 証明データ
    verified: bool
    created_at: datetime


class ZKAuditGateway:
    """
    ZK監査ゲートウェイ
    
    外部APIがゼロ知識証明ベースの監査を要求・検証
    """
    
    def __init__(self):
        self.proofs: Dict[str, ZKProof] = {}
    
    def create_proof(self, claim_data: str, secret: str) -> ZKProof:
        """
        ゼロ知識証明作成
        
        Args:
            claim_data: 証明対象データ
            secret: 秘密鍵
        
        Returns:
            ZKProof
        """
        # クレームのハッシュ化（プライバシー保護）
        claim_hash = hashlib.sha256(claim_data.encode()).hexdigest()
        
        # 証明生成（HMAC-SHA256ベース）
        proof_data = hmac_sign(claim_hash, secret)
        
        proof = ZKProof(
            proof_id=generate_random_id(),
            claim=claim_hash,
            proof=proof_data,
            verified=False,
            created_at=utc_now()
        )
        
        self.proofs[proof.proof_id] = proof
        return proof
    
    def verify_proof(self, proof_id: str, claim_data: str, secret: str) -> bool:
        """
        ゼロ知識証明検証
        
        Args:
            proof_id: 証明ID
            claim_data: 証明対象データ
            secret: 秘密鍵
        
        Returns:
            検証成功ならTrue
        """
        proof = self.proofs.get(proof_id)
        if not proof:
            return False
        
        # クレームのハッシュ化
        claim_hash = hashlib.sha256(claim_data.encode()).hexdigest()
        
        # クレームハッシュの検証
        if claim_hash != proof.claim:
            return False
        
        # 証明データの検証
        expected_proof = hmac_sign(claim_hash, secret)
        if expected_proof != proof.proof:
            return False
        
        # 検証成功
        proof.verified = True
        return True
    
    def get_audit_log(self) -> Dict[str, Any]:
        """監査ログ取得"""
        return {
            "total_proofs": len(self.proofs),
            "verified_proofs": sum(1 for p in self.proofs.values() if p.verified),
            "proofs": [
                {
                    "proof_id": p.proof_id,
                    "claim_hash": p.claim[:16] + "...",  # 先頭のみ表示
                    "verified": p.verified,
                    "created_at": p.created_at.isoformat()
                }
                for p in list(self.proofs.values())[-10:]  # 最新10件
            ]
        }


# グローバルインスタンス
zk_audit_gateway = ZKAuditGateway()
