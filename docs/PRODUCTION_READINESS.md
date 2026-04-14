# 本番展開チェックリスト・高速稼働基準

Sovereign Autarchy 方針に沿った本番サービス展開前の確認用。  
**保存**: 本ドキュメントおよび関連コードの更新はすべてファイルに保存済みです。

## 高速稼働の条件（基準）

| 項目 | 基準値 | 確認方法 |
|------|--------|----------|
| **API 応答** | ヘルス `/api/health` が 2 秒以内 | `curl -w "%{time_total}" -s -o /dev/null http://localhost:5000/api/health` |
| **起動時間** | Node サーバーが 30 秒以内に listen 開始 | ログで `serving on port` を確認 |
| **メモリ** | 8GB 環境で Node プロセス 500MB 以下推奨 | 本番では `NODE_OPTIONS=--max-old-space-size=512` 等で制限可能 |
| **Python Worker** | `infer_local` がタイムアウト以内に応答（デフォルト 60s） | `LIBRAL_PYTHON_TIMEOUT_MS` で調整 |
| **入力制限** | `infer_local` の prompt 32KB 以下 | 実装で Pydantic `max_length` 済み |

## 起動・稼働テスト手順

### 1. 保存状態・ビルド

```bash
# ルートで
npm run check
npm run build
```

### 2. Node 単体起動

```bash
npm run dev
# または本番ビルド後: npm start
```

確認:

- ログに `[REGISTRY] Registered module:` が 2 件以上
- `serving on port 5000`（または PORT の値）
- ブラウザで http://localhost:5000/api/health → `{"status":"healthy"}`

### 3. Python AI モジュール（任意）

```bash
cd libral-core
# 仮想環境推奨
python -m uvicorn libral_core.modules.ai.app:app --host 0.0.0.0 --port 8001
```

別ターミナルで:

```bash
curl -s -X POST http://localhost:8001/api/ai/infer_local \
  -H "Content-Type: application/json" \
  -d "{\"prompt\":\"Hello\"}"
# → {"text":"..."} または [local-llm:not-ready]
```

### 4. Node + Python 連携

`.env` に設定:

```env
LIBRAL_PYTHON_URL=http://localhost:8001
LIBRAL_PYTHON_TIMEOUT_MS=60000
```

Node を起動し、OSS 推論が Python に流れることを確認（ログまたは C3 / Creation モードで実行）。

### 5. 自動テスト

（Node/npm および Python/pip が PATH に入ったターミナルで実行）

```bash
# Node: Vitest（高速・watch なし）
npm run test

# Python: 依存インストール後 pytest（最初の失敗で停止）
cd libral-core && pip install -e . && pytest tests/ -x -q --tb=line
# またはルートから: npm run test:py
```

## 脆弱性対策チェック

| 対策 | 状態 |
|------|------|
| `infer_local` 入力長制限（32KB） | ✅ Pydantic `max_length` |
| `infer_local` 内部呼び出しのみ（本番） | ✅ `LIBRAL_INTERNAL_SECRET` 未設定時は制限なし／設定時は Header 必須 |
| 機密情報のログ出力禁止 | 要コードレビュー（prompt をログに出さない） |
| CORS / 信頼ホスト | 本番では `allow_origins` を絞る |

## 本番展開可否の判定

- 上記「起動・稼働テスト」の 1〜2 が成功し、`npm run test` が通ること
- Python を使う場合は 3〜4 も成功すること
- 本番では `NODE_ENV=production`、必要に応じて `LIBRAL_INTERNAL_SECRET` を設定すること

以上を満たせば、本番サービスとして展開可能とみなす。

---

## 抜け漏れ調査と改善提案（Sovereign Autarchy 完成形）

### 実施済み改善

| 項目 | 内容 |
|------|------|
| **C3 サイドバー** | `client/src/components/dashboard/sidebar.tsx` を `/api/modules` で動的化済み。レジストリに追加したモジュールがメニューに表示される。 |
| **C3 レイアウト** | `client/src/layouts/C3Layout.tsx` を新設し、`/c3` 系ルートでサイドバー＋メインを表示。App のルートを C3Layout でラップ済み。 |
| **サイドバーリンク** | AI Engine → `/creation`、Aegis GPG → `/c3/apps/aegis-pgp` に修正（実在ルートと一致）。 |
| **モジュール詳細** | `c3-module-detail.tsx` に `stamp-creator` を追加。レジストリの stamp-creator をクリックしても NOT FOUND にならない。 |
| **README** | 起動漏れチェックリストを追加。モデル未配置・Python 依存・環境変数を明記。 |
| **models/README** | GGUF の配置手順と curl / huggingface-cli の例を追記。 |

### 今後の推奨

1. **モジュール追加時**: `server/modules/registry.ts` で `registerModule()` するだけで、C3 の「Active Modules」に自動表示される。必要なら `c3-module-detail.tsx` の `moduleConfigs` に当該 ID の説明を追加。
2. **モデル配置**: 初回は `LOCAL_LLM_PATH` 未設定で起動し、`[local-llm:not-ready]` のまま Judge にフォールバックしてもよい。後から GGUF を配置して Worker を有効化可能。
3. **本番**: `LIBRAL_INTERNAL_SECRET` を設定し、`infer_local` を内部呼び出しのみに制限することを推奨。

---

## ⚠️ 起動漏れを防ぐための緊急チェックリスト

コードが揃っていても、以下の準備が抜けていると起動失敗やエラーの原因になります。

| # | 項目 | 対策 |
|---|------|------|
| 1 | **モデルファイル** | `worker.py` は `LOCAL_LLM_PATH`（デフォルト `./models/model.gguf`）を参照。未配置の場合はローカル推論は `[local-llm:not-ready]` となり、**アプリ自体は起動可能**。AI 機能をフルに使う場合は [libral-core/models/README.md](../libral-core/models/README.md) に従い GGUF を配置する。 |
| 2 | **Python 依存** | `cd libral-core && pip install -e .` でインストール。ローカル LLM を使う場合は `pip install llama-cpp-python`（任意）。 |
| 3 | **環境変数** | `.env` を `.env.example` からコピーして作成。`DATABASE_URL` / `REDIS_URL` は未設定でも**起動可能**（メモリストレージ・モック使用）。本番では設定を推奨。 |
| 4 | **C3 サイドバー** | `/api/modules` からモジュール一覧を取得。API が空でもサイドバーは表示され、固定の「AI Engine」「Aegis GPG」＋動的モジュールが表示される。 |
