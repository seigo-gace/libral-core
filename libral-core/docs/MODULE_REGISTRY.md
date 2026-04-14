# Libral Core (Python) - モジュールレジストリ

**最少単位までモジュール化**し、**トラブル検知 → モジュール特定 → 変更**の流れで運用。エラー・破損時は debug より**交換**で対応し、モジュールを進化・アップデートします。

---

## 運用フロー（3 ステップ）

| ステップ | 内容 |
|----------|------|
| **1. トラブル検知** | ログ・メトリクス・アラートで異常を検知。**CRAD（自動debug）** がアラートに基づいてリカバリプロトコルを実行する。 |
| **2. モジュール特定** | `docs/modules.yaml` と依存関係から**モジュール ID** を特定。CRAD の runbook で `target_component` を指定している場合はそのコンポーネント＝対象モジュール。 |
| **3. 変更** | **交換**（互換実装に差し替え）／**設定変更**／**バージョンアップ**。まず交換で復旧し、取り外したモジュールは後から修正・進化させる。 |

```
[トラブル検知] → [モジュール特定] → [変更（交換/設定/更新）]
       ↑                  ↑                    ↑
  ログ/メトリクス      modules.yaml          同一 interface の
  アラート            依存関係              別実装に差し替え
  CRAD(自動debug)     target_component
```

### 自動debug（CRAD）について

- **ファイル**: `src/governance/context_aware_debugger.py` — **CRAD（Context-Aware Recovery & Auto Debugger）**
- **役割**: Prometheus アラート等に基づき、runbook（`recovery_runbook_crad`）のプロトコルを自動実行。各ステップで `target_component` が「どのモジュールか」を表す。
- **流れ**: アラート受信 → プロトコル選択 → ステップ実行（K8S_SCALE_OUT, HA_FAILOVER 等）→ 必要に応じて**モジュール特定 → 交換**につなげる。
- runbook に「該当モジュールを無効化／代替実装に切り替え」といったアクションを追加すれば、検知から変更まで自動化できる。

---

## 方針（3 原則）

| 原則 | 内容 |
|------|------|
| **交換優先** | 不具合・破損時は、原因の深掘りより「問題モジュールを互換実装に差し替える」を優先。 |
| **進化・アップデート** | モジュールを個別にバージョンアップし、全体の品質を上げる。 |
| **再利用・ブラッシュアップ** | リスト化したモジュールを他プロジェクトで再利用し、フィードバックで磨く。 |

---

## モジュール一覧（開発・再利用用）

詳細は **`docs/modules.yaml`** を参照。ここではレイヤー別に要約します。

### Components（共通部品）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| lib-components | libral_core/library/utils/datetime_utils.py | ✅ | 日時（統合モジュール用） |
| src-components-datetime | src/library/components/datetime_utils.py | ✅ | 日時（プロトコル用） |
| src-components-crypto | src/library/components/crypto_helpers.py | ✅ | 暗号ヘルパー |
| src-components-config | src/library/components/config_loader.py | ✅ | 設定・runbook 読み込み |
| src-components-validators | src/library/components/validators.py | ✅ | バリデーション |

### Governance（自動debug・モデレーション）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| governance-crad | src/governance/context_aware_debugger.py | ✅ | **CRAD - 自動リカバリ・自動debug** |
| governance-amm | src/governance/autonomous_moderator.py | ✅ | AMM - セキュリティ自動執行 |
| governance-router | src/governance/router.py | ✅ | ガバナンス API |

### Integrated（libral_core 統合モジュール）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| mod-ai | libral_core/modules/ai/ | ✅ | AI |
| mod-app | libral_core/modules/app/ | ✅ | アプリ |
| mod-auth | libral_core/modules/auth/ | ✅ | 認証 |
| mod-communication | libral_core/modules/communication/ | ✅ | 通信 |
| mod-events | libral_core/modules/events/ | ✅ | イベント |
| mod-gpg | libral_core/modules/gpg/ | ✅ | GPG |
| mod-marketplace | libral_core/modules/marketplace/ | ✅ | マーケットプレース |
| mod-payments | libral_core/modules/payments/ | ✅ | 決済 |
| mod-api_hub | libral_core/modules/api_hub/ | ✅ | API ハブ |

### Integrated Sub（LAS/LEB/LGL/LIC）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| las | libral_core/integrated_modules/las/ | ✅ | LAS |
| leb | libral_core/integrated_modules/leb/ | ✅ | LEB |
| lgl | libral_core/integrated_modules/lgl/ | ✅ | LGL |
| lic | libral_core/integrated_modules/lic/ | ✅ | LIC |

### Protocol（src プロトコルモジュール）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| aeg | src/modules/aeg/ | ✅ | AEG |
| kbe | src/modules/kbe/ | ✅ | KBE |
| lpo | src/modules/lpo/ | ✅ | LPO |
| vaporization | src/modules/vaporization/ | ✅ | Vaporization |
| integration-api | src/modules/integration_api.py | ✅ | 統合 API |

### Library

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| library-api-clients | libral_core/library/api_clients/ | ✅ | API クライアント |
| library-file-handlers | libral_core/library/file_handlers/ | ✅ | ファイルハンドラ |

---

## 交換の手順（モジュール特定 → 変更）

1. **トラブル検知**  
   ログ・アラートで異常を検知。CRAD が動いていれば runbook に従いリカバリが実行される。
2. **モジュール特定**  
   `docs/modules.yaml` の一覧・依存関係、および CRAD の `target_component` から、対象**モジュール ID** を特定する。
3. **契約の確認**  
   該当モジュールの `interface`（router+service, ConfigLoader 等）を満たす別実装を用意する。
4. **変更（交換）**  
   インポート元やルーター登録を、旧モジュールから新モジュールに差し替える。
5. **動作確認**  
   依存している API・他モジュールが期待どおり動くか確認。解消していれば旧実装は後から修正・バージョンアップ。

**流れのまとめ: 検知 → 特定 → 変更。CRAD（自動debug）は検知〜リカバリ。変更は主に「交換」。**

---

## 関連ドキュメント

- **`docs/modules.yaml`** — 機械可読なモジュール一覧（Python 用）。
- **Node 側**: ルートの `docs/MODULE_REGISTRY.md` および `docs/modules.yaml` で同じフロー（トラブル検知 → モジュール特定 → 変更）を採用。CRAD は Python 側で動作し、Node はヘルス・ログで検知して必要なら CRAD や手動で特定 → 変更する。
