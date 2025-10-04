# Libral Core v2.0

**プライバシー優先のマイクロカーネルプラットフォーム**

G-ACE.inc TGAXIS Libral Platform - 完全なユーザーデータ主権を実現する革新的なプラットフォーム

---

## 🌟 概要

Libral Coreは、**プライバシー優先**の設計思想に基づいた、次世代のマイクロカーネルプラットフォームです。Telegramパーソナルログサーバーを活用し、ユーザーが自分のデータを完全にコントロールできる、革新的なアーキテクチャを提供します。

### ✨ 主な特徴

- **🔐 プライバシー優先**: ユーザーデータの主権を完全に保証
- **🏗️ マイクロカーネル設計**: 独立したモジュールによる柔軟な拡張性
- **📱 Telegram統合**: パーソナルログサーバーによるプライバシー保護
- **🔒 エンタープライズ暗号化**: GPG (SEIPDv2/AES-256-OCB) による強力なセキュリティ
- **🤖 デュアルAIシステム**: 内部AI（1000回/日）+ 外部AI評価（2回/24時間）
- **⚡ 高性能**: PostgreSQL + Redis による最適化されたデータ処理

---

## 📦 アーキテクチャ

### 4+1統合モジュール

Libral Coreは、4つの主要統合モジュール + 1つのガバナンス層で構成されています：

#### 🔑 LIC (Libral Identity Core)
**アイデンティティとセキュリティの基盤**
- GPG暗号化（enterprise-grade）
- 認証システム（Telegram OAuth）
- ゼロ知識証明（ZKP）
- 分散型ID（DID）

#### 🌐 LEB (Libral Event Bus)
**イベント駆動型通信基盤**
- マルチプロトコル通信ゲートウェイ
- リアルタイムイベント管理
- Telegram、Email、Webhook対応
- トピック別メッセージルーティング

#### 📦 LAS (Libral Asset Service)
**アセット管理とWASM実行環境**
- 共通ユーティリティライブラリ
- 画像・動画処理システム
- WebAssembly実行環境
- ファイルハンドリング

#### ⚖️ LGL (Libral Governance Layer)
**ガバナンスとコンプライアンス**
- デジタル署名システム
- トラストチェーン管理
- 監査ログ
- コンプライアンス対応

### 独立マイクロサービス

#### 🤖 AI Module (Port 8001)
**デュアルAIシステム**
- 内部AI: 1000回/日の質問可能
- 外部AI審査: 2回/24時間の高度評価
- Context-Lock認証によるプライバシー保護
- Redis使用量管理

#### 📱 APP Module (Port 8002)
**アプリケーション管理システム**
- 完全なライフサイクル管理（Draft → Active → Paused → Archived）
- PostgreSQL永続ストレージ
- Redis高性能キャッシング
- 6種類のアプリタイプ対応

---

## 🚀 クイックスタート

### 必要環境

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Node.js 18+ (フロントエンド用)

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/G-ACE-inc/libral-core.git
cd libral-core

# Python依存関係のインストール
pip install -r requirements.txt
# または Poetry使用
poetry install

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してデータベースURL等を設定
```

### 基本的な起動方法

#### 1. メインアプリケーション（統合モジュール）

```bash
# Libral Core本体の起動
python main.py
```

統合APIエンドポイント: `http://localhost:8000`

#### 2. AIモジュール（独立サービス）

```bash
# AIモジュールの起動
python -m libral_core.modules.ai.app

# または環境変数で設定
AI_HOST=0.0.0.0 AI_PORT=8001 python -m libral_core.modules.ai.app
```

AIモジュールAPI: `http://localhost:8001`

#### 3. APPモジュール（独立サービス）

```bash
# APPモジュールの起動
python -m libral_core.modules.app.app

# または環境変数で設定
APP_HOST=0.0.0.0 APP_PORT=8002 python -m libral_core.modules.app.app
```

APPモジュールAPI: `http://localhost:8002`

---

## 📚 モジュール一覧

### 統合モジュール（main.pyに統合）

| モジュール | 機能 | 主要API |
|-----------|------|--------|
| **GPG** | エンタープライズ暗号化 | `/api/gpg/*` |
| **Auth** | 認証・認可システム | `/api/auth/*` |
| **Communication** | 通信ゲートウェイ | `/api/communication/*` |
| **Events** | イベント管理 | `/api/events/*` |
| **Payments** | 決済・課金システム | `/api/payments/*` |
| **API Hub** | 外部API統合 | `/api/api-hub/*` |
| **Marketplace** | プラグインマーケット | `/api/marketplace/*` |

### 独立マイクロサービス

| サービス | ポート | 機能 | テストファイル |
|---------|--------|------|------------|
| **AI Module** | 8001 | デュアルAIシステム | `tests/test_ai_module.py` |
| **APP Module** | 8002 | アプリ管理システム | `tests/test_app_module.py` |

---

## 🔧 設定

### 環境変数

主要な環境変数の設定例：

```bash
# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/libral_core
REDIS_URL=redis://localhost:6379

# セキュリティ
SECRET_KEY=your-secret-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# AI Module
AI_INTERNAL_PROVIDER=openai
AI_EXTERNAL_PROVIDER=anthropic
AI_INTERNAL_DAILY_LIMIT=1000
AI_EXTERNAL_DAILY_LIMIT=2

# APP Module
APP_MAX_PER_USER=100
APP_CACHE_TTL_HOURS=24
APP_AUTO_ARCHIVE_DAYS=90
```

