# LPO (Libral Protocol Optimizer)

## 概要

**LPO (Libral Protocol Optimizer)**は、Libral Coreの自律監視・最適化システムです。システムの健全性を継続的に監視し、自己修復、財務最適化、予測的監視を提供します。

## 主要機能

### 1. 自律監視 (Autonomous Monitoring)

システム全体をリアルタイムで監視し、異常を検出します。

- **システムメトリクス**: CPU、メモリ、ディスク、ネットワーク
- **アプリケーションメトリクス**: API レスポンスタイム、エラー率、スループット
- **ビジネスメトリクス**: ユーザー数、トランザクション数、収益

### 2. ヘルススコアリング (Health Scoring)

各コンポーネントの健全性を0-100のスコアで評価します。

```typescript
interface HealthScore {
  overall: number;        // 総合スコア (0-100)
  components: {
    api: number;          // API健全性
    database: number;     // データベース健全性
    cache: number;        // キャッシュ健全性
    messaging: number;    // メッセージング健全性
  };
  trend: "improving" | "stable" | "degrading";
  alerts: Alert[];
}
```

### 3. ZK監査 (Zero-Knowledge Audit)

ゼロ知識証明を使用して、プライバシーを保ちながら監査証跡を提供します。

- **プライバシー保護**: データ内容を明かさずに検証可能
- **改ざん防止**: 暗号学的に保証された監査ログ
- **選択的開示**: 必要な情報のみを開示可能

### 4. 自己修復AI (Self-Healing AI)

システムの問題を自動的に検出し、修復します。

**修復シナリオ:**
- メモリリーク検出 → プロセス再起動
- API遅延検出 → キャッシュ最適化
- データベース接続エラー → 接続プール再構成
- 高負荷検出 → スケールアウト

```typescript
interface HealingAction {
  type: "restart" | "optimize" | "scale" | "reconfigure";
  target: string;           // 対象コンポーネント
  reason: string;           // 修復理由
  expectedImpact: string;   // 期待される効果
  rollbackPlan: string;     // ロールバック計画
}
```

### 5. 財務最適化 (Finance Optimizer)

コスト効率を最適化します。

- **リソース最適化**: 未使用リソースの削減
- **キャッシュ戦略**: ヒット率向上によるAPI呼び出し削減
- **スケーリング戦略**: 需要予測に基づく動的スケーリング
- **コスト分析**: サービスごとのコスト可視化

### 6. RBAC抽象化 (Role-Based Access Control)

柔軟な権限管理を提供します。

```typescript
interface RBACPolicy {
  role: string;             // ロール名
  permissions: {
    resource: string;       // リソース
    actions: string[];      // 許可されたアクション
    conditions?: {          // 条件付きアクセス
      time?: string[];      // 時間帯制限
      ip?: string[];        // IP制限
      mfa?: boolean;        // MFA必須
    };
  }[];
}
```

### 7. 予測的監視 (Predictive Monitoring)

機械学習を使用して問題を事前に予測します。

- **トレンド分析**: 過去のデータからトレンドを抽出
- **異常検出**: 通常パターンからの逸脱を検出
- **容量計画**: リソース不足を事前に予測
- **障害予測**: システム障害の前兆を検出

## アーキテクチャ

### Python モジュール構成

```python
# libral-core/src/modules/lpo/

├── __init__.py
├── core.py              # LPOコアロジック
├── health_score.py      # ヘルススコアリング
├── self_healing.py      # 自己修復AI
├── finance.py           # 財務最適化
├── rbac.py              # RBAC抽象化
├── predictive.py        # 予測的監視
├── zk_audit.py          # ZK監査
└── router.py            # FastAPI ルーター
```

### Node.js API クライアント

```typescript
// client/src/api/lpo.ts

export const lpoApi = {
  getHealthScore: () => fetch('/api/lpo/health'),
  getSelfHealingLog: () => fetch('/api/lpo/healing/log'),
  getFinanceReport: () => fetch('/api/lpo/finance/report'),
  getRBACPolicies: () => fetch('/api/lpo/rbac/policies'),
  getPredictions: () => fetch('/api/lpo/predictive/forecast')
};
```

## API エンドポイント

### ヘルススコア

**総合ヘルススコア取得:**
```http
GET /api/lpo/health
```

**レスポンス:**
```json
{
  "overall": 92,
  "components": {
    "api": 95,
    "database": 88,
    "cache": 94,
    "messaging": 90
  },
  "trend": "stable",
  "alerts": [
    {
      "level": "warning",
      "component": "database",
      "message": "Connection pool utilization at 85%"
    }
  ]
}
```

### 自己修復

**修復ログ取得:**
```http
GET /api/lpo/healing/log
```

**手動修復実行:**
```http
POST /api/lpo/healing/execute
Content-Type: application/json

{
  "action": "restart",
  "target": "api-server",
  "reason": "High memory usage"
}
```

### 財務最適化

**コストレポート:**
```http
GET /api/lpo/finance/report?period=30d
```

**レスポンス:**
```json
{
  "totalCost": 1250.50,
  "breakdown": {
    "compute": 650.00,
    "database": 350.50,
    "storage": 150.00,
    "network": 100.00
  },
  "savings": {
    "potential": 215.00,
    "recommendations": [
      "Reduce unused database instances: $120",
      "Optimize cache hit rate: $60",
      "Use reserved instances: $35"
    ]
  }
}
```

### RBAC

**ポリシー一覧:**
```http
GET /api/lpo/rbac/policies
```

