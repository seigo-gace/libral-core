# Libral Core — コード分析・脆弱性・依存関係・将来拡張 アップデート提案書

**作成方針:** コードベースの再分析に基づき、脆弱性・依存性・未来拡張のうち**手が届く範囲**の追加開発からテスト・デバッグまで、最先端の知見を反映した提案を行う。

---

## 1. 分析サマリ

| 観点 | 現状 | 判定 |
|------|------|------|
| **API 入力検証** | 多くのルートが `request.body as any` で未検証 | 要対応 |
| **レート制限** | 実装なし（fixtures に設定のみ） | 要対応 |
| **認証・セッション** | 一部 `mock-user-id` 固定。本番では要認証 | 要方針明確化 |
| **CORS** | `origin: true` で全許可 | 本番で要制限 |
| **セキュリティヘッダー** | Helmet 等なし | 推奨 |
| **Node テスト** | server に 2 ファイル（asyncHandler, storage）のみ | 拡充推奨 |
| **E2E / クライアント** | Vitest は server/shared のみ。client 単体・E2E なし | 拡充推奨 |
| **Python** | Pydantic で入力検証。raw SQL の不適切な文字列結合なし | 良好 |
| **依存関係** | package.json / pyproject.toml はキャレット指定。定期的 audit 推奨 | 要運用 |

---

## 2. 脆弱性・セキュリティ

### 2.1 高優先（早めに対応推奨）

| 項目 | 内容 | 提案 |
|------|------|------|
| **API リクエストボディの未検証** | `routes.ts` / `routes/aegis.ts` で `request.body as any` を多用。型・長さ・必須項目が保証されない。 | **Zod スキーマで検証**。既存の `shared/schema.ts`（insertUserSchema 等）を流用するか、ルート用に `z.object({ ... })` を定義し、`preHandler` または Fastify の schema で validate。 **※一部実装済み:** `shared/requestSchemas.ts` に KB/KBE 用スキーマを追加し、`/api/kb/entries`, `/api/kb/entries/:id`, `/api/kb/search`, `/api/kbe/knowledge/submit`, `/api/kbe/knowledge/lookup` で使用。 |
| **レート制限の未実装** | DoS / ブルートフォース対策が無い。 | **@fastify/rate-limit** を導入。グローバル（例: 100 req/min）と、`/api/telegram/webhook` や `/api/ai/*` など重要エンドポイント用に個別制限を検討。 |
| **CORS が全許可** | `origin: true` のため任意オリジンから API 呼び出し可能。 | 本番では `allow_origin` を明示リスト（例: フロントのドメインのみ）に変更。 |

### 2.2 中優先（本番前に推奨）

| 項目 | 内容 | 提案 |
|------|------|------|
| **認証の仮置き** | `userId = "mock-user-id"` 等の固定値。 | 本番では JWT またはセッションから `userId` を取得する層を用意。Telegram 認証と統合する場合は既存の auth フローに合わせる。 |
| **セキュリティヘッダー** | X-Frame-Options, CSP, X-Content-Type-Options 等なし。 | **@fastify/helmet** を導入し、Fastify に register。CSP は段階的に厳格化。 |
| **Webhook 署名検証** | Telegram webhook で `request.body` をそのまま処理。 | Telegraf の `secretToken`（WEBHOOK_SECRET）による検証を有効化し、.env で設定。 |
| **環境変数の露出** | `process.env` はサーバー側のみでクライアントに渡っていない。 | 現状は問題なし。Vite の `import.meta.env` に機密を置かないよう注意。 |

### 2.3 低優先・運用

| 項目 | 内容 | 提案 |
|------|------|------|
| **ログに機密を含めない** | infer_local では prompt をログに出していない（済）。 | 他ルートでも `body` をそのまま log しないようルール化。 |
| **Python** | Pydantic と型付けで入力検証済み。SQL は ORM/パラメータ化想定。 | 新規エンドポイントでも Pydantic を必ず使用。 |

---