詳細は `.env.example` を参照してください。

---

## 🧪 テスト

```bash
# 全テストの実行
cd libral-core
python -m pytest tests/ -v

# 特定モジュールのテスト
python tests/test_ai_module.py
python tests/test_app_module.py
python tests/test_gpg_module.py

# カバレッジレポート付き
python -m pytest --cov=libral_core tests/
```

---

## 🛠️ 開発

### プロジェクト構造

```
libral-core/
├── libral_core/              # Python FastAPIバックエンド
│   ├── modules/              # 9つのコアモジュール
│   │   ├── gpg/             # GPG暗号化
│   │   ├── auth/            # 認証システム
│   │   ├── communication/   # 通信ゲートウェイ
│   │   ├── events/          # イベント管理
│   │   ├── payments/        # 決済システム
│   │   ├── api_hub/         # API統合
│   │   ├── marketplace/     # プラグイン市場
│   │   ├── ai/              # AIモジュール（独立）
│   │   └── app/             # APPモジュール（独立）
│   ├── integrated_modules/  # 4+1統合モジュール
│   │   ├── lic/             # Identity Core
│   │   ├── leb/             # Event Bus
│   │   ├── las/             # Asset Service
│   │   └── lgl/             # Governance Layer
│   └── library/             # 共通ライブラリ
│       ├── utils/           # ユーティリティ
│       ├── api_clients/     # APIクライアント
│       └── file_handlers/   # ファイル処理
├── tests/                   # テストスイート
├── main.py                  # メインアプリケーション
└── pyproject.toml          # プロジェクト設定
```

### コーディング規約

- **Python**: PEP 8準拠、type hints必須
- **命名**: スネークケース（Python）、キャメルケース（TypeScript）
- **ドキュメント**: 全公開APIにdocstring必須
- **テスト**: 新機能には必ずテストを追加

---

## 🔒 セキュリティ機能

### GPG暗号化ポリシー

#### Modern Strong Policy
- **Cipher**: AES-256-OCB (SEIPDv2)
- **Digest**: SHA-256
- **Use Case**: 最高レベルのセキュリティが必要な操作

#### Compatibility Policy
- **Cipher**: AES-128
- **Digest**: SHA-1
- **Use Case**: レガシーシステムとの互換性

#### Backup Longterm Policy
- **Cipher**: AES-256
- **Digest**: SHA-512
- **Use Case**: 長期保存アーカイブ

### Context-Lock システム

プライバシー優先の革新的な署名システム：

```json
{
  "context_lock_version": "1.0",
  "labels": {
    "operation": "payment",
    "privacy_level": "high",
    "jurisdiction": "EU"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 📖 使い方

### GPG暗号化の例

```python
from libral_core.modules.gpg.service import GPGService
from libral_core.modules.gpg.schemas import EncryptRequest, EncryptionPolicy

# GPGサービス初期化
gpg_service = GPGService()

# データ暗号化
request = EncryptRequest(
    data="機密データ",
    recipients=["user@example.com"],
    policy=EncryptionPolicy.MODERN_STRONG,
    context_labels={"operation": "payment", "privacy_level": "high"}
)

result = await gpg_service.encrypt(request)
```

### AIモジュールの使用例

```bash
# 内部AIに質問（1000回/日まで）
curl -X POST "http://localhost:8001/api/ai/ask" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"question": "Pythonのベストプラクティスは？"}'

# 外部AIで高度評価（2回/24時間）
curl -X POST "http://localhost:8001/api/ai/external/evaluate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"question": "複雑なアーキテクチャ設計について"}'
```

### APPモジュールの使用例

```bash
# アプリケーション作成
curl -X POST "http://localhost:8002/api/apps/quick/create" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token" \
  -d '{"name": "My Web App", "app_type": "web"}'

# マイアプリ一覧取得
curl -X GET "http://localhost:8002/api/apps/quick/my-apps" \
  -H "Authorization: Bearer your_token"
```

---

## 🤝 コントリビューション

コントリビューションを歓迎します！詳細は [CONTRIBUTING.md](CONTRIBUTING.md) をご覧ください。

### バグ報告

バグを発見した場合は、[GitHub Issues](https://github.com/G-ACE-inc/libral-core/issues) で報告してください。

### セキュリティ脆弱性

セキュリティに関する問題は、公開せずに [SECURITY.md](SECURITY.md) の手順に従って報告してください。

---

## 📄 ライセンス

This project is proprietary software developed by G-ACE.inc.

---

## 🙏 謝辞

Libral Coreの開発には、多くのオープンソースプロジェクトが利用されています：

- **FastAPI** - モダンなPython Webフレームワーク
- **PostgreSQL** - 高信頼性データベース
- **Redis** - 高速インメモリデータストア
- **GnuPG** - エンタープライズ暗号化
- **aiogram** - Telegram Bot開発

---

## 📞 サポート

- **ドキュメント**: [libral_core/library/README.md](libral_core/library/README.md)
- **GitHub Issues**: [Issues](https://github.com/G-ACE-inc/libral-core/issues)

---

<div align="center">

**🌟 Libral Core - プライバシー優先の未来を創造する 🌟**

Made with ❤️ by [G-ACE.inc](https://g-ace.inc)

</div>
