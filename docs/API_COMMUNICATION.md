---
title: "Communication API リファレンス（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# Communication API（API_COMMUNICATION）

このドキュメントは、`docs/INDEX.md` の **Communication API** エントリに対応するテンプレートです。
マルチトランスポート通信モジュール（`docs/modules/COMMUNICATION.md`）の外部公開 API をここに整理します。

## 1. エンドポイント一覧（ドラフト）

- `POST /api/communication/send`
- `GET /api/communication/status`

> TODO: 実装に合わせてリクエスト/レスポンススキーマ・エラーコードを追記する。

## 2. 実装ポイント

- トランスポート種別（Telegram / Email / Webhook）を抽象化したパラメータ設計
- 非同期キューやリトライ処理の扱い

## 3. 関連ドキュメント

- `docs/modules/COMMUNICATION.md`
- `docs/MODULE_REGISTRY.md`