## 3. 依存関係

### 3.1 Node (package.json)

- **Fastify 5.x** および **React 18** で現行スタックは妥当。
- **express / express-session / connect-pg-simple** が残っている。実際の HTTP は Fastify なので、未使用なら削除を検討（参照箇所の確認が必要）。
- **推奨運用:** `npm audit` を定期実行し、high/critical を解消。`npm update` は CI で実行し、破壊的変更はテストで検知。

### 3.2 Python (pyproject.toml)

- **FastAPI / Pydantic / uvicorn** は現行の標準的な選択。
- **cryptography / python-jose / passlib** はセキュリティ関連のため、バージョンはセキュリティアドバイザリに従って更新。
- **推奨運用:** `pip audit`（または `safety`）で定期的に脆弱性スキャン。

### 3.3 追加候補（最先端・ベストプラクティス）

| 用途 | パッケージ | 備考 |
|------|------------|------|
| レート制限 | `@fastify/rate-limit` | Fastify v5 対応。グローバル/ルート別設定可能。 |
| リクエスト検証（Zod） | `fastify-type-provider-zod` または `fastify-zod` | 型安全なルート定義と OpenAPI 連携。 |
| セキュリティヘッダー | `@fastify/helmet` | XSS/Clickjacking 等の軽減。 |

---

## 4. 将来拡張（手が届く範囲）

Roadmap（README）の Phase 2 / Phase 3 を前提に、**短期で実装可能**なものを列挙。

### 4.1 短期（1–2 スプリント）

| 項目 | 内容 | 提案 |
|------|------|------|
| **API スキーマ検証** | 全 POST/PUT で body を Zod 検証。 | `shared/schema.ts` に「リクエスト用」の z スキーマを追加し、各ルートで `schema.parse(request.body)` または Fastify schema に組み込む。 |
| **レート制限** | 上記のとおり `@fastify/rate-limit` を導入。 | まずはグローバル 100/min、Webhook は 30/min などから開始。 |
| **ヘルスチェックの一元化** | Node から Python Worker の /health を叩く処理は既存。 | `/api/health` の応答に `python_worker: "ok" | "unreachable"` を追加し、C3 や監視から参照しやすくする。 |
| **Judge トリガー条件のコード化** | README の「スコア < 90 または release-gate」を実装。 | Evaluator または AI Router 内で、スコアとタスク種別に応じて「外部 API を叩くか」を分岐するフラグ/関数を追加。 |

### 4.2 中期（TVFS・拡張テスト）

| 項目 | 内容 | 提案 |
|------|------|------|
| **TVFS 最小索引** | Telegram をベクターストアとして使う設計（README 記載済み）。 | まず「ポインタ表」のスキーマ（kb_id, chat_id, topic_id, message_id, sha256, created_at）を `shared/schema.ts` または Python 側で定義。実ストレージは後からでもよい。 |
| **E2E テスト** | ブラウザから /c3 や /api/modules を叩くテストが無い。 | **Playwright** を導入し、`/api/health` と `/c3` の表示、ログイン不要の主要画面を 1 本だけ E2E でカバー。 |
| **クライアント単体テスト** | Vitest の include が server/shared のみ。 | `client/**/*.test.tsx` を Vitest に追加し、React Testing Library で C3 サイドバーや C3ModuleDetail の表示をテスト。 |

### 4.3 長期（Genetic Mutation・経済エンジン）

- Roadmap の Phase 3 に記載のとおり。ローカルでの変異生成・テスト・Judge 承認のパイプラインは、Worker（Python/Node）と Evaluator の拡張で実装可能。設計は別ドキュメントで詳細化する想定。

---

## 5. テスト・デバッグの強化

### 5.1 現状

- **Node:** `server/utils/asyncHandler.test.ts`, `server/storage.test.ts` の 2 ファイル。Vitest、5s タイムアウト。
- **Python:** pytest、`tests/test_*.py`。`test_tagger.py` で AutoTagger と InferLocalRequest 検証を実施済み。
- **E2E / クライアント:** なし。

