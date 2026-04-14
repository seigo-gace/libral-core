---
title: "開発環境セットアップガイド（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# 開発環境セットアップ（Node + Python）

このドキュメントは、`docs/INDEX.md` の **DEVELOPMENT.md** エントリに対応するテンプレートです。
実際の開発フローに合わせて、後から具体的な手順を追記してください。

## 1. 前提環境

- Node.js (LTS)
- Python 3.11+
- Docker / Docker Compose（任意）

## 2. セットアップ手順（ドラフト）

```bash
cd libral-core_riplit
npm install
npm run dev
```

```bash
cd libral-core_riplit/libral-core
pip install -e .
uvicorn main:app --reload
```

> TODO: 実際のコマンド・依存関係・推奨ツールチェーンを正確に記載する。

## 3. 開発フロー

- ブランチ戦略、コードスタイル、テストポリシーなどをここに整理する。

