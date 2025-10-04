"""
暗号モジュール検証システム
CCA_OPS_002実装: 監査済み暗号モジュール強制利用チェック
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum
import structlog
import os


logger = structlog.get_logger(__name__)


class ValidationStatus(str, Enum):
    """検証ステータス"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class CryptoModule(str, Enum):
    """暗号モジュール"""
    GPG_CORE = "gpg_core"
    CONTEXT_LOCK = "context_lock"
    STORAGE_ENCRYPTION = "storage_encryption"
    TRANSPORT_TLS = "transport_tls"


@dataclass
class ValidationResult:
    """検証結果"""
    module: str
    status: ValidationStatus
    message: str
    details: Dict
    certified_module_used: bool
    uncertified_calls: List[str]
    
    def to_dict(self) -> Dict:
        """辞書変換"""
        return {
            "module": self.module,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "certified_module_used": self.certified_module_used,
            "uncertified_calls": self.uncertified_calls
        }


class CryptoValidator:
    """暗号モジュール検証器"""
    
    def __init__(self):
        self.certified_modules = {
            "certified_crypto_core.py",
            "aegis_pgp_core.py",
            "fips_validated_crypto.py"
        }
        
        self.approved_algorithms = {
            "AES-256-OCB",
            "AES-256-GCM",
            "ChaCha20-Poly1305",
            "SHA-512",
            "Ed25519",
            "RSA-4096"
        }
        
        self.validation_history: List[ValidationResult] = []
        logger.info("crypto_validator_initialized")
    
    async def validate_gpg_module(self, module_path: str) -> ValidationResult:
        """GPGモジュール検証"""
        uncertified_calls = []
        certified_used = False
        
        try:
            # モジュールファイル読み取り（実装例）
            if os.path.exists(module_path):
                with open(module_path, 'r') as f:
                    content = f.read()
                    
                    # certified_crypto_core.pyの呼び出しチェック
                    if "certified_crypto_core" in content or "aegis_pgp_core" in content:
                        certified_used = True
                    
                    # 未監査モジュールチェック
                    dangerous_imports = [
                        "from Crypto.Cipher import",
                        "import pycrypto",
                        "from cryptography.hazmat"  # 直接使用は非推奨
                    ]
                    
                    for dangerous in dangerous_imports:
                        if dangerous in content:
                            uncertified_calls.append(dangerous)
            
            if not certified_used:
                status = ValidationStatus.FAILED
                message = "Certified crypto module not used"
            elif uncertified_calls:
                status = ValidationStatus.WARNING
                message = f"Found {len(uncertified_calls)} uncertified calls"
            else:
                status = ValidationStatus.PASSED
                message = "Module validation passed"
            
        except Exception as e:
            status = ValidationStatus.FAILED
            message = f"Validation error: {str(e)}"
            logger.error("crypto_validation_failed", module=module_path, error=str(e))
        
        result = ValidationResult(
            module=module_path,
            status=status,
            message=message,
            details={
                "certified_modules_found": certified_used,
                "uncertified_call_count": len(uncertified_calls)
            },
            certified_module_used=certified_used,
            uncertified_calls=uncertified_calls
        )
        
        self.validation_history.append(result)
        
        logger.info(
            "crypto_module_validated",
            module=module_path,
            status=status.value,
            certified_used=certified_used
        )
        
        return result
    
    async def validate_algorithm_usage(
        self,
        module_name: str,
        algorithms_used: List[str]
    ) -> ValidationResult:
        """アルゴリズム使用検証"""
        unapproved_algorithms = [
            algo for algo in algorithms_used
            if algo not in self.approved_algorithms
        ]
        
        if not unapproved_algorithms:
            status = ValidationStatus.PASSED
            message = "All algorithms approved"
        else:
            status = ValidationStatus.FAILED
            message = f"Unapproved algorithms detected: {', '.join(unapproved_algorithms)}"
        
        result = ValidationResult(
            module=module_name,
            status=status,
            message=message,
            details={
                "algorithms_used": algorithms_used,
                "unapproved_algorithms": unapproved_algorithms,
                "approved_count": len(algorithms_used) - len(unapproved_algorithms)
            },
            certified_module_used=len(unapproved_algorithms) == 0,
            uncertified_calls=unapproved_algorithms
        )
        
        self.validation_history.append(result)
        
        logger.info(
            "algorithm_usage_validated",
            module=module_name,
            status=status.value,
            approved_count=len(algorithms_used) - len(unapproved_algorithms)
        )
        
        return result
    
    async def validate_all_crypto_modules(
        self,
        module_paths: List[str]
    ) -> Dict[str, ValidationResult]:
        """全暗号モジュール検証"""
        results = {}
        for path in module_paths:
            result = await self.validate_gpg_module(path)
            results[path] = result
        
        return results
    
    def get_validation_summary(self) -> Dict:
        """検証サマリー"""
        total = len(self.validation_history)
        passed = sum(1 for r in self.validation_history if r.status == ValidationStatus.PASSED)
        failed = sum(1 for r in self.validation_history if r.status == ValidationStatus.FAILED)
        warnings = sum(1 for r in self.validation_history if r.status == ValidationStatus.WARNING)
        
        return {
            "total_validations": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "pass_rate": passed / total if total > 0 else 0,
            "recent_validations": [
                r.to_dict() for r in self.validation_history[-10:]
            ]
        }
    
    def is_certified_module(self, module_name: str) -> bool:
        """認証済みモジュールチェック"""
        return module_name in self.certified_modules
    
    def is_approved_algorithm(self, algorithm: str) -> bool:
        """承認済みアルゴリズムチェック"""
        return algorithm in self.approved_algorithms
    
    def add_certified_module(self, module_name: str):
        """認証済みモジュール追加"""
        self.certified_modules.add(module_name)
        logger.info("certified_module_added", module=module_name)
    
    def add_approved_algorithm(self, algorithm: str):
        """承認済みアルゴリズム追加"""
        self.approved_algorithms.add(algorithm)
        logger.info("approved_algorithm_added", algorithm=algorithm)
