# Libral Core - 本番環境デプロイメントガイド

## 🎯 デプロイメント概要

Libral Coreは、4つの独立したサービスで構成される完全な本番環境対応システムです：

1. **フロントエンドダッシュボード** (Port 5000) - Node.js/React
2. **メインアプリケーション** (Port 8000) - Python/FastAPI
3. **AIモジュール** (Port 8001) - 独立型FastAPIサービス
4. **APPモジュール** (Port 8002) - 独立型FastAPIサービス

## ✅ 事前準備チェックリスト

### 1. システム要件
- [ ] Python 3.11以上
- [ ] Node.js 20以上
- [ ] PostgreSQL 14以上
- [ ] Redis 7以上
- [ ] 最低4GB RAM
- [ ] 最低10GB ディスク空き容量

### 2. 環境変数設定
```bash
# .env.exampleから.envをコピー
cd libral-core
cp .env.example .env

# 必須項目を編集
nano .env
```

**必須環境変数：**
- `DATABASE_URL`: PostgreSQL接続文字列
- `REDIS_URL`: Redis接続文字列
- `SECRET_KEY`: アプリケーションシークレットキー
- `TELEGRAM_BOT_TOKEN`: Telegram Bot API トークン

**AI Module環境変数：**
- `OPENAI_API_KEY`: OpenAI APIキー（内部AI用）
- `GEMINI_API_KEY`: Google Gemini APIキー（判定役用）

### 3. 依存関係インストール

**Node.js依存関係：**
```bash
npm install
```

**Python依存関係：**
```bash
cd libral-core
pip install -r requirements.txt
```

または、uvを使用：
```bash
uv pip install -r requirements.txt
```

## 🚀 デプロイメント手順

### ステップ1: 環境確認

本番環境テストを実行：
```bash
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

### ステップ2: データベースセットアップ

```bash
# PostgreSQLデータベースの作成
psql -U postgres -c "CREATE DATABASE libral_core;"

# データベース接続確認
psql -U postgres -d libral_core -c "SELECT version();"
```

**注**: データベーススキーマは、各モジュール（AI, APP）が起動時に必要に応じて初期化します。
本番環境では、サービス起動前にDATABASE_URL環境変数が正しく設定されていることを確認してください。

### ステップ3: サービス起動

#### 方法1: Python バックエンド起動

```bash
cd libral-core
bash run_production.sh all
```

このコマンドは以下のPythonサービスを起動します：
- Main Application (Port 8000)
- AI Module (Port 8001)
- APP Module (Port 8002)

**注**: フロントエンドは別途起動が必要です（下記「方法2」参照）

ログファイル：
- `logs/main.log`
- `logs/ai.log`
- `logs/app.log`

#### 方法2: 個別サービス起動

**フロントエンド（本番環境）：**
```bash
# 本番ビルド（フロントエンド + バックエンド）
npm run build

# 本番サーバー起動
npm start
# または、フロントエンドのみプレビュー
npx vite preview --port 5000
```

**注**: 開発環境では `npm run dev` を使用します。`npm run build`はフロントエンドとバックエンドの両方をビルドし、`npm start`は本番用の統合サーバーを起動します。

**メインアプリケーション：**
```bash
cd libral-core
PYTHONPATH=. python main.py
```

**AIモジュール：**
```bash
cd libral-core
PYTHONPATH=. python -m libral_core.modules.ai.app
```

**APPモジュール：**
```bash
cd libral-core
PYTHONPATH=. python -m libral_core.modules.app.app
```

### ステップ4: 動作確認

各サービスのヘルスチェック：

```bash
# フロントエンド
curl http://localhost:5000

# メインアプリケーション
curl http://localhost:8000/health

# AIモジュール
curl http://localhost:8001/api/ai/health

# APPモジュール
curl http://localhost:8002/api/apps/health
```

API ドキュメント：
- メインアプリ: http://localhost:8000/docs
- AIモジュール: http://localhost:8001/docs
- APPモジュール: http://localhost:8002/docs

### ステップ5: 本番環境設定

#### Systemdサービス設定（推奨）

**フロントエンド用：**
```ini
# /etc/systemd/system/libral-frontend.service
[Unit]
Description=Libral Core Frontend Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/libral-core
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**メインアプリ用：**
```ini
# /etc/systemd/system/libral-main.service
[Unit]
Description=Libral Core Main Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/libral-core
Environment="PYTHONPATH=."
Environment="DATABASE_URL=postgresql://..."
Environment="REDIS_URL=redis://localhost:6379"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**AIモジュール用：**
```ini
# /etc/systemd/system/libral-ai.service
[Unit]
Description=Libral AI Module
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/libral-core
Environment="PYTHONPATH=."
Environment="REDIS_URL=redis://localhost:6379"
Environment="OPENAI_API_KEY=..."
Environment="AI_PORT=8001"
ExecStart=/usr/bin/python3 -m libral_core.modules.ai.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**APPモジュール用：**
```ini
# /etc/systemd/system/libral-app.service
[Unit]
Description=Libral APP Module
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/libral-core
Environment="PYTHONPATH=."
Environment="DATABASE_URL=postgresql://..."
Environment="REDIS_URL=redis://localhost:6379"
Environment="APP_PORT=8002"
ExecStart=/usr/bin/python3 -m libral_core.modules.app.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

サービス有効化：
```bash
sudo systemctl daemon-reload
sudo systemctl enable libral-frontend
sudo systemctl enable libral-main
sudo systemctl enable libral-ai
sudo systemctl enable libral-app

