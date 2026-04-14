"""
Predictive Monitor
予測型異常検知機能

システムメトリクスに基づく予測型異常検知
CRADのトリガーを進化させる
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now


@dataclass
class MetricSnapshot:
    """メトリクススナップショット"""
    timestamp: datetime
    metric_name: str
    value: float


@dataclass
class AnomalyDetection:
    """異常検知結果"""
    detection_id: str
    metric_name: str
    current_value: float
    predicted_value: float
    deviation: float
    severity: str  # "low" | "medium" | "high" | "critical"
    timestamp: datetime


class PredictiveMonitor:
    """
    予測型異常検知
    
    移動平均とz-scoreベースの異常検知
    """
    
    def __init__(self, window_size: int = 30):
        """
        Args:
            window_size: 移動平均ウィンドウサイズ（デフォルト30）
        """
        self.window_size = window_size
        self.metrics_history: Dict[str, deque] = {}
        self.anomalies: List[AnomalyDetection] = []
        
        # 異常検知しきい値（標準偏差の倍数）
        self.thresholds = {
            "low": 1.5,
            "medium": 2.0,
            "high": 2.5,
            "critical": 3.0
        }
    
    def record_metric(self, metric_name: str, value: float) -> Optional[AnomalyDetection]:
        """
        メトリクス記録と異常検知
        
        Args:
            metric_name: メトリクス名
            value: 値
        
        Returns:
            異常検知されたらAnomalyDetection、正常ならNone
        """
        # 履歴初期化
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = deque(maxlen=self.window_size)
        
        history = self.metrics_history[metric_name]
        
        # 履歴に追加
        snapshot = MetricSnapshot(
            timestamp=utc_now(),
            metric_name=metric_name,
            value=value
        )
        history.append(snapshot)
        
        # ウィンドウサイズに達していない場合は異常検知スキップ
        if len(history) < self.window_size:
            return None
        
        # 異常検知実行
        return self._detect_anomaly(metric_name, value, history)
    
    def _detect_anomaly(
        self, 
        metric_name: str, 
        current_value: float, 
        history: deque
    ) -> Optional[AnomalyDetection]:
        """
        異常検知実行
        
        Args:
            metric_name: メトリクス名
            current_value: 現在値
            history: 履歴データ
        
        Returns:
            異常検知されたらAnomalyDetection
        """
        # 過去データから統計量計算
        values = [s.value for s in history]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # z-score計算
        if std_dev == 0:
            return None  # 分散がゼロの場合は異常検知不可
        
        z_score = abs((current_value - mean) / std_dev)
        
        # しきい値判定
        severity = None
        if z_score >= self.thresholds["critical"]:
            severity = "critical"
        elif z_score >= self.thresholds["high"]:
            severity = "high"
        elif z_score >= self.thresholds["medium"]:
            severity = "medium"
        elif z_score >= self.thresholds["low"]:
            severity = "low"
        
        if severity:
            detection = AnomalyDetection(
                detection_id=f"{metric_name}_{utc_now().timestamp()}",
                metric_name=metric_name,
                current_value=current_value,
                predicted_value=mean,
                deviation=z_score,
                severity=severity,
                timestamp=utc_now()
            )
            
            self.anomalies.append(detection)
            
            # 最新100件のみ保持
            if len(self.anomalies) > 100:
                self.anomalies = self.anomalies[-100:]
            
            return detection
        
        return None
    
    def get_recent_anomalies(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        最近の異常検知取得
        
        Args:
            hours: 何時間以内の異常を取得するか
        
        Returns:
            異常検知リスト
        """
        cutoff = utc_now() - timedelta(hours=hours)
        recent = [a for a in self.anomalies if a.timestamp >= cutoff]
        
        return [
            {
                "detection_id": a.detection_id,
                "metric_name": a.metric_name,
                "current_value": round(a.current_value, 2),
                "predicted_value": round(a.predicted_value, 2),
                "deviation": round(a.deviation, 2),
                "severity": a.severity,
                "timestamp": a.timestamp.isoformat()
            }
            for a in recent
        ]
    
    def get_metric_forecast(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        メトリクス予測
        
        Args:
            metric_name: メトリクス名
        
        Returns:
            予測データ
        """
        history = self.metrics_history.get(metric_name)
        if not history or len(history) < self.window_size:
            return None
        
        values = [s.value for s in history]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        # 簡易的な線形トレンド計算
        n = len(values)
        x_values = list(range(n))
        x_mean = sum(x_values) / n
        
        # 傾き計算
        numerator = sum((x_values[i] - x_mean) * (values[i] - mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # 次の値を予測
        next_value = mean + slope * n
        
        return {
            "metric_name": metric_name,
            "current_mean": round(mean, 2),
            "std_deviation": round(std_dev, 2),
            "trend_slope": round(slope, 4),
            "predicted_next_value": round(next_value, 2),
            "confidence_interval_95": {
                "lower": round(next_value - 1.96 * std_dev, 2),
                "upper": round(next_value + 1.96 * std_dev, 2)
            }
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "monitored_metrics": list(self.metrics_history.keys()),
            "total_anomalies_detected": len(self.anomalies),
            "recent_anomalies_24h": len(self.get_recent_anomalies(24)),
            "severity_breakdown": {
                "critical": sum(1 for a in self.anomalies if a.severity == "critical"),
                "high": sum(1 for a in self.anomalies if a.severity == "high"),
                "medium": sum(1 for a in self.anomalies if a.severity == "medium"),
                "low": sum(1 for a in self.anomalies if a.severity == "low")
            }
        }


# グローバルインスタンス
predictive_monitor = PredictiveMonitor()
