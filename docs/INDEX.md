# Libral Core - ドキュメント索引

すべてのプロジェクトドキュメントを一か所にまとめています。

## 📚 主要ドキュメント

### プロジェクト概要
- [README.md](../README.md) - プロジェクト概要・セットアップ・使い方（日本語）
- [replit.md](../replit.md) - システムアーキテクチャ・技術仕様・設計原則
- [PROJECT_STRUCTURE.md](../PROJECT_STRUCTURE.md) - プロジェクトファイル構造

### アプリケーション・モジュール
- [APPS_MODULES.md](./APPS_MODULES.md) - アプリ・モジュール管理の説明

## 🔐 コアモジュール

### 暗号化・セキュリティ
- [Aegis-PGP 暗号化モジュール](./modules/AEGIS_PGP.md)
  - 企業グレードGPG暗号化
  - Context-Lock署名
  - WKD統合
  - RSA-4096、ED25519、ECDSA-P256対応

### 通信システム
- [マルチトランスポート通信](./modules/COMMUNICATION.md)
  - Telegram、Email、Webhook
  - インテリジェントフェイルオーバー
  - 暗号化ペイロード配信

### パーソナルログ
- [パーソナルログサーバー](./modules/PERSONAL_LOG.md)
  - Telegram Supergroups統合
  - GPG暗号化ログ
  - ハッシュタグフィルタリング

## 🤖 SelfEvolution システム

### LPO (Libral Protocol Optimizer)
- [LPO モジュール](./modules/LPO.md)
  - 自律監視・ヘルススコアリング
  - ZK監査
  - 自己修復AI
  - 財務最適化
  - RBAC抽象化
  - 予測的監視

### KBE (Knowledge Booster Engine)
- [KBE モジュール](./modules/KBE.md)
  - プライバシーファースト集合知
  - 連合学習
  - 準同型暗号化
  - 独立KBシステム（80+言語対応）
  - Web UI (`/kb-editor`)

### AEG (Auto Evolution Gateway)
- [AEG モジュール](./modules/AEG.md)
  - AI駆動の開発優先順位付け
  - GitHub PR自動生成
  - タスク管理
  - 自動コードレビュー
  - 技術的負債追跡

### Vaporization Protocol
- [Vaporization モジュール](./modules/VAPORIZATION.md)
  - プライバシーファーストキャッシュ管理
  - Redis TTL強制
  - KBEフラッシュフック
  - 個人データパターン保護
  - GDPR準拠

## 🎨 UI/UX システム

### C3 Console
- [C3 Console (Context Command Center)](./UI_C3_CONSOLE.md)
  - Main Dashboard (`/c3`)
  - Apps & Features (`/c3/apps`)
  - Console Menu (`/c3/console`)
  - Module Detail Pages (`/c3/apps/:moduleId`)
  - 幾何学的ドアアニメーション
  - 二重確認ロジック

### Dashboard & HUD
- [Dashboard HUD](./UI_DASHBOARD.md)
  - Monitor Mode (`/monitor`)
  - Control Mode (`/control`)
  - Creation Mode (`/creation`)
  - リアルタイムメトリクス
  - WebSocket統合

### 決済システム
- [決済システム](./PAYMENT_SYSTEM.md)
  - Telegram Stars
  - PayPal Server SDK
  - トランザクションGPG暗号化

## 📋 完了レポート

### マイグレーション・戦略
- [LIBRAL_CORE_MIGRATION_STRATEGY.md](./LIBRAL_CORE_MIGRATION_STRATEGY.md)
- [PLUGIN_MARKETPLACE_COMPLETION_REPORT.md](./PLUGIN_MARKETPLACE_COMPLETION_REPORT.md)

### Telegram統合
- [TELEGRAM_PERSONAL_LOG_PROTOCOL.md](./TELEGRAM_PERSONAL_LOG_PROTOCOL.md)
- [TELEGRAM_TOPICS_HASHTAGS_IMPROVEMENT_REPORT.md](./TELEGRAM_TOPICS_HASHTAGS_IMPROVEMENT_REPORT.md)

