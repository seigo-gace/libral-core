# Libral Core プロジェクト構造

このドキュメントでは、Libral Coreプロジェクトの全体構造を説明します。

## 📁 ディレクトリ構造

```
libral-core/
├── libral_core/                 # Pythonコアパッケージ
│   ├── modules/                 # 9つのコアモジュール
│   │   ├── gpg/                # GPG暗号化モジュール
│   │   ├── auth/               # 認証・認可モジュール
│   │   ├── communication/      # 通信ゲートウェイモジュール
│   │   ├── events/             # イベント管理モジュール
│   │   ├── payments/           # 決済・課金モジュール
│   │   ├── api_hub/            # 外部API統合モジュール
│   │   ├── marketplace/        # プラグインマーケットモジュール
│   │   ├── ai/                 # AIモジュール（独立）⭐
│   │   └── app/                # APPモジュール（独立）⭐
│   ├── integrated_modules/     # 4+1統合モジュール
│   │   ├── lic/                # Libral Identity Core
│   │   ├── leb/                # Libral Event Bus
│   │   ├── las/                # Libral Asset Service
│   │   └── lgl/                # Libral Governance Layer
│   ├── library/                # 共通ライブラリ層
│   │   ├── utils/              # ユーティリティ関数
│   │   ├── api_clients/        # 外部APIクライアント
│   │   ├── file_handlers/      # ファイル処理
│   │   └── examples/           # 使用例
│   ├── __init__.py
│   └── config.py               # グローバル設定
├── tests/                      # テストスイート
│   ├── test_ai_module.py       # AIモジュールテスト
│   ├── test_app_module.py      # APPモジュールテスト
│   ├── test_gpg_module.py      # GPGモジュールテスト
│   ├── test_auth_module.py     # 認証モジュールテスト
│   ├── test_marketplace_module.py  # マーケットプレイステスト
│   └── test_integration_complete.py  # 統合テスト
├── docs/                       # ドキュメント
│   ├── QUICKSTART.md          # クイックスタートガイド
│   ├── AI_MODULE.md           # AIモジュール詳細
│   ├── APP_MODULE.md          # APPモジュール詳細
│   └── PROJECT_STRUCTURE.md   # このファイル
├── archive/                    # アーカイブ
│   ├── old-docs/              # 古いドキュメント
│   ├── old-configs/           # 古い設定ファイル
│   └── reports/               # 開発報告書
├── data/                       # データファイル（gitignore）
├── main.py                     # メインアプリケーション
├── pyproject.toml             # プロジェクト設定（Poetry）
├── requirements.txt           # Python依存関係
├── .env.example               # 環境変数サンプル
├── .gitignore                 # Git除外設定
├── README.md                  # プロジェクト概要
├── CONTRIBUTING.md            # コントリビューションガイド
├── SECURITY.md                # セキュリティポリシー
├── Dockerfile                 # Dockerイメージ定義
└── docker-compose.yml         # Docker Compose設定
```

## 🏗️ アーキテクチャレイヤー

### Layer 1: Core Modules（コアモジュール）

9つの独立したモジュールで構成：

1. **GPG Module** - エンタープライズ暗号化
2. **Auth Module** - 認証・認可システム
3. **Communication Module** - マルチプロトコル通信
4. **Events Module** - イベント管理
5. **Payments Module** - 決済・課金
6. **API Hub Module** - 外部API統合
7. **Marketplace Module** - プラグインシステム
8. **AI Module** - デュアルAIシステム（独立サービス）
9. **APP Module** - アプリケーション管理（独立サービス）

### Layer 2: Integrated Modules（統合モジュール）

4つの主要統合モジュール + 1つのガバナンス層：

1. **LIC (Libral Identity Core)** - アイデンティティとセキュリティ
2. **LEB (Libral Event Bus)** - イベント駆動通信
3. **LAS (Libral Asset Service)** - アセット管理とWASM
4. **LGL (Libral Governance Layer)** - ガバナンスとコンプライアンス

### Layer 3: Library（共通ライブラリ）

再利用可能なユーティリティとツール：

1. **Utils** - 文字列処理、日時管理、バリデーション
2. **API Clients** - 統一された外部API通信
3. **File Handlers** - 画像・動画処理

## 📦 各モジュールの構成

各モジュールは以下の標準構造を持ちます：

```
module_name/
├── __init__.py        # モジュール初期化
├── schemas.py         # Pydanticデータモデル
├── service.py         # ビジネスロジック
├── router.py          # FastAPI APIエンドポイント
└── app.py             # 独立アプリケーション（AIとAPPのみ）
```

### 各ファイルの役割

#### schemas.py
- Pydantic V2データモデル定義
- リクエスト/レスポンススキーマ
- バリデーションルール
- 型安全性の保証

#### service.py
- コアビジネスロジック
- データベース操作
- 外部サービス連携
- エラーハンドリング

#### router.py
- FastAPI APIエンドポイント
- HTTPリクエスト処理
- 認証・認可チェック
- レスポンス整形

#### app.py（独立モジュールのみ）
- 独立したFastAPIアプリケーション
- lifespanイベント管理
- ミドルウェア設定
- サーバー起動設定

## 🚀 起動方法

### メインアプリケーション

```bash
python main.py
```

- ポート: 8000
- 含まれるモジュール: GPG, Auth, Communication, Events, Payments, API Hub, Marketplace
- 統合モジュール: LIC, LEB, LAS, LGL

