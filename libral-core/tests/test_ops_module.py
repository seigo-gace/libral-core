"""
OPS Module Tests
OPS Blueprint V1実装のテスト
"""

import pytest
from datetime import datetime, timedelta
from libral_core.ops.monitoring.metrics import metrics_registry
from libral_core.ops.monitoring.alerting import AlertManager, AlertSeverity
from libral_core.ops.storage_layer.manager import StorageAbstractionLayer
from libral_core.ops.storage_layer.provider import StorageSecurityLevel
from libral_core.ops.security.certificates import CertificateManager
from libral_core.ops.security.crypto_validator import CryptoValidator
from libral_core.ops.security.kms_manager import KMSManager, KeyType
from libral_core.ops.k8s.gitops import GitOpsManager
from libral_core.ops.k8s.chaos import ChaosEngineeringManager, ExperimentType
from libral_core.ops.k8s.ha_drp import HADRPManager
from libral_core.ops.k8s.vulnerability import VulnerabilityScanner


class TestMonitoring:
    """監視システムテスト"""
    
    def test_metrics_registry_initialization(self):
        """メトリクスレジストリ初期化"""
        assert metrics_registry is not None
        assert metrics_registry.storage_latency is not None
        assert metrics_registry.storage_errors is not None
        assert metrics_registry.storage_calls is not None
    
    def test_metrics_record_operations(self):
        """メトリクス記録操作"""
        metrics_registry.record_failover("telegram", "s3")
        metrics_registry.update_success_rate("telegram", 0.99)
        metrics_registry.record_crypto_operation("encrypt", "gpg")
        assert True  # 例外が発生しないことを確認
    
    @pytest.mark.asyncio
    async def test_alert_manager(self):
        """アラートマネージャー"""
        manager = AlertManager()
        
        await manager.send_alert(
            title="Test Alert",
            description="Test alert description",
            severity=AlertSeverity.INFO,
            component="test_component"
        )
        
        alerts = manager.get_recent_alerts(limit=10)
        assert len(alerts) == 1
        assert alerts[0].title == "Test Alert"
        assert alerts[0].severity == AlertSeverity.INFO


class TestStorageLayer:
    """ストレージ抽象化レイヤーテスト"""
    
    @pytest.mark.asyncio
    async def test_storage_layer_initialization(self):
        """SAL初期化"""
        sal = StorageAbstractionLayer()
        assert sal is not None
        assert len(sal.providers) == 4  # Telegram, S3, LOB, Local
    
    @pytest.mark.asyncio
    async def test_storage_operations(self):
        """ストレージ操作"""
        sal = StorageAbstractionLayer()
        
        # データ保存
        success = await sal.store(
            "test_key",
            b"test_data",
            StorageSecurityLevel.STANDARD,
            "test_user"
        )
        assert success is True
        
        # データ取得
        data = await sal.retrieve(
            "test_key",
            StorageSecurityLevel.STANDARD,
            "test_user"
        )
        assert data is not None
    
    @pytest.mark.asyncio
    async def test_storage_health_check(self):
        """ストレージヘルスチェック"""
        sal = StorageAbstractionLayer()
        health = await sal.health_check_all()
        assert len(health) == 4
        assert all(isinstance(v, bool) for v in health.values())
    
    def test_storage_metrics_summary(self):
        """ストレージメトリクスサマリー"""
        sal = StorageAbstractionLayer()
        summary = sal.get_metrics_summary()
        assert "telegram" in summary
        assert "s3" in summary
        assert "lob" in summary
        assert "local" in summary


class TestSecurity:
    """セキュリティテスト"""
    
    def test_certificate_manager(self):
        """証明書マネージャー"""
        manager = CertificateManager()
        
        # 全証明書取得
        certs = manager.get_all_certificates()
        assert len(certs) >= 3  # デフォルト証明書
        
        # 有効な証明書
        valid_certs = manager.get_valid_certificates()
        assert len(valid_certs) >= 0
        
        # サマリー
        summary = manager.get_certificate_summary()
        assert "total_certificates" in summary
        assert "by_type" in summary
    
    @pytest.mark.asyncio
    async def test_crypto_validator(self):
        """暗号検証器"""
        validator = CryptoValidator()
        
        # アルゴリズム検証
        result = await validator.validate_algorithm_usage(
            "test_module",
            ["AES-256-OCB", "SHA-512"]
        )
        assert result.status.value == "passed"
        assert result.certified_module_used is True
    
    def test_kms_manager(self):
        """KMSマネージャー"""
        kms = KMSManager()
        
        # 鍵取得
        keys = kms.get_active_keys()
        assert len(keys) >= 3  # デフォルト鍵
        
        # アクセスチェック
        has_access = kms.check_access(
            "context_lock_master_001",
            "gpg_module",
            "sign"
        )
        assert has_access is True
        
        # サマリー
        summary = kms.get_kms_summary()
        assert "total_keys" in summary
        assert "active_keys" in summary


