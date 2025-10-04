"""
証明書管理システム
CCA_OPS_001実装: 監査証明書管理と有効期限監視
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import structlog


logger = structlog.get_logger(__name__)


class CertificateType(str, Enum):
    """証明書タイプ"""
    FIPS_140_3 = "fips_140_3"
    ISO_27001 = "iso_27001"
    SOC2_TYPE2 = "soc2_type2"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"


class CertificateStatus(str, Enum):
    """証明書ステータス"""
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"  # 30日以内
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class Certificate:
    """証明書"""
    cert_id: str
    name: str
    cert_type: CertificateType
    issuer: str
    issue_date: datetime
    expiry_date: datetime
    file_path: Optional[str] = None
    metadata: Dict = None
    
    @property
    def days_until_expiry(self) -> int:
        """有効期限までの日数"""
        delta = self.expiry_date - datetime.utcnow()
        return max(0, delta.days)
    
    @property
    def status(self) -> CertificateStatus:
        """ステータス"""
        days = self.days_until_expiry
        if days <= 0:
            return CertificateStatus.EXPIRED
        elif days <= 30:
            return CertificateStatus.EXPIRING_SOON
        else:
            return CertificateStatus.VALID
    
    @property
    def is_valid(self) -> bool:
        """有効性"""
        return self.status == CertificateStatus.VALID or self.status == CertificateStatus.EXPIRING_SOON
    
    def to_dict(self) -> Dict:
        """辞書変換"""
        return {
            "cert_id": self.cert_id,
            "name": self.name,
            "cert_type": self.cert_type.value,
            "issuer": self.issuer,
            "issue_date": self.issue_date.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "days_until_expiry": self.days_until_expiry,
            "status": self.status.value,
            "is_valid": self.is_valid,
            "file_path": self.file_path,
            "metadata": self.metadata or {}
        }


class CertificateManager:
    """証明書マネージャー"""
    
    def __init__(self):
        self.certificates: Dict[str, Certificate] = {}
        self._initialize_default_certificates()
        logger.info("certificate_manager_initialized")
    
    def _initialize_default_certificates(self):
        """デフォルト証明書初期化"""
        now = datetime.utcnow()
        
        # FIPS 140-3証明書（サンプル）
        self.add_certificate(Certificate(
            cert_id="fips_140_3_aegis_pgp",
            name="FIPS 140-3 Validation - Aegis PGP Core",
            cert_type=CertificateType.FIPS_140_3,
            issuer="NIST/CMVP",
            issue_date=now - timedelta(days=365),
            expiry_date=now + timedelta(days=730),
            file_path="/certs/fips-140-3-aegis-pgp.pdf",
            metadata={
                "certificate_number": "#4567",
                "algorithm_coverage": "AES-256-OCB, SHA-512, Ed25519",
                "validation_level": "Level 1"
            }
        ))
        
        # ISO/IEC 27001証明書（サンプル）
        self.add_certificate(Certificate(
            cert_id="iso_27001_libral",
            name="ISO/IEC 27001:2022 - Libral Core",
            cert_type=CertificateType.ISO_27001,
            issuer="BSI Group",
            issue_date=now - timedelta(days=180),
            expiry_date=now + timedelta(days=1095),  # 3年
            file_path="/certs/iso-27001-libral.pdf",
            metadata={
                "scope": "Information Security Management System",
                "audit_date": (now - timedelta(days=90)).isoformat()
            }
        ))
        
        # SOC 2 Type II証明書（サンプル）
        self.add_certificate(Certificate(
            cert_id="soc2_type2_libral",
            name="SOC 2 Type II - Libral Platform",
            cert_type=CertificateType.SOC2_TYPE2,
            issuer="Deloitte & Touche",
            issue_date=now - timedelta(days=90),
            expiry_date=now + timedelta(days=275),  # 1年 - 90日
            file_path="/certs/soc2-type2-libral.pdf",
            metadata={
                "report_period": "12 months",
                "trust_services_criteria": ["Security", "Availability", "Confidentiality"]
            }
        ))
    
    def add_certificate(self, certificate: Certificate):
        """証明書追加"""
        self.certificates[certificate.cert_id] = certificate
        logger.info(
            "certificate_added",
            cert_id=certificate.cert_id,
            name=certificate.name,
            expiry_date=certificate.expiry_date.isoformat()
        )
    
    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        """証明書取得"""
        return self.certificates.get(cert_id)
    
    def get_all_certificates(self) -> List[Certificate]:
        """全証明書取得"""
        return list(self.certificates.values())
    
    def get_expiring_certificates(self, days_threshold: int = 30) -> List[Certificate]:
        """有効期限切れ間近の証明書取得"""
        return [
            cert for cert in self.certificates.values()
            if 0 < cert.days_until_expiry <= days_threshold
        ]
    
    def get_expired_certificates(self) -> List[Certificate]:
        """有効期限切れ証明書取得"""
        return [
            cert for cert in self.certificates.values()
            if cert.status == CertificateStatus.EXPIRED
        ]
    
    def get_valid_certificates(self) -> List[Certificate]:
        """有効な証明書取得"""
        return [
            cert for cert in self.certificates.values()
            if cert.is_valid
        ]
    
    def check_all_certificates(self) -> Dict:
        """全証明書チェック"""
        return {
            "total": len(self.certificates),
            "valid": len(self.get_valid_certificates()),
            "expiring_soon": len(self.get_expiring_certificates()),
            "expired": len(self.get_expired_certificates()),
            "certificates": [cert.to_dict() for cert in self.get_all_certificates()]
        }
    
    def get_certificate_summary(self) -> Dict:
        """証明書サマリー"""
        certs_by_type = {}
        for cert in self.certificates.values():
            cert_type = cert.cert_type.value
            if cert_type not in certs_by_type:
                certs_by_type[cert_type] = []
            certs_by_type[cert_type].append({
                "name": cert.name,
                "status": cert.status.value,
                "days_until_expiry": cert.days_until_expiry
            })
        
        return {
            "total_certificates": len(self.certificates),
            "valid_count": len(self.get_valid_certificates()),
            "expiring_soon_count": len(self.get_expiring_certificates()),
            "expired_count": len(self.get_expired_certificates()),
            "by_type": certs_by_type
        }
    
    def update_certificate_expiry(self, cert_id: str, new_expiry_date: datetime):
        """証明書有効期限更新"""
        cert = self.get_certificate(cert_id)
        if cert:
            old_expiry = cert.expiry_date
            cert.expiry_date = new_expiry_date
            logger.info(
                "certificate_expiry_updated",
                cert_id=cert_id,
                old_expiry=old_expiry.isoformat(),
                new_expiry=new_expiry_date.isoformat()
            )
        else:
            logger.warning("certificate_not_found", cert_id=cert_id)
