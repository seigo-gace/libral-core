# Libral Core - 本番環境クイックスタートガイド

## 🚀 5分で開発/テスト環境起動

**注意**: これは開発/テスト環境のセットアップガイドです。本番環境では追加の設定（PostgreSQL, Redis）が必要です。

### 前提条件
- Python 3.11+
- Node.js 20+
- PostgreSQL 14+
- Redis 7+

### ステップ1: 環境設定（1分）

```bash
# リポジトリクローン
git clone https://github.com/yourusername/libral-core.git
cd libral-core

# 環境変数設定
cp .env.example .env
nano .env  # 必須項目を編集
```

必須環境変数：
- `DATABASE_URL`: PostgreSQL接続文字列
- `REDIS_URL`: Redis接続文字列
- `SECRET_KEY`: ランダムな秘密鍵
- `TELEGRAM_BOT_TOKEN`: TelegramボットToken

### ステップ2: 依存関係インストール（2分）

```bash
# Node.js依存関係
npm install

# Python依存関係
cd libral-core
pip install -r requirements.txt
```

### ステップ3: 動作確認（1分）

```bash
# 本番環境テスト
cd libral-core
bash run_production.sh test
```

期待される出力：
```
✅ All imports successful
✅ AI Module: 7/7 tests passed
✅ APP Module: 6/6 tests passed
🎉 Production tests completed!
```

### ステップ4: サービス起動（1分）

#### オプションA: Python バックエンド起動

```bash
cd libral-core
bash run_production.sh all
```

**注**: これはPythonバックエンドのみ起動します。フロントエンドは別途起動してください（オプションB参照）

#### オプションB: 個別起動

```bash
# Python バックエンド（ターミナル1）
cd libral-core
bash run_production.sh main

# AI Module（ターミナル2）
cd libral-core
bash run_production.sh ai

# APP Module（ターミナル3）
cd libral-core
bash run_production.sh app

# フロントエンド（本番ビルド）
npm run build
npm start
# または
npx vite preview --port 5000
```

**注**: 開発環境では `npm run dev` を使用できますが、本番環境では上記の `build` + `start` を推奨します。

### ステップ5: 動作確認

各サービスにアクセス：

- **ダッシュボード**: http://localhost:5000
- **メインAPI**: http://localhost:8000/docs
- **AI API**: http://localhost:8001/docs
- **APP API**: http://localhost:8002/docs

## 📊 サービス構成

| サービス | ポート | 説明 |
|---------|--------|------|
| フロントエンド | 5000 | React ダッシュボード |
| メインアプリ | 8000 | GPG/Auth/Events/Payments |
| AI Module | 8001 | 双AI システム |
| APP Module | 8002 | アプリケーション管理 |

## 🔍 ヘルスチェック

```bash
# すべてのサービスが正常か確認
curl http://localhost:5000
curl http://localhost:8000/health
curl http://localhost:8001/api/ai/health
curl http://localhost:8002/api/apps/health
```

## 📝 主要コマンド

```bash
# 全サービス起動
bash run_production.sh all

# 個別サービス起動
bash run_production.sh main    # メインアプリ
bash run_production.sh ai      # AIモジュール
bash run_production.sh app     # APPモジュール

# テスト実行
bash run_production.sh test

# サービス停止
# Ctrl+C で停止、または
kill <PID>
```

## 🛠️ トラブルシューティング

### ポート競合

```bash
# ポート使用状況確認
sudo netstat -tulpn | grep -E '5000|8000|8001|8002'

# プロセス停止
kill <PID>
```

### データベース接続エラー

```bash
# PostgreSQL起動確認
sudo systemctl status postgresql

# データベース作成
psql -U postgres -c "CREATE DATABASE libral_core;"
```

### Redis接続エラー

```bash
# Redis起動確認
sudo systemctl status redis

# Redis起動
sudo systemctl start redis
```

### Python依存関係エラー

```bash
# 依存関係再インストール
cd libral-core
pip install -r requirements.txt --force-reinstall
```

## 📚 詳細ドキュメント

- [完全デプロイメントガイド](DEPLOYMENT.md) - 本番環境詳細手順
- [クイックスタート](docs/QUICKSTART.md) - 開発環境セットアップ
- [AIモジュール](docs/AI_MODULE.md) - AI API詳細
- [APPモジュール](docs/APP_MODULE.md) - APP API詳細
- [プロジェクト構造](docs/PROJECT_STRUCTURE.md) - アーキテクチャ詳細

## ✨ 次のステップ

1. **本番環境設定**: [DEPLOYMENT.md](DEPLOYMENT.md)を参照してSystemdサービス設定
2. **SSL設定**: Let's Encryptで証明書取得
3. **監視設定**: ログとメトリクス監視システム設定
4. **バックアップ**: 定期バックアップスクリプト設定

## 🎉 完了！

すべてのサービスが起動したら、以下で確認：

```bash
# システムステータス
curl http://localhost:5000/api/system/metrics

# AI統計
curl http://localhost:8001/api/ai/metrics

# APP統計
curl http://localhost:8002/api/apps/stats
```

---

**サポート**: [GitHub Issues](https://github.com/yourusername/libral-core/issues)