**ポリシー作成:**
```http
POST /api/lpo/rbac/policies
Content-Type: application/json

{
  "role": "data_analyst",
  "permissions": [
    {
      "resource": "analytics",
      "actions": ["read", "export"],
      "conditions": {
        "time": ["09:00-18:00"],
        "mfa": true
      }
    }
  ]
}
```

### 予測的監視

**予測データ取得:**
```http
GET /api/lpo/predictive/forecast?metric=cpu&horizon=7d
```

**レスポンス:**
```json
{
  "metric": "cpu",
  "current": 65,
  "predictions": [
    { "date": "2025-10-16", "value": 68, "confidence": 0.92 },
    { "date": "2025-10-17", "value": 72, "confidence": 0.89 },
    { "date": "2025-10-18", "value": 78, "confidence": 0.85 }
  ],
  "alerts": [
    {
      "date": "2025-10-18",
      "message": "CPU usage expected to exceed 75% threshold"
    }
  ]
}
```

## 使用例

### ヘルススコア監視

```typescript
import { lpoApi } from '@/api/lpo';

// ヘルススコア取得
const health = await lpoApi.getHealthScore();

if (health.overall < 80) {
  console.warn('システム健全性が低下しています');
  
  // アラートを確認
  for (const alert of health.alerts) {
    console.log(`[${alert.level}] ${alert.component}: ${alert.message}`);
  }
}

// トレンド確認
if (health.trend === "degrading") {
  // 自己修復を検討
  const healingLog = await lpoApi.getSelfHealingLog();
  console.log('最近の修復アクション:', healingLog);
}
```

### 財務最適化

```typescript
// コストレポート取得
const report = await lpoApi.getFinanceReport();

console.log(`総コスト: $${report.totalCost}`);
console.log(`潜在的節約額: $${report.savings.potential}`);

// 推奨事項の表示
report.savings.recommendations.forEach((rec, i) => {
  console.log(`${i + 1}. ${rec}`);
});
```

### 予測的監視

```typescript
// CPU使用率の7日間予測
const forecast = await lpoApi.getPredictions({
  metric: 'cpu',
  horizon: '7d'
});

// アラートチェック
forecast.alerts.forEach(alert => {
  console.warn(`予測アラート (${alert.date}): ${alert.message}`);
});

// 高信頼度の予測のみ抽出
const highConfidence = forecast.predictions.filter(p => p.confidence > 0.9);
console.log('高信頼度予測:', highConfidence);
```

## 設定

### 環境変数

```env
# LPO設定
LPO_HEALTH_CHECK_INTERVAL=60        # ヘルスチェック間隔(秒)
LPO_AUTO_HEALING_ENABLED=true       # 自己修復の有効化
LPO_ALERT_THRESHOLD=80              # アラート閾値
LPO_PREDICTION_HORIZON_DAYS=7       # 予測期間(日)

# ZK監査設定
LPO_ZK_ENABLED=true
LPO_ZK_PROOF_TYPE=groth16

# 財務設定
LPO_COST_OPTIMIZATION_ENABLED=true
LPO_COST_ALERT_THRESHOLD=1000       # コストアラート閾値($)
```

### 設定ファイル (libral-core/src/modules/lpo/config.py)

```python
class LPOConfig:
    HEALTH_CHECK_INTERVAL = 60
    AUTO_HEALING_ENABLED = True
    ALERT_THRESHOLD = 80
    PREDICTION_HORIZON_DAYS = 7
    ZK_ENABLED = True
    COST_OPTIMIZATION_ENABLED = True
```

## 監視ダッシュボード

LPOは専用の監視ダッシュボードを提供します:

### Monitor Mode (`/monitor`)

- リアルタイムヘルススコア表示
- システムメトリクスのグラフ
- アラート一覧
- 自己修復ログ

### Control Mode (`/control`)

- 手動修復アクション実行
- RBAC ポリシー管理
- システム設定変更
- 緊急停止ボタン

## トラブルシューティング

### よくある問題

**Q: ヘルススコアが常に低い**
- A: 閾値設定を確認してください。環境に合わせて調整が必要な場合があります

**Q: 自己修復が動作しない**
- A: `LPO_AUTO_HEALING_ENABLED=true` が設定されているか確認してください

**Q: 予測精度が低い**
- A: 学習データが不足している可能性があります。最低30日間のデータ蓄積が推奨されます

**Q: ZK監査証明の検証に失敗する**
- A: 正しいProverパラメータが設定されているか確認してください

## 開発ガイド

### カスタムヘルスチェックの追加

```python
# libral-core/src/modules/lpo/health_score.py

class CustomHealthCheck:
    async def check_custom_service(self):
        # カスタムサービスのヘルスチェック
        response = await http_client.get('http://custom-service/health')
        return {
            'score': 100 if response.status == 200 else 0,
            'details': response.json()
        }
```

### カスタム修復アクションの追加

```python
# libral-core/src/modules/lpo/self_healing.py

class CustomHealingAction:
    async def heal_custom_issue(self, issue):
        # カスタム修復ロジック
        if issue.type == "custom_error":
            # 修復実行
            await self.restart_service(issue.target)
            return {"status": "healed", "action": "restart"}
```

## リファレンス

- [ヘルススコアリング仕様](./LPO_HEALTH_SPEC.md)
- [ZK監査プロトコル](./LPO_ZK_AUDIT.md)
- [自己修復アルゴリズム](./LPO_SELF_HEALING.md)
- [予測モデル詳細](./LPO_PREDICTIVE.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core SelfEvolution Team
