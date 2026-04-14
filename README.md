# Libral Core v3.1.0 — Sovereign Autarchy

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-brightgreen.svg)](https://nodejs.org/)

## 🌌 Vision: Sovereign Autarchy (完全自給自足)

**「他社AIは、あくまで『監査役』に過ぎない。」**

Libral Core は、外部 API への依存を極限まで排除し、**ローカル環境での「無限の思考」と「完全なプライバシー」**を実現するために設計された自律型マイクロカーネルプラットフォームです。

### 💎 Core Doctrine

1. **Worker (Self)**: 生成・解析・会話はすべて**ローカル LLM (Llama-3 / Mistral)** で実行。思考回数は無制限、コストはゼロ。
2. **Judge (External)**: GPT-4o などの外部 AI は、出力品質が閾値を下回った場合の**「監査（Audit）」**としてのみ使用。
3. **Zero Storage Cost**: Telegram Personal Log Protocol (TPLP) により、Telegram を容量無制限の暗号化ストレージとして活用。

---

## 🗺️ Roadmap: The Path to Sovereignty

### ✅ Phase 1: Genesis (Completed)

- [x] **Micro-Kernel Core**: Node.js & Python Hybrid Architecture.
- [x] **Privacy First**: Aegis-PGP による全データ暗号化と Telegram ログ保存。
- [x] **Real Implementation**: `worker.py` によるローカル推論、`las` による実画像処理の実装。

### 🚧 Phase 2: Independence (Current)

- [ ] **Local-Native Intelligence**: ローカル LLM を標準とし、外部 API 課金を 90% 削減。
- [ ] **TVFS (Telegram Vector File System)**: Telegram Topic をベクターストアとして利用し、外部 DB コストをゼロにする。
- [ ] **Wasm Edge**: 暗号化処理をクライアントサイド（ブラウザ）へ委譲し、サーバー負荷を軽減。

### 🔮 Phase 3: Autarchy (Vision)

- [ ] **Genetic Code Mutation**: Worker がローカルで大量のコード変異を生成し、テスト後に Judge が最終承認。
- [ ] **Sovereign Economic Engine**: 最小サーバーコストを自律サービスで賄う。

---

## 🚀 Setup & Launch (本番起動)

### 1. Prerequisites

- Node.js v20+
- Python 3.11+
- Redis（本番推奨）

### 2. Install

```bash
# Node
npm install

# Python (libral-core)
cd libral-core
pip install -e .
# ローカル LLM を使う場合（任意）: pip install llama-cpp-python
```

### 3. ローカル AI モデルの配置（任意・AI 機能を使う場合）

コードは `LOCAL_LLM_PATH`（デフォルト `./models/model.gguf`）を参照します。モデルがない場合は `[local-llm:not-ready]` となり、Judge 側にフォールバック可能です。

```bash
# libral-core から実行する場合
mkdir -p libral-core/models
# HuggingFace 等から GGUF をダウンロードし、model.gguf として配置
# 例: Llama-3-8B-Instruct-Q4_K_M.gguf を model.gguf にリネーム
```

詳細は [libral-core/models/README.md](libral-core/models/README.md) を参照。

### 4. 環境変数

```bash
cp .env.example .env
# 本番では DATABASE_URL, REDIS_URL を設定推奨。未設定でも起動は可能（メモリ/モック使用）。
# Python 連携: LIBRAL_PYTHON_URL=http://localhost:8001
```

### 5. Launch

```bash
# 開発モード (Frontend + Node Server)
npm run dev

# Python Worker を別途起動する場合
cd libral-core && python -m uvicorn libral_core.modules.ai.app:app --host 0.0.0.0 --port 8001
```

本番ビルド: `npm run build && npm start`

### ⚠️ 起動漏れを防ぐチェックリスト

| 項目 | 対策 |
|------|------|
| **モデルファイル** | `worker.py` は `LOCAL_LLM_PATH`（既定 `./models/model.gguf`）を参照。未配置なら `[local-llm:not-ready]` で起動可。配置手順は [libral-core/models/README.md](libral-core/models/README.md)。 |
| **Python 依存** | `pip install -e .` で基本は入る。ローカル推論のみ追加: `pip install llama-cpp-python`（任意）。 |
| **環境変数** | `DATABASE_URL` / `REDIS_URL` は未設定でも起動可（メモリ/モック）。本番では設定推奨。 |

---

## 📁 プロジェクト構成（LeadMe）

見やすく管理しやすい正式ツリーは **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** を参照してください。

| 役割 | パス | 説明 |
|------|------|------|
| フロント | `client/` | React + Vite（C3 Console・Dashboard） |
| バックエンド | `server/` | Fastify（API・Webhook・モジュール） |
| 共通 | `shared/` | 型・Zod スキーマ（schema.ts, requestSchemas.ts） |
| E2E | `e2e/` | Playwright 稼働テスト |
| ドキュメント | `docs/` | 索引・契約・環境変数・レポート |
| Python コア | `libral-core/` | FastAPI（AI・認証・決済・統合モジュール） |

**テスト**: `npm run test`（Vitest） / `npm run test:e2e`（Playwright・事前にサーバー起動）

---

## 📚 ドキュメント

- **[プロジェクト構成（正式ツリー）](PROJECT_STRUCTURE.md)** — ディレクトリ基準・管理用
- [ドキュメント索引](docs/INDEX.md) — 全ドキュメントの入口
- [起動確認手順](docs/STARTUP_CHECK.md)
- [本番展開・高速稼働基準](docs/PRODUCTION_READINESS.md)
- [環境変数チェックリスト](docs/ENV_VARIABLES_CHECKLIST.md)

---

**Libral Core** — *Privacy First. Zero Waste. World.*
