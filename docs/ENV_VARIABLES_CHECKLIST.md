# 環境変数チェックリスト — 動かすために必要なもの

`libral-core/.env.example` と現状コードを照合した結果です。

---

## 1. Node.js（Fastify）サーバー用（リポジトリルート or `server/` で参照）

| 変数名 | 必須 | デフォルト | 参照箇所 | 備考 |
|--------|------|------------|----------|------|
| **PORT** | 任意 | `5000` | server/index.ts | Fastify の listen ポート |
| **NODE_ENV** | 任意 | - | server/index.ts, vite.ts, python-client.ts | `development` で Vite / ログ有効 |
| **TELEGRAM_BOT_TOKEN** | **実運用で必須** | `mock_token` | server/services/telegram.ts | 未設定時はモックのまま動作するが本番では必須 |
| **DATABASE_URL** | 任意 | - | server/db.ts | 未設定時は `pool`/`db` が null で起動可能。将来 DB ストレージに切り替える場合は設定すること |
| **REDIS_URL** | 任意 | - | server/services/redis.ts | 未設定時はインメモリモック。設定時は実 Redis に接続（本番推奨） |
| **LIBRAL_PYTHON_URL** | 任意 | 空 | server/core/ai-bridge/python-client.ts, server/modules/oss-manager.ts | Python (libral-core) のベース URL。例: `http://localhost:8000` |
| **LIBRAL_PYTHON_TIMEOUT_MS** | 任意 | `5000` (1〜30s) / oss-manager は 60s | server/core/ai-bridge/python-client.ts, server/modules/oss-manager.ts | Python /health および infer_local のタイムアウト（ミリ秒） |
| **LIBRAL_INTERNAL_SECRET** | 任意 | 空 | server/modules/oss-manager.ts | 本番で infer_local を内部のみに制限する場合、Node と Python で同じ値を設定。設定時は Node が X-Internal-Secret で送信 |
| **VITE_HMR_PORT** | 任意 | - | server/vite.ts | 開発時 Vite HMR 用ポート（指定時のみ使用） |

**Node 側で「動かすために足りない」環境変数（最小構成）**

- 開発: なし（すべてデフォルトで起動可能）
- 本番で Telegram Bot を動かす: **TELEGRAM_BOT_TOKEN**
- 本番で Python 連携を使う: **LIBRAL_PYTHON_URL**（任意）

---

## 2. Python（libral-core）用 — `libral-core/.env.example` との照合

`libral-core/.env.example` にある項目のうち、**動かすために特に重要**なものと、**.env.example に無くコードで参照されているもの**を整理しました。

### 2.1 libral-core で必須 / 推奨（main.py, libral_core/config.py）

| 変数名 | .env.example | コード | 必須度 | 備考 |
|--------|--------------|--------|--------|------|
| **SECRET_KEY** | ✅ あり | main.py で未設定時は起動失敗 | **必須** | 本番では必ず変更 |
| **PORT** | ✅ 8000 | main.py (uvicorn) | 推奨 | Python サーバーのポート。Node の PORT(5000) と別 |
| **HOST** | ✅ 0.0.0.0 | main.py | 任意 | |
| **DATABASE_URL** | ✅ postgresql+asyncpg://... | config: database_url | 推奨 | PostgreSQL。Node とは別DB可 |
| **REDIS_URL** | ✅ redis://localhost:6379 | config: redis_url | 推奨 | Node 側は現状 Redis 未使用（モック） |
| **TELEGRAM_BOT_TOKEN** | ✅ あり | config: telegram_bot_token | 任意 | Python 側で Telegram 使う場合。Node 側は別途 TELEGRAM_BOT_TOKEN を使用 |
| **TELEGRAM_WEBHOOK_SECRET** | ✅ あり | config: telegram_webhook_secret | 任意 | |
| **TELEGRAM_WEBHOOK_URL** | ✅ あり | .env.example のみ | - | 実装で未参照の可能性あり。Webhook 登録用 URL として記載 |
| **DEBUG** | ✅ false | .env.example | - | config は debug |
| **LOG_LEVEL** | ✅ INFO | .env.example | - | |

### 2.2 .env.example に無いが「動かすために足りない」可能性があるもの（Python）

- 特になし。`libral_core/config.py` は `database_url`, `redis_url`, `secret_key`, `telegram_bot_token` 等で、いずれも .env.example に記載あり（大文字スネークは Pydantic で snake_case にマッピング）。

### 2.3 Node 用で .env.example に無いもの（libral-core は Python 用のため）

Node サーバー用の環境変数は **libral-core/.env.example には含まれていません**（Python 用テンプレートのため）。  
以下は **Node を動かすために必要な／あるとよい環境変数**です。

| 変数名 | 説明 |
|--------|------|
| **PORT** | Fastify の listen ポート（デフォルト 5000） |
| **NODE_ENV** | development / production |
| **TELEGRAM_BOT_TOKEN** | Telegram Bot（Node で Webhook 受信する場合必須） |
| **LIBRAL_PYTHON_URL** | Python (libral-core) の URL（例: http://localhost:8000）。Node の AI-Bridge が /health を叩く場合に使用 |
| **LIBRAL_PYTHON_TIMEOUT_MS** | 上記 /health のタイムアウト（ミリ秒） |
| **DATABASE_URL** | 将来 Node が Drizzle で DB を使う場合に設定（未設定でも起動可） |
| **REDIS_URL** | 本番で実 Redis を使う場合に設定（未設定時はモックで動作） |

---

## 3. 動かすために足りない環境変数 — まとめ

### 3.1 最小限で「Node の Fastify サーバーを動かす」だけ

- **足りない環境変数はなし**。  
  - `PORT` 未設定時は 5000、`TELEGRAM_BOT_TOKEN` 未設定時は `mock_token` で起動する。

### 3.2 Telegram Bot を本番で動かす（Node）

- **TELEGRAM_BOT_TOKEN** を設定する。  
- Webhook URL は `https://<your-domain>/api/telegram/webhook` に設定する（.env に書くかは運用次第）。

### 3.3 Python (libral-core) を動かす

- **SECRET_KEY** を設定する（必須）。  
- 必要に応じて **DATABASE_URL**, **REDIS_URL**, **PORT**(例: 8000) を設定する。

### 3.4 Node と Python を連携させる（AI-Bridge /health）

- Node: **LIBRAL_PYTHON_URL**（例: `http://localhost:8000`）を設定する。  
- Python: 上記と同じホスト/ポートで起動する（例: PORT=8000）。

### 3.5 Redis を本番で使う場合

- **Python**: libral-core/.env.example の **REDIS_URL** を設定。  
- **Node**: **REDIS_URL** を設定するだけで実 Redis に接続する（最適案で対応済み）。

---

## 4. 推奨: ルートに Node 用 .env.example を置く

リポジトリルート（または server で読む場合）に、Node 用の `.env.example` を用意することを推奨します。  
記載内容の例は **ルートの .env.example** に記載済みです。
