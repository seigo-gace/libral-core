---
title: "SelfEvolution API リファレンス（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# SelfEvolution API（API_SELFEVOLUTION）

このドキュメントは、`docs/INDEX.md` の **SelfEvolution API** エントリに対応するテンプレートです。
LPO / KBE / AEG / Vaporization など SelfEvolution 系モジュール向け API をここに集約します。

## 1. エンドポイント一覧（ドラフト）

- `GET /api/selfevolution/status`
- `POST /api/selfevolution/tasks`

> TODO: 実装に合わせて全エンドポイントとペイロード形式を網羅する。

## 2. モジュール連携

- LPO: プロトコル最適化・ヘルススコア取得
- KBE: 知識ベース更新
- AEG: 自動進化ゲートウェイのタスク管理

## 3. セキュリティ

- RBAC / ポリシー定義は `docs/modules/LPO.md` および `SECURITY_POLICY.md` を参照。

