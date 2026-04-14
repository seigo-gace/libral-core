# Libral Core - モジュールレジストリ

**最少単位までモジュール化**し、**トラブル検知 → モジュール特定 → 変更**の流れで運用。エラー・破損時は debug より**交換**で対応し、開発の進行に合わせてモジュールを進化・アップデートします。

---

## 運用フロー（3 ステップ）

| ステップ | 内容 |
|----------|------|
| **1. トラブル検知** | ログ・メトリクス・ヘルスチェック・アラートで異常を検知する。**自動debug（CRAD）** はここで動作し、アラートに基づいてリカバリプロトコルを実行する。 |
| **2. モジュール特定** | マニフェスト（`modules.yaml`）と依存関係から、原因となり得る**モジュール ID** を特定する。CRAD の `target_component` やアラート名からも特定可能。 |
| **3. 変更** | **交換**（互換実装に差し替え）／**設定変更**／**バージョンアップ**のいずれかで対応。まず交換で復旧し、取り外したモジュールは後から修正・進化させる。 |

```
[トラブル検知] → [モジュール特定] → [変更（交換/設定/更新）]
       ↑                  ↑                    ↑
  ログ/メトリクス      modules.yaml          MODULE_CONTRACT
  アラート/CRAD       依存関係から特定       に沿った実装に交換
  (自動debug)
```

### 自動debug（CRAD）について

- **Python 側**: `libral-core/src/governance/context_aware_debugger.py` の **CRAD（Context-Aware Recovery & Auto Debugger）** が、Prometheus アラート等に基づいてリカバリプロトコルを自動実行する。
- **役割**: トラブル検知の一環として「アラート → プロトコル実行（スケールアウト・フェイルオーバー等）」を行い、必要に応じて**対象コンポーネント（モジュール）** を特定して変更につなげる。
- Node 側では `/api/health`・モジュールステータス・イベントログで検知し、必要なら CRAD（Python）や手動でモジュール特定 → 変更を行う。

---

## 方針（3 原則）

| 原則 | 内容 |
|------|------|
| **交換優先** | 不具合・破損時は、原因の深掘りより「問題モジュールを互換実装に差し替える」を優先する。 |
| **進化・アップデート** | 開発が進むにつれ、モジュールを個別にバージョンアップし、全体の品質を上げる。 |
| **再利用・ブラッシュアップ** | 一度作ったモジュールはリスト化し、他プロジェクトや新機能で再利用し、フィードバックで磨く。 |

---

## モジュール一覧（開発・再利用用）

マニフェストの詳細は **`docs/modules.yaml`**（機械可読）を参照。ここではレイヤー別の一覧と交換可否を示します。

### Foundation（基盤）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| storage | server/storage.ts | ✅ | 永続化。IStorage 実装を差し替え可能（例: MemStorage → DB）。 |
| shared-schema | shared/schema.ts | ❌ | スキーマ・型。変更時はマイグレーションで整合。 |
| utils-async-handler | server/utils/asyncHandler.ts | ✅ | 非同期ルート用ラッパー。 |
| data-fixtures | server/data/fixtures.ts | ✅ | モックデータ。本番では別データソースに交換。 |

### Transport（通信）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| transport-router | server/core/transport/router.ts | ✅ | 送信ルーティング・フェイルオーバー。 |
| transport-adapter | server/core/transport/adapter.ts | - | TransportAdapter インターフェース定義。 |
| transport-bootstrap | server/core/transport/bootstrap.ts | ✅ | トランスポート初期化。 |
| transport-policy | server/core/transport/policy.ts | ✅ | 送信ポリシー。 |
| adapter-telegram | server/adapters/telegram.ts | ✅ | Telegram 送信。 |
| adapter-email | server/adapters/email.ts | ✅ | メール送信。 |
| adapter-webhook | server/adapters/webhook.ts | ✅ | Webhook 送信。 |

### Services（サービス）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| service-redis | server/services/redis.ts | ✅ | Redis。別インスタンス・モックに交換可。 |
| service-events | server/services/events.ts | ✅ | イベント発行・購読。 |
| service-websocket | server/services/websocket.ts | ✅ | WebSocket ブロードキャスト。 |
| service-telegram | server/services/telegram.ts | ✅ | Telegram Bot Webhook。 |

### Core（AI・暗号）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| ai-bridge | server/core/ai-bridge/index.ts | ✅ | AI キュー・リトライ・フォールバック。 |
| ai-bridge-queue | server/core/ai-bridge/queue.ts | ✅ | AI リクエストキュー。 |
| ai-router | server/core/ai-router.ts | ✅ | AI ルーティング。 |
| crypto-aegis-client | server/crypto/aegisClient.ts | ✅ | Aegis-PGP クライアント。 |

