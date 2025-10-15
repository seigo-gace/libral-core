# Libral Core v3.0.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-brightgreen.svg)](https://nodejs.org/)

## 📖 概要

**Libral Core**は、プライバシーファーストのマイクロカーネルプラットフォームです。企業グレードの暗号化操作とユーザーデータ主権を実現します。Telegramパーソナルログサーバーを活用した、**中央集約型ストレージゼロ**のユニークなアーキテクチャを採用しています。

### 主要機能

- 🔒 **プライバシーファースト**: ゼロ中央ストレージモデル、ユーザーデータはGPG暗号化され、ユーザー管理のTelegramサーバーに保存
- 🔌 **マイクロカーネル設計**: モジュラー、ホットスワップ可能なコンポーネントによるランタイムでの動的なロード/アンロード
- 🤖 **AI並列化**: Gemini（速度重視）とGPT（複雑性重視）による二重検証モード
- 🛡️ **Aegis-PGP暗号化**: 企業グレードのGPG実装（RSA-4096、ED25519、ECDSA-P256対応）
- 📡 **マルチトランスポート通信**: Telegram、Email、Webhookによるインテリジェントなフェイルオーバー
- 🔄 **SelfEvolution自律システム**: 自己修復、継続的改善、予測的監視

## 🏗️ システムアーキテクチャ

### 技術スタック

- **バックエンドコア**: Node.js/Express (TypeScript) - REST API & WebSocket
- **高度なモジュール**: Python/FastAPI - 暗号化操作 & AI処理
- **フロントエンド**: React (TypeScript) + Vite + Shadcn/UI
- **データベース**: PostgreSQL (Neon) + Drizzle ORM
- **キャッシュ/Pub-Sub**: Redis
- **決済**: PayPal Server SDK, Telegram Stars

### システムコンポーネント

#### 🎮 C3 Console (Context Command Center)

**3つの操作モード:**
- **Monitor Mode** (`/monitor`): リアルタイムシステムヘルスダッシュボード
- **Control Mode** (`/control`): クリティカル操作のための実行パネル
- **Creation Mode** (`/creation`): AIアシスタント「月の光」とのChatOps開発

**C3ダッシュボード** (`/c3`):
- **Main Dashboard**: 幾何学的ドアアニメーション、デュアルナビゲーション
- **Apps & Features** (`/c3/apps`): 自動生成モジュール管理UI、リアルタイムステータス
- **Console Menu** (`/c3/console`): システム監視、二重確認ロジック付きクリティカル操作
- **Module Detail Pages** (`/c3/apps/:moduleId`): 各モジュールの動的生成詳細ページ

#### 🤖 AI並列化システム

**AI Bridge Layer:**
- 非同期キューコントローラー
- 自動フォールバックチェーン（Gemini → GPT5-mini → OSSモデル）
- リトライロジック、優先度ベースルーティング

**Evaluator 2.0:**
- 多基準評価（精度、一貫性、関連性、倫理性、完全性）
- 90点閾値での自動再生成
- KB統合、ハルシネーション検出

**OSS Manager:**
- 動的モデルロード（LLaMA3、Mistral、Falcon、Whisper、CLIP）
- メモリ効率的な自動アンロード
- カテゴリベース管理

**AI Router:**
- タスクタイプに基づくインテリジェントルーティング
- 負荷分散、パフォーマンス監視

**Embedding Layer:**
- 384次元ベクトル埋め込み生成
- コサイン類似度検索
- FAISS + ChromaDB対応基盤

#### 🔐 Aegis-PGP暗号化モジュール (Python/FastAPI)

- 企業グレードGPG（Modern Strong、Compatibility、Backup Longtermポリシー）
- Context-Lock署名、RSA-4096、ED25519、ECDSA-P256対応
- WKD統合

#### 📡 マルチトランスポート通信システム

- Telegram、Email、Webhook横断のインテリジェントメッセージルーティング
- ヘルスチェック、優先度ベースルーティング
- 暗号化ペイロード配信

#### 📝 パーソナルログサーバーシステム

- ユーザー管理のTelegram Supergroupsで、GPG暗号化されたアクティビティログを保存
- ユーザー管理のデータ保持、ハッシュタグフィルタリング
- 中央データストレージゼロ