sudo systemctl start libral-frontend
sudo systemctl start libral-main
sudo systemctl start libral-ai
sudo systemctl start libral-app
```

#### Nginx リバースプロキシ設定

```nginx
# /etc/nginx/sites-available/libral-core
upstream frontend {
    server localhost:5000;
}

upstream main_app {
    server localhost:8000;
}

upstream ai_module {
    server localhost:8001;
}

upstream app_module {
    server localhost:8002;
}

server {
    listen 80;
    server_name libral.example.com;

    # フロントエンド
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # メインアプリケーションAPI
    location /api/v1/ {
        proxy_pass http://main_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # AIモジュールAPI
    location /api/ai/ {
        proxy_pass http://ai_module;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # APPモジュールAPI
    location /api/apps/ {
        proxy_pass http://app_module;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Nginx有効化：
```bash
sudo ln -s /etc/nginx/sites-available/libral-core /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 監視とメンテナンス

### ログ確認

**Systemdサービスログ：**
```bash
# フロントエンド
sudo journalctl -u libral-frontend -f

# メインアプリ
sudo journalctl -u libral-main -f

# AIモジュール
sudo journalctl -u libral-ai -f

# APPモジュール
sudo journalctl -u libral-app -f
```

**アプリケーションログ：**
```bash
# 本番環境ログ
tail -f /opt/libral-core/logs/main.log
tail -f /opt/libral-core/logs/ai.log
tail -f /opt/libral-core/logs/app.log
```

### パフォーマンス監視

```bash
# システムメトリクス
curl http://localhost:5000/api/system/metrics

# AIモジュール統計
curl http://localhost:8001/api/ai/metrics

# APPモジュール統計
curl http://localhost:8002/api/apps/stats
```

### バックアップ

**データベースバックアップ：**
```bash
# PostgreSQL
pg_dump -U postgres libral_core > backup_$(date +%Y%m%d).sql

# Redisバックアップ
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb
```

**設定ファイルバックアップ：**
```bash
tar czf libral_config_backup_$(date +%Y%m%d).tar.gz \
    /opt/libral-core/.env \
    /opt/libral-core/libral_core/config.py
```

## 🔒 セキュリティ設定

### ファイアウォール設定

```bash
# UFWの場合
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# iptablesの場合
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### SSL/TLS設定（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d libral.example.com
```

### 環境変数の暗号化

```bash
# GPGで.envを暗号化
gpg --symmetric --cipher-algo AES256 .env
rm .env

# 復号化
gpg --decrypt .env.gpg > .env
```

## 🐛 トラブルシューティング

### サービスが起動しない

```bash
# 依存関係確認
cd libral-core
bash run_production.sh test

# ポート使用状況確認
sudo netstat -tulpn | grep -E '5000|8000|8001|8002'

# ログ確認
sudo journalctl -u libral-main -n 100
```

### データベース接続エラー

```bash
# PostgreSQL接続確認
psql -U postgres -d libral_core -c "SELECT 1;"

# DATABASE_URL確認
echo $DATABASE_URL
```

### Redis接続エラー

```bash
# Redis動作確認
redis-cli ping

# Redis URL確認
echo $REDIS_URL
```

### メモリ不足

```bash
# メモリ使用状況確認
free -h

# サービス再起動
sudo systemctl restart libral-main
sudo systemctl restart libral-ai
sudo systemctl restart libral-app
```

## 📈 スケーリング

### 水平スケーリング

複数のワーカープロセスで起動：
```bash
# Gunicorn使用（メインアプリ）
gunicorn main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000

# AIモジュール
gunicorn libral_core.modules.ai.app:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001
```

### Dockerデプロイメント

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
ENV PYTHONPATH=/app

CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: libral_core
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  main:
    build: ./libral-core
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres/libral_core
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  ai:
    build: ./libral-core
    command: python -m libral_core.modules.ai.app
    ports:
      - "8001:8001"
    environment:
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - redis

  app:
    build: ./libral-core
    command: python -m libral_core.modules.app.app
    ports:
      - "8002:8002"
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres/libral_core
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - NODE_ENV=production

volumes:
  pgdata:
  redis_data:
```

起動：
```bash
docker-compose up -d
```

## 📝 チェックリスト

デプロイ前の最終確認：

- [ ] すべての環境変数が設定されている
- [ ] データベース接続が正常
- [ ] Redis接続が正常
- [ ] 本番環境テストが100%通過
- [ ] SSL証明書が設定されている
- [ ] ファイアウォールが設定されている
- [ ] バックアップスクリプトが設定されている
- [ ] 監視システムが設定されている
- [ ] ログローテーションが設定されている
- [ ] エラーアラートが設定されている

## 🎉 デプロイメント完了

すべてのステップが完了したら、以下のURLでアクセス可能：

- **ダッシュボード**: https://libral.example.com
- **メインAPI**: https://libral.example.com/api/v1/docs
- **AI API**: https://libral.example.com/api/ai/docs
- **APP API**: https://libral.example.com/api/apps/docs

---

**サポート**: 問題が発生した場合は、[GitHub Issues](https://github.com/yourusername/libral-core/issues)で報告してください。