### Registered Modules（登録モジュール）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| module-registry | server/modules/registry.ts | ✅ | モジュール登録・取得。registerModule で追加。 |
| module-stamp-creator | server/modules/stamp-creator.ts | ✅ | スタンプ作成（StampModule）。 |
| module-aegis-pgp | server/modules/aegis-pgp.ts | ✅ | Aegis-PGP（StampModule）。 |
| module-kb-system | server/modules/kb-system.ts | ✅ | 独立 KB。 |
| module-evaluator | server/modules/evaluator.ts | ✅ | AI 評価。 |
| module-oss-manager | server/modules/oss-manager.ts | ✅ | OSS モデル。 |
| module-embedding | server/modules/embedding.ts | ✅ | 埋め込み・類似検索。 |

### Routes（API）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| routes-main | server/routes.ts | ✅ | 全ルート登録。ドメイン別に分割可。 |
| routes-aegis | server/routes/aegis.ts | ✅ | Aegis API。 |

### Runtime（起動）

| ID | パス | 交換 | 説明 |
|----|------|:----:|------|
| server-index | server/index.ts | ❌ | エントリ。 |
| vite | server/vite.ts | ✅ | Vite ミドルウェア・静的配信。 |

---

## 交換の手順（「モジュール特定 → 変更」の具体）

1. **トラブル検知**  
   ログ・メトリクス・アラートで異常を検知。CRAD が動いていればアラートに応じたリカバリが走る。
2. **モジュール特定**  
   `docs/modules.yaml` または上表で、原因となり得る**モジュール ID** と `interface` を確認する。依存関係から「どのモジュールを差し替えればよいか」を決める。
3. **契約の確認**  
   `docs/MODULE_CONTRACT.md` で、そのモジュールが実装すべきインターフェースを確認する。
4. **変更（交換）**  
   同じインターフェースを満たす別実装を用意し、インポート元または `registerModule` で差し替える。
5. **動作確認**  
   依存しているルート・サービスが期待どおり動くか確認。解消していれば旧実装は後から修正・バージョンアップ（デバッグはここで）。

**流れのまとめ: 検知 → 特定 → 変更。自動debug（CRAD）は検知〜リカバリまで。変更は主に「交換」で行う。**

---

## 進化・アップデートの流れ

1. **マニフェストの更新**  
   モジュールを追加・削除・分割したら、`docs/modules.yaml` の該当レイヤーにエントリを追加・修正し、`version` を上げる。
2. **インターフェースの維持**  
   既存モジュールを「進化」させる場合、**同じ ID・同じ interface を維持**すると、交換がしやすい。破壊的変更が必要な場合は新 ID（例: `storage-v2`）を用意し、レジストリで切り替え可能にする。
3. **再利用**  
   他プロジェクト（MultiPost, TSC, kb-system など）で使う場合は、`modules.yaml` の `path` を参照し、必要なモジュールだけコピーまたはパッケージ化して利用する。改善したらコア側にフィードバック（PR やバージョン bump）する。
4. **リストの活用**  
   新機能開発時は「既存モジュールで足りるか」をこの一覧で確認し、足りない部分だけ新規モジュールとして追加してから、再度マニフェストに載せる。

---

## クライアント・他リポジトリ

- **client/** はページ・コンポーネント単位でモジュール化されている。必要なら `modules.yaml` に `client_modules` を追加し、同様にリスト化・交換可能にできる。
- **Python 側**: **`libral-core/docs/modules.yaml`** と **`libral-core/docs/MODULE_REGISTRY.md`** で同じフロー（トラブル検知 → モジュール特定 → 変更）・一覧を管理。**CRAD（自動debug）** は Python の `libral-core/src/governance/context_aware_debugger.py` に実装。

---

## 関連ドキュメント

- **`docs/modules.yaml`** — 機械可読なモジュール一覧（CI・ツール用）。`flow` でトラブル検知〜変更の3ステップを定義。
- **`docs/MODULE_CONTRACT.md`** — 交換に必要なインターフェース（IStorage, TransportAdapter, StampModule 等）の説明。
- **`PROJECT_STRUCTURE.md`** — プロジェクト全体のディレクトリ構成。
- **Python**: `libral-core/docs/modules.yaml`, `libral-core/docs/MODULE_REGISTRY.md`

更新のたびに **モジュールをリスト化し、交換で切り替え、進化させながら構成を上げる** 運用にすると、保守性と再利用性が上がります。