#### 🔄 SelfEvolution自律システム

1. **LPO (Libral Protocol Optimizer)**
   - 自律監視、ヘルススコアリング、ZK監査
   - 自己修復AI、財務最適化、RBAC抽象化
   - 予測的監視

2. **KBE (Knowledge Booster Engine)**
   - プライバシーファーストの集合知
   - 連合学習、準同型集約、匿名知識投稿
   - 独立KB システム + Web UI (`/kb-editor`)

3. **AEG (Auto Evolution Gateway)**
   - AI駆動の開発優先順位付け
   - GitHub PR生成、タスク管理

4. **Vaporization Protocol**
   - プライバシーファーストのキャッシュ管理
   - Redis TTL強制、KBEフラッシュフック
   - 個人データのパターン保護

## 📂 プロジェクト構成

```
libral-core/
├── client/                    # フロントエンド (React + TypeScript)
│   ├── src/
│   │   ├── api/              # API クライアント (aeg, ai, kbe, lpo, etc.)
│   │   ├── components/       # Reactコンポーネント
│   │   │   ├── dashboard/    # ダッシュボード関連コンポーネント
│   │   │   ├── payment/      # 決済UIコンポーネント
│   │   │   └── ui/           # Shadcn UIコンポーネント
│   │   ├── hooks/            # カスタムフック (use-websocket, use-toast)
│   │   ├── pages/            # ページコンポーネント
│   │   │   ├── c3-dashboard.tsx      # C3メインダッシュボード
│   │   │   ├── c3-apps.tsx           # Apps & Features
│   │   │   ├── c3-console.tsx        # Console Menu
│   │   │   ├── c3-module-detail.tsx  # モジュール詳細ページ
│   │   │   ├── Monitor.tsx           # モニターモード
│   │   │   ├── Control.tsx           # コントロールモード
│   │   │   ├── Creation.tsx          # クリエーションモード
│   │   │   └── kb-editor.tsx         # KBエディタ
│   │   └── lib/              # ユーティリティ
│   └── index.html
│
├── server/                    # バックエンド (Node.js + Express)
│   ├── adapters/             # 通信アダプター
│   │   ├── email.ts          # Emailアダプター
│   │   ├── telegram.ts       # Telegramアダプター
│   │   └── webhook.ts        # Webhookアダプター
│   ├── core/                 # コアシステム
│   │   ├── ai-bridge/        # AIブリッジレイヤー
│   │   │   ├── index.ts      # メインブリッジ
│   │   │   └── queue.ts      # 非同期キュー
│   │   ├── transport/        # マルチトランスポートシステム
│   │   │   ├── adapter.ts    # トランスポートアダプター
│   │   │   ├── bootstrap.ts  # ブートストラップ
│   │   │   ├── policy.ts     # ルーティングポリシー
│   │   │   └── router.ts     # メッセージルーター
│   │   └── ai-router.ts      # AIルーター
│   ├── crypto/               # 暗号化モジュール
│   │   └── aegisClient.ts    # Aegis-PGPクライアント
│   ├── modules/              # ホットスワップモジュール
│   │   ├── aegis-pgp.ts      # Aegis-PGP統合
│   │   ├── kb-system.ts      # 独立KBシステム
│   │   ├── evaluator.ts      # Evaluator 2.0
│   │   ├── oss-manager.ts    # OSSモデルマネージャー
│   │   ├── embedding.ts      # 埋め込みレイヤー
│   │   ├── registry.ts       # モジュールレジストリ
│   │   └── stamp-creator.ts  # スタンプクリエーター
│   ├── routes/               # APIルート
│   │   ├── aegis.ts          # Aegis-PGPルート
│   │   └── routes.ts         # メインルート
│   ├── services/             # サービスレイヤー
│   │   ├── events.ts         # イベントバス
│   │   ├── redis.ts          # Redis pub/sub
│   │   ├── telegram.ts       # Telegramサービス
│   │   └── websocket.ts      # WebSocketサービス
│   ├── db.ts                 # データベース接続
│   ├── index.ts              # サーバーエントリーポイント
│   ├── routes.ts             # APIルート定義
│   └── storage.ts            # ストレージインターフェース
│
├── libral-core/              # Pythonモジュール (FastAPI)
│   ├── libral_core/
│   │   ├── integrated_modules/  # 統合モジュール
│   │   │   ├── las/          # Libral Auth System
│   │   │   ├── leb/          # Libral Event Bus
│   │   │   ├── lgl/          # Libral GPG Layer
│   │   │   └── lic/          # Libral Integration Core
│   │   ├── library/          # 共有ライブラリ
│   │   │   ├── api_clients/  # APIクライアント
│   │   │   ├── file_handlers/ # ファイルハンドラー
│   │   │   └── utils/        # ユーティリティ
│   │   └── modules/          # コアモジュール
│   │       ├── ai/           # AI統合
│   │       ├── gpg/          # Aegis-PGP
│   │       ├── auth/         # 認証
│   │       ├── communication/ # 通信
│   │       ├── events/       # イベント管理
│   │       ├── marketplace/  # プラグインマーケットプレイス
│   │       └── payments/     # 決済
│   └── src/
│       ├── governance/       # ガバナンスシステム
│       │   ├── autonomous_moderator.py
│       │   └── context_aware_debugger.py
│       └── modules/          # SelfEvolutionモジュール
│           ├── lpo/          # Protocol Optimizer
│           ├── kbe/          # Knowledge Booster
│           ├── aeg/          # Evolution Gateway
│           └── vaporization/ # キャッシュ管理
│
├── shared/                   # 共有型定義
│   └── schema.ts             # データベーススキーマ & Zod検証
│
├── docs/                     # ドキュメント
│   ├── modules/              # モジュール別ドキュメント
│   ├── INDEX.md              # ドキュメント索引
│   └── *.md                  # 各種ドキュメント
│
└── archive/                  # アーカイブファイル
```