### 5.2 提案

| 種別 | 内容 |
|------|------|
| **API ルートの単体テスト** | 重要ルート（`/api/health`, `/api/modules`, `/api/kb/entries`, `/api/oss/models` 等）を Vitest でテスト。`request.body` を Zod で検証するようにした後は、不正 body で 400 が返ることをテスト。 |
| **統合テスト** | Node 起動 → `/api/health` に fetch → 200 と body の `status` を assert。既存の initializeAiModules の「続行」で落ちないことも確認。 |
| **E2E（Playwright）** | 1 本でよいので、`/` → `/c3` → サイドバーに「Active Modules」が表示される流れをテスト。 |
| **デバッグ** | 開発時は `NODE_OPTIONS='--inspect'` や VSCode/Cursor の launch でサーバーを attach。Python は `uvicorn --reload` で再読込。ログは構造化（JSON）にすると CRAD や監視との連携が容易。 |

---

## 6. 実装の優先順位（推奨）

1. **P0（セキュリティ）**  
   - 重要 API（webhook, aegis, kb, ai 系）の **request body を Zod で検証**。  
   - **@fastify/rate-limit** の導入（グローバル + webhook/ai の個別制限）。

2. **P1（本番準備）**  
   - 本番用 **CORS のオリジン制限**。  
   - **@fastify/helmet** の導入。  
   - Telegram webhook の **secretToken 検証** を有効化。

3. **P2（品質・拡張）**  
   - **Judge トリガー条件**のコード化（スコア & release-gate）。  
   - **/api/health** に Python Worker の状態を追加。  
   - **API ルートの Vitest** と **1 本の E2E（Playwright）** 追加。

4. **P3（将来）**  
   - TVFS のポインタ表スキーマ定義と、必要に応じた実装。  
   - クライアントの Vitest 追加（C3 関連コンポーネント）。  
   - Genetic Mutation パイプラインの詳細設計。

---

## 7. 参照（最先端・ベストプラクティス）

- **Fastify:** [Validation and Serialization](https://fastify.io/docs/latest/Reference/Validation-and-Serialization/) — スキーマベース検証の推奨。ユーザー提供スキーマの `new Function()` 利用は避ける。  
- **レート制限:** [@fastify/rate-limit](https://www.npmjs.com/package/@fastify/rate-limit) — Fastify v5 対応。404 も保護する設定を推奨。  
- **Zod 連携:** [fastify-type-provider-zod](https://github.com/fastify/fastify-type-provider-zod) / [fastify-zod](https://www.npmjs.com/package/fastify-zod) — 型安全なルートと OpenAPI 生成。  
- **セキュリティ:** 入力検証・レート制限・ヘッダー hardening の組み合わせで、XSS/インジェクション/DoS を軽減。

---

## 8. 次のアクション（チェックリスト）

- [x] 重要ルートに Zod スキーマを導入し、`request.body` を検証する。（**一部済:** `shared/requestSchemas.ts` で KB/KBE 5 ルートを検証。他ルートは同パターンで拡張可能）  
- [ ] `@fastify/rate-limit` を登録し、グローバルと webhook/ai 用の制限を設定する。  
- [ ] 本番用に CORS の `origin` を制限する。  
- [ ] `@fastify/helmet` を導入する。  
- [ ] Telegram webhook で `secretToken` を設定し、検証を有効化する。  
- [ ] `/api/health` に Python Worker の状態を追加する。  
- [ ] Evaluator / AI Router に「Judge を呼ぶ条件」を実装する。  
- [ ] API ルートの Vitest を 1 本以上追加する。  
- [ ] Playwright で E2E を 1 本追加する。  
- [ ] `npm audit` / `pip audit`（または safety）を CI で回す。  

以上を実施することで、脆弱性の低減・依存関係の可視化・将来拡張（TVFS・Genetic・Judge）への土台が整い、テストとデバッグも手が届く範囲で強化できる。
