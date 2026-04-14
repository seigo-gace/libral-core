---
title: "Dashboard & HUD 設計（テンプレート）"
status: "draft"
version: "0.1.0"
last_updated: "2026-02-10"
---

# Dashboard & HUD（Monitor / Control / Creation）

このドキュメントは、`docs/INDEX.md` の **Dashboard & HUD** セクションに対応するテンプレートです。
`/monitor`, `/control`, `/creation` などの画面仕様をここに集約します。

## 1. 画面構成（ドラフト）

- **Monitor Mode (`/monitor`)**
  - システムメトリクスのリアルタイム監視
- **Control Mode (`/control`)**
  - 制御系アクション（再起動・スケーリング等）
- **Creation Mode (`/creation`)**
  - 新規モジュール・ジョブの作成 UI

> TODO: 各画面のコンポーネントツリー・状態遷移図・主要 UX フローを記載する。

## 2. 技術スタック

- フロントエンド: React + TypeScript + Vite
- UI コンポーネント: `client/src/components/ui/*`
- リアルタイム通信: WebSocket (`server/services/websocket.ts`)

## 3. デザインガイドライン（ドラフト）

- ダークテーマ前提、HUD 風の情報配置
- 視認性を重視した色設計（アラート/警告/正常）

> TODO: Figma などのデザインソースへのリンク・トークン設計を追記する。

