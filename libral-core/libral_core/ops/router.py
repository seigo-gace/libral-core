"""
OPS API Router
運用自動化APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional, List
from pydantic import BaseModel
import structlog

from .monitoring.metrics import metrics_registry, PrometheusExporter
from .monitoring.alerting import AlertManager, AlertSeverity, AlertChannel
from .monitoring.health import HealthChecker
from .storage_layer.manager import StorageAbstractionLayer
from .storage_layer.provider import StorageSecurityLevel
from .security.certificates import CertificateManager
from .security.crypto_validator import CryptoValidator
from .security.kms_manager import KMSManager
from .k8s.gitops import GitOpsManager
from .k8s.chaos import ChaosEngineeringManager, ExperimentType
from .k8s.ha_drp import HADRPManager
from .k8s.vulnerability import VulnerabilityScanner


logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/ops", tags=["ops"])

# 初期化
storage_layer = StorageAbstractionLayer()
cert_manager = CertificateManager()
crypto_validator = CryptoValidator()
kms_manager = KMSManager()
gitops_manager = GitOpsManager()
chaos_manager = ChaosEngineeringManager()
ha_drp_manager = HADRPManager()
vuln_scanner = VulnerabilityScanner()
health_checker = HealthChecker()


class StoreRequest(BaseModel):
    """ストレージ保存リクエスト"""
    key: str
    data: str
    security_level: str = "standard"
    user_id: Optional[str] = None


class RetrieveRequest(BaseModel):
    """ストレージ取得リクエスト"""
    key: str
    security_level: str = "standard"
    user_id: Optional[str] = None


# ========== Prometheus Metrics ==========

@router.get("/metrics")
async def get_prometheus_metrics():
    """Prometheusメトリクス取得"""
    return PrometheusExporter.get_metrics_text()


@router.get("/metrics/summary")
async def get_metrics_summary() -> Dict:
    """メトリクスサマリー"""
    return storage_layer.get_metrics_summary()


# ========== Health Checks ==========

@router.get("/health")
async def get_health_status() -> Dict:
    """ヘルスステータス"""
    await health_checker.check_database()
    await health_checker.check_redis()
    await health_checker.check_crypto_module()
    
    return health_checker.get_health_report()


@router.get("/health/storage")
async def get_storage_health() -> Dict:
    """ストレージヘルスチェック"""
    return await storage_layer.health_check_all()


# ========== Storage Abstraction Layer ==========

@router.post("/storage/store")
async def store_data(request: StoreRequest) -> Dict:
    """データ保存"""
    try:
        security_level = StorageSecurityLevel(request.security_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid security level")
    
    data_bytes = request.data.encode('utf-8')
    success = await storage_layer.store(
        request.key,
        data_bytes,
        security_level,
        request.user_id
    )
    
    return {
        "success": success,
        "key": request.key,
        "security_level": security_level.value
    }


@router.post("/storage/retrieve")
async def retrieve_data(request: RetrieveRequest) -> Dict:
    """データ取得"""
    try:
        security_level = StorageSecurityLevel(request.security_level)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid security level")
    
    data = await storage_layer.retrieve(
        request.key,
        security_level,
        request.user_id
    )
    
    if data is None:
        raise HTTPException(status_code=404, detail="Data not found")
    
    return {
        "key": request.key,
        "data": data.decode('utf-8') if data else None,
        "security_level": security_level.value
    }


@router.get("/storage/audit")
async def get_storage_audit() -> Dict:
    """ストレージ監査ログ"""
    return storage_layer.get_audit_summary()


# ========== Certificate Management ==========

@router.get("/certificates")
async def get_certificates() -> Dict:
    """証明書一覧"""
    return cert_manager.check_all_certificates()


@router.get("/certificates/summary")
async def get_certificate_summary() -> Dict:
    """証明書サマリー"""
    return cert_manager.get_certificate_summary()


@router.get("/certificates/expiring")
async def get_expiring_certificates(days: int = 30) -> Dict:
    """期限切れ間近の証明書"""
    certs = cert_manager.get_expiring_certificates(days)
    return {
        "count": len(certs),
        "certificates": [c.to_dict() for c in certs]
    }


# ========== Crypto Validation ==========

@router.get("/crypto/validation/summary")
async def get_crypto_validation_summary() -> Dict:
    """暗号検証サマリー"""
    return crypto_validator.get_validation_summary()


@router.post("/crypto/validate/module")
async def validate_crypto_module(module_path: str) -> Dict:
    """暗号モジュール検証"""
    result = await crypto_validator.validate_gpg_module(module_path)
    return result.to_dict()


# ========== KMS Management ==========

@router.get("/kms/summary")
async def get_kms_summary() -> Dict:
    """KMSサマリー"""
    return kms_manager.get_kms_summary()


@router.get("/kms/keys/{key_id}")
async def get_key_info(key_id: str) -> Dict:
    """鍵情報取得"""
    key = kms_manager.get_key(key_id)
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    return key.to_dict()


# ========== GitOps ==========

@router.get("/gitops/deployments")
async def get_deployments(limit: int = 10) -> Dict:
    """デプロイメント履歴"""
    deployments = gitops_manager.get_recent_deployments(limit)
    return {
        "count": len(deployments),
        "deployments": [d.to_dict() for d in deployments]
    }


@router.get("/gitops/summary")
async def get_gitops_summary() -> Dict:
    """GitOpsサマリー"""
    return gitops_manager.get_deployment_summary()


# ========== Chaos Engineering ==========

@router.post("/chaos/experiment/pod-kill")
async def run_pod_kill_experiment(pod_name: str) -> Dict:
    """Pod停止実験"""
    experiment = await chaos_manager.run_pod_kill_experiment(pod_name)
    return experiment.to_dict()


@router.post("/chaos/experiment/network-delay")
async def run_network_delay_experiment(
    target: str,
    delay_ms: int = 100
) -> Dict:
    """ネットワーク遅延実験"""
    experiment = await chaos_manager.run_network_delay_experiment(target, delay_ms)
    return experiment.to_dict()


@router.get("/chaos/summary")
async def get_chaos_summary() -> Dict:
    """カオスエンジニアリングサマリー"""
    return chaos_manager.get_chaos_summary()


@router.get("/chaos/mttr")
async def get_mttr_statistics() -> Dict:
    """MTTR統計"""
    return chaos_manager.get_mttr_statistics()


# ========== HA/DRP ==========

@router.post("/ha/backup")
async def create_backup(
    backup_type: str,
    database: str
) -> Dict:
    """バックアップ作成"""
    backup = await ha_drp_manager.create_backup(backup_type, database)
    return backup.to_dict()


@router.get("/ha/status")
async def get_ha_status() -> Dict:
    """HA構成ステータス"""
    return ha_drp_manager.get_ha_status()


@router.get("/ha/summary")
async def get_drp_summary() -> Dict:
    """DRPサマリー"""
    return ha_drp_manager.get_drp_summary()


# ========== Vulnerability Scanning ==========

@router.post("/vulnerability/scan/image")
async def scan_docker_image(
    image_name: str,
    scanner: str = "trivy"
) -> Dict:
    """Dockerイメージスキャン"""
    result = await vuln_scanner.scan_docker_image(image_name, scanner)
    return result.to_dict()


@router.get("/vulnerability/summary")
async def get_vulnerability_summary() -> Dict:
    """脆弱性サマリー"""
    return vuln_scanner.get_vulnerability_summary()


@router.get("/vulnerability/scans")
async def get_scan_summary() -> Dict:
    """スキャンサマリー"""
    return vuln_scanner.get_scan_summary()


@router.get("/vulnerability/remediations")
async def get_remediation_summary() -> Dict:
    """修復サマリー"""
    return vuln_scanner.get_remediation_summary()


# ========== Complete OPS Dashboard ==========

@router.get("/dashboard")
async def get_ops_dashboard() -> Dict:
    """OPS統合ダッシュボード"""
    return {
        "health": health_checker.get_health_report(),
        "storage": {
            "metrics": storage_layer.get_metrics_summary(),
            "audit": storage_layer.get_audit_summary()
        },
        "certificates": cert_manager.get_certificate_summary(),
        "crypto_validation": crypto_validator.get_validation_summary(),
        "kms": kms_manager.get_kms_summary(),
        "gitops": gitops_manager.get_deployment_summary(),
        "chaos": chaos_manager.get_chaos_summary(),
        "ha_drp": ha_drp_manager.get_drp_summary(),
        "vulnerability": {
            "summary": vuln_scanner.get_vulnerability_summary(),
            "scans": vuln_scanner.get_scan_summary(),
            "remediations": vuln_scanner.get_remediation_summary()
        }
    }
