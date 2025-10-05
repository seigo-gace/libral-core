# Libral Core クイックスタートガイド

このガイドでは、Libral Coreを最速でセットアップして動かす方法を説明します。

## 📋 前提条件

以下のソフトウェアがインストールされていることを確認してください：

- **Python 3.11以上**
- **PostgreSQL 14以上**
- **Redis 7以上**
- **Git**

## ⚡ 5分でスタート

### ステップ1: リポジトリのクローン

```bash
git clone https://github.com/G-ACE-inc/libral-core.git
cd libral-core
```

### ステップ2: Python依存関係のインストール

```bash
# pipを使用
pip install -r requirements.txt

# またはPoetryを使用（推奨）
poetry install
```

### ステップ3: 環境変数の設定

```bash
# サンプル環境ファイルをコピー
cp .env.example .env

# .envファイルを編集（必須項目）
nano .env  # またはお好みのエディタ
```

**最低限必要な設定:**

```bash
# データベース
DATABASE_URL=postgresql://user:password@localhost:5432/libral_core

# Redis
REDIS_URL=redis://localhost:6379

# シークレットキー
SECRET_KEY=your-secret-key-here
```

### ステップ4: データベースのセットアップ

```bash
# PostgreSQLデータベースの作成
createdb libral_core

# マイグレーション実行（Alembicを使用する場合）
alembic upgrade head
```

### ステップ5: アプリケーションの起動

```bash
# メインアプリケーション起動
python main.py
```

🎉 **完了！** ブラウザで `http://localhost:8000/docs` を開いてAPIドキュメントを確認できます。

## 🔧 個別モジュールの起動

### AIモジュール（独立サービス）

```bash
# 環境変数設定
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# AIモジュール起動（Port 8001）
python -m libral_core.modules.ai.app
```

APIドキュメント: `http://localhost:8001/docs`

### APPモジュール（独立サービス）

```bash
# APPモジュール起動（Port 8002）
python -m libral_core.modules.app.app
```

APIドキュメント: `http://localhost:8002/docs`

## 📝 初めてのAPI呼び出し

### ヘルスチェック

```bash
# メインアプリケーション
curl http://localhost:8000/health

# AIモジュール
curl http://localhost:8001/health

# APPモジュール
curl http://localhost:8002/health
```

### AIに質問（認証が必要）

```bash
# まず認証トークンを取得（実装により異なる）
TOKEN="access_token_user123"

# AIに質問
curl -X POST "http://localhost:8001/api/ai/ask" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Pythonのベストプラクティスは？",
    "context": "Web開発"
  }'
```

### アプリケーション作成

```bash
# アプリケーション作成
curl -X POST "http://localhost:8002/api/apps/quick/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First App",
    "app_type": "web"
  }'
```

## 🐳 Dockerで起動（簡単）

Docker Composeを使用すると、すべての依存関係を自動的にセットアップできます：

```bash
# すべてのサービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

これにより、以下のサービスが起動します：
- PostgreSQL（Port 5432）
- Redis（Port 6379）
- Libral Core（Port 8000）
- AI Module（Port 8001）
- APP Module（Port 8002）

## 🧪 動作確認

### テストの実行

```bash
# すべてのテストを実行
pytest tests/ -v

# 特定モジュールのテスト
pytest tests/test_ai_module.py -v
pytest tests/test_app_module.py -v
```

### 統合テスト

```bash
# 統合テスト実行
python tests/test_integration_complete.py
```

すべてのテストが通れば、正しくセットアップされています！

## 📚 次のステップ

### 1. ドキュメントを読む

- **[モジュールドキュメント](.)**: 各モジュールの詳細
- **[API仕様](API.md)**: 全APIエンドポイント
- **[開発ガイド](../CONTRIBUTING.md)**: 開発者向け情報

### 2. 統合モジュールを試す

```python
# GPG暗号化
from libral_core.modules.gpg.service import GPGService

gpg = GPGService()
# 暗号化処理...

# 認証システム
from libral_core.modules.auth.service import AuthService

auth = AuthService()
# 認証処理...
```

### 3. カスタマイズ

`.env`ファイルで各種設定をカスタマイズできます：

```bash
# AI設定
AI_INTERNAL_DAILY_LIMIT=1000
AI_EXTERNAL_DAILY_LIMIT=2

# APP設定
APP_MAX_PER_USER=100
APP_AUTO_ARCHIVE_DAYS=90

# セキュリティ設定
AI_REQUIRE_CONTEXT_LOCK=true
AI_ENCRYPT_RESPONSES=true
```

## 🔍 トラブルシューティング

### PostgreSQL接続エラー

```bash
# PostgreSQLが起動しているか確認
pg_isready

# データベースが存在するか確認
psql -l | grep libral_core
```

### Redis接続エラー

```bash
# Redisが起動しているか確認
redis-cli ping
# 結果: PONG
```

### ポート番号の競合

別のアプリケーションがポートを使用している場合：

```bash
# 使用中のポートを確認
lsof -i :8000
lsof -i :8001
lsof -i :8002

# 環境変数でポートを変更
export APP_PORT=8003
python -m libral_core.modules.app.app
```

### モジュールインポートエラー

```bash
# Pythonパスを確認
echo $PYTHONPATH

# libral-coreディレクトリから実行していることを確認
pwd
# 出力: .../libral-core
```

## 💡 ヒント

### 開発時の便利な設定

```bash
# リロードモードで起動（コード変更時に自動再起動）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# ログレベルを変更
export LOG_LEVEL=debug
python main.py
```

### API開発ツール

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Postman**: APIテストに便利
- **HTTPie**: cURLの代替ツール

```bash
# HTTPieのインストール
pip install httpie

# 使用例
http POST localhost:8001/api/ai/ask \
  Authorization:"Bearer $TOKEN" \
  question="Hello AI"
```

## 📞 サポート

問題が解決しない場合：

1. **ドキュメント**: [docs/](.) で詳細を確認
2. **GitHub Issues**: [Issues](https://github.com/G-ACE-inc/libral-core/issues) で質問
3. **ログ確認**: エラーメッセージを詳しく確認

## 🎓 学習リソース

- **FastAPI Tutorial**: https://fastapi.tiangolo.com/tutorial/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Redis Documentation**: https://redis.io/documentation

---

**準備完了！Libral Coreで革新的なアプリケーションを開発しましょう！** 🚀