class TestGitOps:
    """GitOpsテスト"""
    
    @pytest.mark.asyncio
    async def test_gitops_manager(self):
        """GitOpsマネージャー"""
        manager = GitOpsManager()
        
        # Git変更検出
        detected = await manager.detect_git_change(
            "libral-core",
            "abc123def",
            "main"
        )
        assert detected is True
        
        # デプロイメント取得
        deployments = manager.get_recent_deployments(limit=5)
        assert len(deployments) >= 1
        
        # サマリー
        summary = manager.get_deployment_summary()
        assert "total_deployments" in summary
        assert summary["manual_operations_blocked"] is True


class TestChaosEngineering:
    """カオスエンジニアリングテスト"""
    
    @pytest.mark.asyncio
    async def test_chaos_manager(self):
        """カオスマネージャー"""
        manager = ChaosEngineeringManager()
        
        # Pod停止実験
        experiment = await manager.run_pod_kill_experiment("test-pod")
        assert experiment is not None
        assert experiment.experiment_type == ExperimentType.POD_KILL
        
        # MTTR統計
        stats = manager.get_mttr_statistics()
        assert "total_experiments" in stats
        assert "target_mttr" in stats
        
        # サマリー
        summary = manager.get_chaos_summary()
        assert "total_experiments" in summary
        assert "mttr_stats" in summary


class TestHADRP:
    """HA/DRPテスト"""
    
    @pytest.mark.asyncio
    async def test_ha_drp_manager(self):
        """HA/DRPマネージャー"""
        manager = HADRPManager()
        
        # バックアップ作成
        backup = await manager.create_backup("full", "libral_db")
        assert backup is not None
        assert backup.backup_type == "full"
        
        # HAステータス
        status = manager.get_ha_status()
        assert status["patroni_enabled"] is True
        
        # サマリー
        summary = manager.get_drp_summary()
        assert "ha_status" in summary
        assert "backup_summary" in summary


class TestVulnerabilityScanning:
    """脆弱性スキャンテスト"""
    
    @pytest.mark.asyncio
    async def test_vulnerability_scanner(self):
        """脆弱性スキャナー"""
        scanner = VulnerabilityScanner()
        
        # Dockerイメージスキャン
        result = await scanner.scan_docker_image("libral-core:latest", "trivy")
        assert result is not None
        assert result.target == "image"
        
        # 脆弱性サマリー
        summary = scanner.get_vulnerability_summary()
        assert "total_vulnerabilities" in summary
        assert "sla_hours" in summary
        
        # スキャンサマリー
        scan_summary = scanner.get_scan_summary()
        assert "total_scans" in scan_summary


@pytest.mark.asyncio
async def test_ops_integration():
    """OPS統合テスト"""
    
    # 全コンポーネント初期化
    sal = StorageAbstractionLayer()
    cert_manager = CertificateManager()
    kms_manager = KMSManager()
    gitops = GitOpsManager()
    chaos = ChaosEngineeringManager()
    ha_drp = HADRPManager()
    vuln_scanner = VulnerabilityScanner()
    
    # ストレージ操作
    await sal.store("integration_test", b"test_data", StorageSecurityLevel.CONFIDENTIAL)
    
    # 証明書チェック
    certs = cert_manager.check_all_certificates()
    assert certs["total"] >= 3
    
    # Git変更検出
    await gitops.detect_git_change("libral-core", "test_commit", "main")
    
    # カオス実験
    await chaos.run_pod_kill_experiment("test-pod")
    
    # バックアップ
    await ha_drp.create_backup("incremental", "libral_db")
    
    # 脆弱性スキャン
    await vuln_scanner.scan_docker_image("test:latest")
    
    # 統合動作確認
    assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
