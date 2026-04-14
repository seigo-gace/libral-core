# リファクタリング後 整合性検証レポート

**検証日**: 2026-02-10  
**対象**: libral-core_riplit（Fastify/Telegraf リファクタ後）

---

## 1. Node.js と Python 間の型定義

### 1.1 現状

| 項目 | Node.js | Python (libral-core) | 整合性 |
|------|---------|----------------------|--------|
| **データベース** | 未使用（MemStorage） | PostgreSQL (asyncpg) | 別系統のため競合なし |
| **共有API** | Node → Python は `/health` のみ | FastAPI `GET /health` | ✅ 整合 |
| **Health レスポンス** | `PythonHealthResponse`: `status`, `version?`, `architecture?`, `modules?`（各 `status`, `description?`） | 実装は `status`, `version`, `architecture`, `modules`（各 `status`, `description`） | ✅ 型を揃えて整合 |

**結論**: Node が Python を呼ぶのは AI-Bridge の `checkPythonHealth()` のみ。レスポンスは `status === "healthy"` で判定しており、型のズレは実害なし。将来 API を増やす場合は OpenAPI や共有型生成の検討を推奨。

### 1.2 型のずれが起きうる箇所（将来）

- Node と Python で同一の「ユーザー」「取引」スキーマを共有する場合、現状は **共有定義がない**（Node: `@shared/schema`, Python: 各モジュール内モデル）。同一 DB を共有する場合は Drizzle スキーマと Python モデルの同期が必要。

---

## 2. DB 接続とデッドロック

### 2.1 Node.js 側

| コンポーネント | 接続先 | トランザクション/ロック | デッドロックリスク |
|----------------|--------|--------------------------|---------------------|
| **server/db.ts** | `DATABASE_URL` 設定時のみ Pool 作成 | 単一 `Pool`、未設定時は `pool`/`db` が null（起動時エラーにしない最適案） | 現状未使用。将来使用時は `db !== null` を確認すること |
| **server/storage.ts** | なし（MemStorage = インメモリ Map） | ロックなし、同期的 Map 操作 | なし |
| **server/services/redis.ts** | `REDIS_URL` 設定時は実 Redis、未設定時はインメモリモック | 実接続時は publish/subscribe で別接続を利用 | なし |

**結論**: 現時点で Node は DB に接続しておらず、デッドロックの可能性はない。`db.ts` は `DATABASE_URL` 未設定でも起動可能（最適案）。Redis は `REDIS_URL` 設定で本番用実接続に切り替わる。

### 2.2 Python 側

- `libral_core/config.py`: `database_url`, `redis_url` を参照。
- 各モジュールで DB/Redis 利用有無は未精査だが、通常は非ブロッキング（asyncpg 等）のため、同一プロセス内で適切に await していればデッドロックは起きにくい。
- **Node と Python は別プロセス・別DB**のため、跨るデッドロックは存在しない。

### 2.3 推奨（将来 DB を Node で使う場合）

- トランザクションは `db.transaction()` で短く保ち、長時間ロックを避ける。
- Redis を本番で使う場合は `REDIS_URL` を設定し、接続プール・タイムアウトを設定すること。

---

## 3. プロジェクト横断チェック

| チェック項目 | 結果 |
|--------------|------|
| Fastify 起動 (index.ts) | ✅ `registerRoutes(fastify)` でルート登録、listen 後に WebSocket 初期化 |
| ルートの一貫性 | ✅ `request` / `reply`、`reply.send()` に統一 |
| Telegraf Webhook | ✅ `processWebhook(update)` → `bot.handleUpdate(update)`、同一 Update 型 |
| Aegis ルート | ✅ Fastify 化済み、`request.body` / `request.query` 使用 |
| Vite / 静的配信 | ✅ 開発時 `setupVite(app)`、本番時 `serveStatic(app)`（@fastify/static） |
| エラーハンドリング | ✅ `setErrorHandler` で共通処理 |
| API 計測 | ✅ `onResponse` フックで `/api/*` のみ storage / eventService に記録 |

---

## 4. 環境変数（要約）

- **Node で必須**: なし（PORT はデフォルト 5000）。本番で DB を使う場合は `DATABASE_URL` が必要になる可能性あり。
- **Node で推奨**: `TELEGRAM_BOT_TOKEN`, `PORT`, `NODE_ENV`。Python 連携時は `LIBRAL_PYTHON_URL`。
- **Python (libral-core)**: `libral-core/.env.example` 参照。`SECRET_KEY` は main.py で必須。

詳細は **「足りない環境変数リスト」** を参照。