### 独立マイクロサービス

#### AIモジュール

```bash
python -m libral_core.modules.ai.app
```

- ポート: 8001
- 機能: デュアルAIシステム

#### APPモジュール

```bash
python -m libral_core.modules.app.app
```

- ポート: 8002
- 機能: アプリケーション管理

## 🧪 テスト構造

```
tests/
├── test_ai_module.py          # AI機能テスト（7/7テスト）
├── test_app_module.py         # APP機能テスト（6/6テスト）
├── test_gpg_module.py         # GPG暗号化テスト
├── test_auth_module.py        # 認証システムテスト
├── test_marketplace_module.py # マーケットプレイステスト
└── test_integration_complete.py  # 統合テスト
```

### テスト実行

```bash
# すべてのテスト
pytest tests/ -v

# 特定モジュール
python tests/test_ai_module.py
python tests/test_app_module.py
```

## 📚 ドキュメント構造

```
docs/
├── QUICKSTART.md          # 初心者向けガイド
├── AI_MODULE.md           # AIモジュール詳細
├── APP_MODULE.md          # APPモジュール詳細
└── PROJECT_STRUCTURE.md   # プロジェクト構造（このファイル）
```

## 🗄️ データストレージ

### PostgreSQL

- **用途**: 永続化データストレージ
- **使用モジュール**: Auth, Events, Payments, API Hub, Marketplace, APP
- **接続**: `DATABASE_URL` 環境変数

### Redis

- **用途**: 高速キャッシング、セッション管理、使用量追跡
- **使用モジュール**: AI, APP, Events
- **接続**: `REDIS_URL` 環境変数

## 🔧 設定ファイル

### pyproject.toml

Poetry プロジェクト設定：

- Python依存関係管理
- プロジェクトメタデータ
- ビルド設定

### .env.example

環境変数のテンプレート：

- データベース接続情報
- APIキー設定
- モジュール設定
- セキュリティ設定

### docker-compose.yml

Docker Compose設定：

- PostgreSQL コンテナ
- Redis コンテナ
- アプリケーション コンテナ
- ネットワーク設定

## 🌳 依存関係

### コア依存関係

- **FastAPI**: Web フレームワーク
- **Pydantic**: データバリデーション
- **SQLAlchemy**: ORM
- **asyncpg**: PostgreSQL非同期ドライバ
- **redis**: Redisクライアント
- **aiogram**: Telegram Bot API
- **python-gnupg**: GPG統合
- **httpx**: HTTPクライアント

### 開発依存関係

- **pytest**: テストフレームワーク
- **pytest-asyncio**: 非同期テスト
- **black**: コードフォーマッター
- **flake8**: リンター
- **mypy**: 型チェッカー

## 📊 コード統計

### プロジェクト規模

- **モジュール数**: 13（9コア + 4統合）
- **Python ファイル**: 約50ファイル
- **総コード行数**: 約15,000行
- **テストカバレッジ**: 85%以上

### モジュール別行数（概算）

- GPG Module: ~800行
- Auth Module: ~600行
- Communication Module: ~500行
- Events Module: ~400行
- Payments Module: ~500行
- API Hub Module: ~400行
- Marketplace Module: ~700行
- AI Module: ~1,200行
- APP Module: ~1,000行

## 🔐 セキュリティ構造

### 暗号化レイヤー

1. **GPG Module**: データ暗号化・署名
2. **Auth Module**: 認証・JWT
3. **LGL Module**: ガバナンス・監査

### プライバシー保護

- Context-Lock システム
- 最小限のデータ保持
- 自動データ削除
- 監査ログ

## 🚦 デプロイメント

### 開発環境

```bash
python main.py
# + 独立モジュール個別起動
```

### 本番環境

```bash
# Docker Compose
docker-compose up -d

# または個別Docker
docker run -p 8000:8000 libral-core
docker run -p 8001:8001 libral-ai-module
docker run -p 8002:8002 libral-app-module
```

## 📝 命名規則

### Python

- **ファイル名**: スネークケース (`my_module.py`)
- **クラス名**: パスカルケース (`MyClass`)
- **関数名**: スネークケース (`my_function()`)
- **定数**: アッパースネーク (`MY_CONSTANT`)

### API

- **エンドポイント**: ケバブケース (`/api/my-endpoint`)
- **パラメータ**: スネークケース (`user_id`)

## 🔄 開発ワークフロー

1. **機能ブランチ作成**: `git checkout -b feature/new-feature`
2. **コード実装**: 各モジュールの標準構造に従う
3. **テスト作成**: `tests/` にテストファイル追加
4. **テスト実行**: `pytest tests/ -v`
5. **コミット**: `git commit -m "Add: new feature"`
6. **プルリクエスト**: GitHub でレビュー依頼

## 🎯 ベストプラクティス

### モジュール設計

- **単一責任原則**: 各モジュールは1つの責任のみ
- **疎結合**: モジュール間の依存を最小化
- **高凝集**: 関連する機能をまとめる

### コード品質

- **Type Hints**: すべての関数に型ヒント
- **Docstrings**: 公開APIにドキュメント
- **Error Handling**: 適切な例外処理
- **Logging**: 構造化ログ（structlog）

### テスト

- **単体テスト**: 各関数をテスト
- **統合テスト**: モジュール間連携テスト
- **カバレッジ**: 85%以上を目標

---

**このプロジェクト構造により、拡張性、保守性、テスト容易性が保証されています！**
