---
title: "Knowledge Base API リファレンス（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# Knowledge Base API（API_KB）

このドキュメントは、`docs/INDEX.md` の **Knowledge Base API** エントリに対応するテンプレートです。
KBE / KB Editor (`/kb-editor`) まわりの HTTP / WebSocket API をここに集約します。

## 1. エンドポイント一覧（ドラフト）

- `GET /api/kb/documents`
- `POST /api/kb/documents`
- `GET /api/kb/documents/:id`

> TODO: 実装に合わせてエンドポイント・クエリパラメータ・レスポンススキーマを正確に記載する。

## 2. 認可・レートリミット

- 認可方式（JWT / セッション / API キー等）をここで定義。
- 高頻度アクセスに対するレートリミット戦略を明文化する。

## 3. 関連ドキュメント

- `docs/modules/KBE.md`
- `docs/ENV_VARIABLES_CHECKLIST.md`