## 🚀 セットアップ

### 前提条件

- Node.js 20+
- Python 3.11+
- PostgreSQL (Neon)
- Redis
- Git

### インストール

1. **リポジトリのクローン**
```bash
git clone https://github.com/yourusername/libral-core.git
cd libral-core
```

2. **Node.js依存関係のインストール**
```bash
npm install
```

3. **Python依存関係のインストール**
```bash
cd libral-core
pip install -e .
```

4. **環境変数の設定**
```bash
cp .env.example .env
# .env ファイルを編集して必要な環境変数を設定
```

必要な環境変数:
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_SECRET=...
```

5. **データベースのセットアップ**
```bash
npm run db:push
```

### 起動

**開発モード:**
```bash
npm run dev
```

**本番モード:**
```bash
npm run build
npm start
```

## 📡 API エンドポイント

### Knowledge Base (KB)
- `GET /api/kb/stats` - KBシステム統計
- `POST /api/kb/entries` - KB エントリー作成
- `GET /api/kb/entries` - KB エントリー一覧
- `GET /api/kb/entries/:id` - 特定エントリー取得
- `PUT /api/kb/entries/:id` - エントリー更新
- `DELETE /api/kb/entries/:id` - エントリー削除
- `POST /api/kb/search` - KB検索

### AI モジュール
- `POST /api/evaluator/evaluate` - AI出力評価
- `GET /api/evaluator/stats` - Evaluator統計
- `GET /api/oss/models` - OSSモデル一覧
- `POST /api/oss/models/:id/load` - モデルロード
- `POST /api/ai-router/route` - AIリクエストルーティング
- `POST /api/embedding/generate` - 埋め込み生成
- `POST /api/embedding/search` - 類似埋め込み検索

### システム
- `GET /api/system/metrics` - システムメトリクス
- `POST /api/telegram/webhook` - Telegram Webhook
- `GET /api/transport/status` - トランスポートシステムステータス

## 📚 モジュールドキュメント

### コアモジュール
- [Aegis-PGP 暗号化モジュール](./docs/modules/AEGIS_PGP.md)
- [AI統合システム](./docs/modules/AI_SYSTEM.md)
- [マルチトランスポート通信](./docs/modules/COMMUNICATION.md)
- [パーソナルログサーバー](./docs/modules/PERSONAL_LOG.md)

### SelfEvolution システム
- [LPO (Protocol Optimizer)](./docs/modules/LPO.md)
- [KBE (Knowledge Booster Engine)](./docs/modules/KBE.md)
- [AEG (Evolution Gateway)](./docs/modules/AEG.md)
- [Vaporization Protocol](./docs/modules/VAPORIZATION.md)

### UI/UXシステム
- [C3 Console](./docs/UI_C3_CONSOLE.md)
- [Dashboard HUD](./docs/UI_DASHBOARD.md)
- [決済システム](./docs/PAYMENT_SYSTEM.md)

### 開発ガイド
- [開発環境セットアップ](./docs/DEVELOPMENT.md)
- [モジュール作成ガイド](./docs/MODULE_CREATION.md)
- [APIリファレンス](./docs/API_REFERENCE.md)

📋 **ドキュメント索引**: [docs/INDEX.md](./docs/INDEX.md)

## 🔒 セキュリティ

### 暗号化標準
- **暗号化**: AES-256-OCB
- **ハッシュ**: SHA-256、SHA-512
- **鍵交換**: RSA-4096、ED25519、ECDSA-P256
- **MAC**: HMAC-SHA256

### セキュリティ機能
- XSS保護
- SQLインジェクション防止
- レート制限
- CSPヘッダー
- GPG暗号化された監査証跡
- GDPR準拠設計
- ユーザーデータのエクスポート/削除機能

## 🧪 テスト

```bash
# すべてのテストを実行
npm test

