"""
Prometheusメトリクス統合
SAL_OPS_001実装: ストレージプロバイダのレイテンシ、エラーレート、APIコール数
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from typing import Dict, Optional
import time
from functools import wraps


class MetricsRegistry:
    """中央メトリクスレジストリ"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        
        self.storage_latency = Histogram(
            'storage_provider_latency_seconds',
            'Storage provider operation latency',
            ['provider', 'operation'],
            registry=self.registry,
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0)
        )
        
        self.storage_errors = Counter(
            'storage_provider_errors_total',
            'Storage provider error count',
            ['provider', 'error_type'],
            registry=self.registry
        )
        
        self.storage_calls = Counter(
            'storage_provider_api_calls_total',
            'Total API calls to storage providers',
            ['provider', 'method'],
            registry=self.registry
        )
        
        self.storage_success_rate = Gauge(
            'storage_provider_success_rate',
            'Storage provider success rate (0-1)',
            ['provider'],
            registry=self.registry
        )
        
        self.storage_failover_total = Counter(
            'storage_provider_failover_total',
            'Storage provider failover events',
            ['from_provider', 'to_provider'],
            registry=self.registry
        )
        
        self.crypto_operations = Counter(
            'crypto_operations_total',
            'Cryptographic operations count',
            ['operation', 'module'],
            registry=self.registry
        )
        
        self.crypto_validation_errors = Counter(
            'crypto_validation_errors_total',
            'Crypto module validation errors',
            ['module', 'reason'],
            registry=self.registry
        )
        
        self.certificate_expiry = Gauge(
            'certificate_expiry_days',
            'Days until certificate expiration',
            ['certificate_name'],
            registry=self.registry
        )
        
        self.chaos_experiments = Counter(
            'chaos_experiments_total',
            'Chaos engineering experiments executed',
            ['experiment_type', 'status'],
            registry=self.registry
        )
        
        self.system_recovery_time = Histogram(
            'system_recovery_time_seconds',
            'System recovery time (MTTR)',
            ['component'],
            registry=self.registry
        )
        
        self.vulnerability_scans = Counter(
            'vulnerability_scans_total',
            'Vulnerability scan executions',
            ['scanner', 'severity'],
            registry=self.registry
        )

    def track_storage_operation(self, provider: str, operation: str):
        """ストレージ操作の追跡デコレータ"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                self.storage_calls.labels(provider=provider, method=operation).inc()
                
                try:
                    result = await func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    self.storage_latency.labels(
                        provider=provider,
                        operation=operation
                    ).observe(elapsed)
                    return result
                    
                except Exception as e:
                    error_type = type(e).__name__
                    self.storage_errors.labels(
                        provider=provider,
                        error_type=error_type
                    ).inc()
                    raise
                    
            return wrapper
        return decorator

    def record_failover(self, from_provider: str, to_provider: str):
        """フェイルオーバーイベント記録"""
        self.storage_failover_total.labels(
            from_provider=from_provider,
            to_provider=to_provider
        ).inc()

    def update_success_rate(self, provider: str, rate: float):
        """成功率更新（0-1）"""
        self.storage_success_rate.labels(provider=provider).set(rate)

    def record_crypto_operation(self, operation: str, module: str):
        """暗号化操作記録"""
        self.crypto_operations.labels(operation=operation, module=module).inc()

    def record_crypto_validation_error(self, module: str, reason: str):
        """暗号検証エラー記録"""
        self.crypto_validation_errors.labels(module=module, reason=reason).inc()

    def update_certificate_expiry(self, cert_name: str, days_remaining: int):
        """証明書有効期限更新"""
        self.certificate_expiry.labels(certificate_name=cert_name).set(days_remaining)

    def record_chaos_experiment(self, experiment_type: str, status: str):
        """カオスエンジニアリング実験記録"""
        self.chaos_experiments.labels(
            experiment_type=experiment_type,
            status=status
        ).inc()

    def record_recovery_time(self, component: str, seconds: float):
        """システム復旧時間記録"""
        self.system_recovery_time.labels(component=component).observe(seconds)

    def record_vulnerability_scan(self, scanner: str, severity: str):
        """脆弱性スキャン記録"""
        self.vulnerability_scans.labels(scanner=scanner, severity=severity).inc()


metrics_registry = MetricsRegistry()


class PrometheusExporter:
    """Prometheusエクスポーター"""
    
    @staticmethod
    def get_metrics() -> bytes:
        """メトリクス取得"""
        return generate_latest(metrics_registry.registry)
    
    @staticmethod
    def get_metrics_text() -> str:
        """メトリクステキスト取得"""
        return PrometheusExporter.get_metrics().decode('utf-8')
