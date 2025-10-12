# Libral Core - Master Reference (PCGP V1.0)

**Professional Grooming Protocol準拠 - 統合リファレンスドキュメント**

最終更新: 2025年10月4日

---

## 📋 目次

1. [システムアーキテクチャ](#システムアーキテクチャ)
2. [ポリシー一覧](#ポリシー一覧)
3. [AMM/CRADルール](#ammcradルール)
4. [API エンドポイント](#apiエンドポイント)
5. [Component層](#component層)
6. [OPS運用自動化](#ops運用自動化)
7. [開発ガイドライン](#開発ガイドライン)

---

## システムアーキテクチャ

### PCGP 4階層モジュールスタイル

```
libral-core/
├── src/                          # ソースコード（PCGP準拠構造）
│   ├── main.py                   # メインアプリケーション
│   ├── library/                  # ライブラリ層
│   │   └── components/           # Component層（最小単位部品）
│   ├── modules/                  # 機能モジュール
│   └── governance/               # ガバナンスレイヤー（AMM/CRAD）
├── libral_core/                  # コアシステム
│   ├── integrated_modules/       # 統合モジュール（LIC/LEB/LAS/LGL）
│   ├── modules/                  # 独立モジュール（Payment/API Hub）
│   └── ops/                      # OPS運用自動化
├── policies/                     # ポリシー定義（JSON/YAML）
├── infra/                        # インフラ設定
├── docs/                         # ドキュメント
└── archive/                      # アーカイブ
```

### Revolutionary 4+1 Module Integration

- **LIC (Libral Identity Core)**: GPG暗号化、認証、ZKP、DID
- **LEB (Libral Event Bus)**: 通信ゲートウェイ、イベント管理
- **LAS (Libral Asset Service)**: ライブラリユーティリティ、アセット管理、WebAssembly
- **LGL (Libral Governance Layer)**: デジタル署名、トラストチェーン、ガバナンス、監査
- **Payment System**: Telegram Stars、PayPay、PayPal統合
- **API Hub**: OpenAI、Anthropic、Google、AWS統合

---

## ポリシー一覧

### 1. AMM（Autonomous Moderator Module）セキュリティポリシー

**ファイル**: [`policies/security_policy_amm.json`](../policies/security_policy_amm.json)

**概要**: KMSアクセス制御とGitOps操作ブロックの自動執行ポリシー

**ルール一覧**:
- **KMS-R-001**: KMSアクセス頻度制限（3回/秒 → 30分ブロック）
- **KMS-R-002**: 営業時間外アクセス制御（UTC 22:00-07:00 → 2FA要求）
- **GIT-R-001**: GitOps強制（手動kubectl操作ブロック）

**実装モジュール**: [`src/governance/autonomous_moderator.py`](../src/governance/autonomous_moderator.py)

### 2. CRAD（Context-Aware Recovery & Auto Debugger）ランブック

**ファイル**: [`policies/recovery_runbook_crad.json`](../policies/recovery_runbook_crad.json)

**概要**: アラートベース自動リカバリプロトコル（MTTRターゲット: 180秒）

**プロトコル一覧**:

#### HighLatency_P99_BackendAPI（P99 150ms超過）
1. K8Sスケールアウト (+1 replica)
2. カオス実験（Network Delay）※遅延継続時のみ

#### Postgres_Primary_Down（PostgreSQL Primary障害）
1. Patroni HAフェイルオーバー
2. PITR復旧テスト（5分前時点）※フェイルオーバー失敗時

**実装モジュール**: [`src/governance/context_aware_debugger.py`](../src/governance/context_aware_debugger.py)

---

## AMM/CRADルール

### AMM実装詳細

**モジュール**: `AutonomousModerator`

**主要メソッド**:
- `check_kms_access(pod_id, operation)` - KMSアクセス検証
- `check_kubectl_operation(user, operation, target)` - kubectl操作検証
- `get_blocked_pods()` - ブロック中Pod一覧
- `get_policy_summary()` - ポリシーサマリー

**使用例**:
```python
from governance.autonomous_moderator import autonomous_moderator

# KMSアクセスチェック
result = autonomous_moderator.check_kms_access("pod-123", "decrypt")

# kubectl操作チェック
result = autonomous_moderator.check_kubectl_operation("admin1", "exec", "pod/backend-api")
```

### CRAD実装詳細

**モジュール**: `ContextAwareAutoDebugger`

**主要メソッド**:
- `handle_alert(alert_name, alert_data)` - アラート処理（async）
- `get_mttr_stats()` - MTTR統計
- `get_crad_summary()` - CRADサマリー

**使用例**:
```python
from governance.context_aware_debugger import context_aware_debugger

# アラート処理
execution = await context_aware_debugger.handle_alert(
    "HighLatency_P99_BackendAPI",
    {"latency_p99": 180, "latency_persists": True}
)

# MTTR統計取得
stats = context_aware_debugger.get_mttr_stats()
```

---

## API エンドポイント

### Core System API

**ベースURL**: `http://localhost:8000`

#### システム管理
- `GET /health` - ヘルスチェック
- `GET /api/v2/system/overview` - システム概要

#### 統合モジュール（V2アーキテクチャ）
- `POST /api/v2/identity/*` - LIC（GPG、認証、ZKP、DID）
- `POST /api/v2/eventbus/*` - LEB（通信、イベント）
- `POST /api/v2/assets/*` - LAS（アセット、WebAssembly）
- `POST /api/v2/governance/*` - LGL（署名、トラストチェーン、監査）

#### 独立モジュール
- `POST /api/payments/*` - Payment System
- `GET /api/external/*` - API Hub

### OPS運用自動化API

**ベースURL**: `http://localhost:8000/ops`

#### 監視・メトリクス
- `GET /ops/metrics` - Prometheusメトリクス
- `GET /ops/dashboard` - 統合ダッシュボード

#### ストレージ抽象化レイヤー（SAL）
- `POST /ops/storage/store` - データ保存
- `GET /ops/storage/retrieve` - データ取得
- `GET /ops/storage/health` - ヘルスチェック
- `GET /ops/storage/metrics` - メトリクスサマリー

#### セキュリティ
- `GET /ops/certificates` - 証明書一覧
- `POST /ops/crypto/validation/usage` - 暗号検証
- `GET /ops/kms/keys` - KMS鍵一覧

#### K8S運用
- `POST /ops/gitops/detect-change` - Git変更検出
- `POST /ops/chaos/experiments/pod-kill` - カオス実験
- `POST /ops/ha/backup` - バックアップ作成
- `POST /ops/vulnerability/scan` - 脆弱性スキャン

### ガバナンスAPI（AMM/CRAD）

**実装予定エンドポイント**:
- `POST /governance/amm/check-kms-access` - KMSアクセスチェック
- `POST /governance/amm/check-kubectl` - kubectl操作チェック
- `GET /governance/amm/blocked-pods` - ブロック中Pod一覧
- `POST /governance/crad/handle-alert` - アラート処理
- `GET /governance/crad/mttr-stats` - MTTR統計

---

## Component層

**場所**: `src/library/components/`

### 提供機能

#### 1. 日時処理（`datetime_utils.py`）
- `utc_now()` - UTC現在時刻
- `format_iso8601(dt)` - ISO8601形式変換
- `is_business_hours(dt)` - 営業時間判定
- `format_relative_time(dt)` - 相対時間表示

#### 2. 暗号化ヘルパー（`crypto_helpers.py`）
- `generate_random_token(length)` - 安全なトークン生成
- `sha256_hash(data)` - SHA-256ハッシュ
- `hmac_sha256(data, key)` - HMAC署名
- `constant_time_compare(a, b)` - タイミング攻撃対策比較

#### 3. 設定ローダー（`config_loader.py`）
- `config_loader.load_json(path)` - JSON読み込み
- `config_loader.load_policy(name)` - ポリシー読み込み
- `config_loader.get_bool_env(key)` - 環境変数（bool）

#### 4. バリデーション（`validators.py`）
- `validate_not_empty(value)` - 空文字列チェック
- `validate_email(email)` - メールバリデーション
- `validate_range(value, min, max)` - 数値範囲チェック
- `sanitize_string(value)` - 文字列サニタイズ

**使用例**:
```python
from library.components import utc_now, sha256_hash, config_loader, validate_email

# 日時取得
now = utc_now()

# ハッシュ計算
hash_value = sha256_hash("my_data")

# ポリシー読み込み
policy = config_loader.load_policy("security_policy_amm")

# バリデーション
email = validate_email("user@example.com")
```

---

## OPS運用自動化

### OPS Blueprint V1実装

#### SAL運用指令（Storage Abstraction Layer）
- **SAL_OPS_001**: Prometheus統合（レイテンシ、エラーレート）
- **SAL_OPS_002**: 動的ルーティングポリシー（セキュリティレベル別）
- **SAL_OPS_003**: ストレージ切替監査（暗号化ログ）

#### CCA運用指令（Context-Lock Audit）
- **CCA_OPS_001**: 監査証明書管理（FIPS 140-3、ISO 27001、SOC 2）
- **CCA_OPS_002**: 暗号モジュール強制チェック
- **CCA_OPS_003**: KMS鍵管理（HSM/クラウドKMS、RBAC）

#### K8S運用自動化指令
- **K8S_OPS_001**: GitOps強制（Argo CD、手動kubectl操作ブロック）
- **K8S_OPS_002**: カオスエンジニアリング（Chaos Mesh、MTTR測定）
- **K8S_OPS_003**: PostgreSQL HA/DRP（Patroni、PITR）
- **K8S_OPS_004**: 脆弱性スキャン（Trivy/Clair、自動パッチ）

**実装場所**: `libral_core/ops/`

---

## 開発ガイドライン

### PCGP準拠開発フロー

1. **Component層参照**: 全ての機能は`src/library/components/`の部品を使用
2. **ポリシー駆動**: `policies/`のJSON/YAMLファイルで動作定義
3. **AMM/CRAD統合**: セキュリティとリカバリは自律実行
4. **GitOps強制**: 手動操作禁止、全てGit管理
5. **アーカイブ自動化**: デプロイ成功時に自動アーカイブ

### コーディング規約

```python
# Component層インポート
from library.components import utc_now, sha256_hash, config_loader

# ポリシー読み込み
policy = config_loader.load_policy("policy_name")

# 時刻はUTC統一
timestamp = utc_now()

# ハッシュは暗号学的安全性確保
secure_hash = sha256_hash(data)
```

### テスト実行

```bash
# OPSモジュールテスト
cd libral-core
pytest tests/test_ops_module.py -v

# 統合テスト
pytest tests/test_integration_complete.py -v
```

---

## アーカイブポリシー

### 自動アーカイブトリガー

**条件**: Argo CD SYNCED ステータス時

**スクリプト**: 
```bash
git archive --format=zip \
  --output=libral-core/archive/$(date +%Y%m%d_%H%M%S)_$(git rev-parse --short HEAD).zip \
  HEAD -- libral-core/src/ libral-core/policies/ libral-core/infra/
```

**格納場所**: `archive/`
- `archive/old_configs/` - 旧設定ファイル
- `archive/reports/` - 開発報告書
- `archive/legacy_code/` - レガシーコード

---

## 関連ドキュメント

- [システム概要](../README.md)
- [デプロイメントガイド](../DEPLOYMENT.md)
- [本番環境クイックスタート](../README_PRODUCTION.md)
- [本番ステータス](../PRODUCTION_STATUS.md)
- [replit.md](../replit.md) - プロジェクト設定

---

**Libral Core - Professional Grooming Protocol V1.0**  
**自律運用システム - AMM & CRAD統合完了**