# 特定のテストスイート
npm test -- --grep "KB System"

# E2Eテスト
npm run test:e2e
```

## 📊 開発進捗

### ✅ 完了 (v3.0)

**コアインフラ**
- [x] マイクロカーネルアーキテクチャ
- [x] PostgreSQLデータベーススキーマ (Drizzle ORM)
- [x] Redis pub/subシステム
- [x] WebSocketリアルタイム更新
- [x] マルチトランスポート通信システム

**AI モジュール**
- [x] KBシステム独立化 (80+言語対応)
- [x] AI Bridge Layer（フォールバックチェーン）
- [x] Evaluator 2.0（90点閾値）
- [x] OSS Manager（動的モデルロード）
- [x] AI Router（インテリジェントルーティング）
- [x] Embedding Layer（384次元ベクトル）

**UI/UX**
- [x] C3 Console Dashboard (`/c3`)
- [x] Monitor/Control/Creationモード
- [x] KB Editor Web UI (`/kb-editor`)
- [x] 自動生成モジュール管理UI

**セキュリティ & プライバシー**
- [x] Aegis-PGP暗号化モジュール
- [x] GPG暗号化統合
- [x] パーソナルログサーバーシステム
- [x] ゼロ中央ストレージアーキテクチャ

### 🔄 進行中

**SelfEvolution システム**
- [ ] LPO完全実装
- [ ] KBE連合学習
- [ ] AEG自動PR生成
- [ ] Vaporizationプロトコル

**ベクトルデータベース統合**
- [ ] FAISS統合
- [ ] ChromaDB永続化
- [ ] シミュレーションから実埋め込みへの移行

**決済統合**
- [ ] Telegram Stars決済フロー
- [ ] PayPal Server SDK統合
- [ ] トランザクションGPG暗号化

## 🤝 コントリビューション

コントリビューションを歓迎します！詳細は[コントリビューションガイドライン](CONTRIBUTING.md)を参照してください。

### 開発ワークフロー

1. リポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📝 ライセンス

このプロジェクトはMITライセンスの下でライセンスされています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 🙏 謝辞

- **Neon Database** - サーバーレスPostgreSQL
- **Replit** - 開発・デプロイプラットフォーム
- **Telegram** - Bot API & パーソナルログサーバー
- **OpenAI & Google** - AIモデルアクセス

## 📞 サポート

サポートが必要な場合:
- GitHubでIssueを開く
- コミュニティDiscordに参加
- Email: support@libralcore.dev

## 🔗 リンク

- **ドキュメント**: [docs/INDEX.md](./docs/INDEX.md)
- **モジュール一覧**: [docs/APPS_MODULES.md](./docs/APPS_MODULES.md)
- **技術アーキテクチャ**: [replit.md](./replit.md)

---

**Built with ❤️ by the Libral Core Team**

*ユーザーにプライバシー、主権、AI駆動の自動化を提供*