### 週次完了レポート
- [WEEK_1_COMPLETION_REPORT.md](./WEEK_1_COMPLETION_REPORT.md) - Week 1: 基盤構築
- [WEEK_3_AUTH_COMPLETION_REPORT.md](./WEEK_3_AUTH_COMPLETION_REPORT.md) - Week 3: 認証システム
- [WEEK_4_COMMUNICATION_COMPLETION_REPORT.md](./WEEK_4_COMMUNICATION_COMPLETION_REPORT.md) - Week 4: 通信システム
- [WEEK_5_EVENTS_COMPLETION_REPORT.md](./WEEK_5_EVENTS_COMPLETION_REPORT.md) - Week 5: イベント管理
- [WEEK_6_PAYMENTS_COMPLETION_REPORT.md](./WEEK_6_PAYMENTS_COMPLETION_REPORT.md) - Week 6: 決済システム
- [WEEK_7_API_HUB_COMPLETION_REPORT.md](./WEEK_7_API_HUB_COMPLETION_REPORT.md) - Week 7: APIハブ

## 🛠️ 開発者ガイド

### Python コア (libral-core)
- [LIBRAL_CORE_PYTHON_REFERENCE.md](./LIBRAL_CORE_PYTHON_REFERENCE.md) - Python実装リファレンス

### API リファレンス
- [API_KB.md](./API_KB.md) - Knowledge Base API
- [API_SELFEVOLUTION.md](./API_SELFEVOLUTION.md) - SelfEvolution API
- [API_COMMUNICATION.md](./API_COMMUNICATION.md) - Communication API

### 開発環境
- [DEVELOPMENT.md](./DEVELOPMENT.md) - 開発環境セットアップ
- [MODULE_CREATION.md](./MODULE_CREATION.md) - モジュール作成ガイド
- [TESTING.md](./TESTING.md) - テストガイド

## 🔒 セキュリティ・コンプライアンス

- [SECURITY_POLICY.md](./SECURITY_POLICY.md) - セキュリティポリシー
- [GDPR_COMPLIANCE.md](./GDPR_COMPLIANCE.md) - GDPR準拠ガイド
- [AUDIT_TRAIL.md](./AUDIT_TRAIL.md) - 監査証跡仕様

## 📊 アーキテクチャ図

```
Libral Core v3.0.0
├── Frontend (React + TypeScript)
│   ├── C3 Console (/c3)
│   │   ├── Main Dashboard
│   │   ├── Apps & Features
│   │   ├── Console Menu
│   │   └── Module Details
│   ├── Monitor/Control/Creation Modes
│   └── KB Editor (/kb-editor)
│
├── Backend (Node.js + Express)
│   ├── Multi-Transport Communication
│   ├── AI Bridge Layer
│   ├── Module Registry
│   ├── WebSocket Service
│   └── GPG Crypto Client
│
├── Python Modules (FastAPI)
│   ├── Aegis-PGP
│   ├── SelfEvolution
│   │   ├── LPO (Protocol Optimizer)
│   │   ├── KBE (Knowledge Booster)
│   │   ├── AEG (Evolution Gateway)
│   │   └── Vaporization Protocol
│   └── Integrated Modules
│
└── Infrastructure
    ├── PostgreSQL (Neon)
    ├── Redis (Pub/Sub + Cache)
    ├── Telegram Bot API
    └── Payment Providers
```

## 🔍 検索方法

すべてのmdファイルは`docs/`フォルダに集約されています。

### カテゴリ別検索

**モジュールドキュメント**: `docs/modules/*.md`
**UI/UXドキュメント**: `docs/UI_*.md`
**APIリファレンス**: `docs/API_*.md`
**完了レポート**: `docs/*_COMPLETION_REPORT.md`

### 推奨検索ワード

- **暗号化**: Aegis-PGP, GPG, 暗号化
- **AI**: AI, 機械学習, 連合学習, 埋め込み
- **監視**: LPO, ヘルススコア, メトリクス
- **知識管理**: KBE, KB, Knowledge Base
- **進化**: AEG, 自動PR, タスク管理
- **プライバシー**: Vaporization, GDPR, TTL
- **UI**: C3 Console, Dashboard, HUD
- **通信**: Telegram, Email, Webhook

## 📝 ドキュメント更新履歴

- **2025-10-15**: v3.0.0 - 主要モジュールドキュメント作成、日本語化完了
- **2025-10-01**: v2.1.0 - AI Module Ascension完了
- **2025-09-15**: v2.0.0 - C3 Console実装完了
- **2025-09-01**: v1.0.0 - 初版リリース

## 🆘 サポート

ドキュメントに関する質問や改善提案は、以下の方法でお問い合わせください：

- 📧 Email: docs@libralcore.dev
- 💬 Telegram: @LibralCoreDocs
- 🐛 GitHub Issues: ドキュメント改善提案

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core Documentation Team
