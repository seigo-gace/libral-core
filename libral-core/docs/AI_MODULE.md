# AI Module - デュアルAIシステム

**独立マイクロサービス（Port 8001）**

## 概要

AI Moduleは、プライバシー優先のデュアルAIシステムを提供する独立したマイクロサービスです。内部AIと外部AI評価の2つのシステムで、効率的かつ高品質なAI応答を実現します。

## 主な機能

### 🤖 デュアルAIシステム

#### 内部AI（日常利用）
- **利用制限**: 1000回/日
- **用途**: 日常的な質問、クイック回答
- **対応プロバイダー**: OpenAI, Anthropic, Google Gemini
- **応答速度**: 高速

#### 外部AI評価（高度分析）
- **利用制限**: 2回/24時間
- **用途**: 複雑な分析、重要な意思決定
- **対応プロバイダー**: Anthropic, OpenAI
- **品質**: 最高品質

### 🔒 セキュリティ機能

- **Context-Lock認証**: すべてのリクエストに必須
- **暗号化応答**: 機密情報の自動暗号化
- **PII除去**: 個人情報の自動削除
- **自動削除**: 24時間後にデータ自動削除

### 📊 使用量管理

- **Redis統合**: リアルタイム使用量追跡
- **自動リセット**: 毎日午前0時（UTC）にリセット
- **使用状況確認**: APIで現在の使用状況を確認可能

## API仕様

### エンドポイント

#### 内部AI質問
```http
POST /api/ai/ask
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "question": "Pythonのベストプラクティスは？",
  "context": "Web開発プロジェクト",
  "max_tokens": 500
}
```

**レスポンス:**
```json
{
  "answer": "AI応答内容...",
  "tokens_used": 450,
  "provider": "openai",
  "remaining_quota": 999,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 外部AI評価
```http
POST /api/ai/external/evaluate
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "question": "複雑なアーキテクチャ設計の評価",
  "context": "エンタープライズシステム設計",
  "evaluation_criteria": ["scalability", "security", "maintainability"]
}
```

**レスポンス:**
```json
{
  "evaluation": "詳細な評価内容...",
  "score": 85,
  "recommendations": ["推奨事項1", "推奨事項2"],
  "provider": "anthropic",
  "remaining_quota": 1,
  "timestamp": "2025-01-01T00:00:00Z"
}
```

#### 使用状況確認
```http
GET /api/ai/usage
Authorization: Bearer {access_token}
```

**レスポンス:**
```json
{
  "internal_ai": {
    "used": 250,
    "limit": 1000,
    "remaining": 750,
    "reset_at": "2025-01-02T00:00:00Z"
  },
  "external_ai": {
    "used": 1,
    "limit": 2,
    "remaining": 1,
    "reset_at": "2025-01-02T00:00:00Z"
  }
}
```

#### ヘルスチェック
```http
GET /api/ai/health
```

**レスポンス:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "components": {
    "redis": "connected",
    "internal_ai": "operational",
    "external_ai": "operational"
  },
  "uptime_seconds": 3600
}
```

## 起動方法

### 基本的な起動

```bash
# デフォルト設定で起動
python -m libral_core.modules.ai.app
```

### カスタム設定で起動

```bash
# 環境変数で設定
AI_HOST=0.0.0.0 \
AI_PORT=8001 \
AI_INTERNAL_PROVIDER=openai \
AI_EXTERNAL_PROVIDER=anthropic \
python -m libral_core.modules.ai.app
```

### Docker起動

```bash
docker run -p 8001:8001 \
  -e DATABASE_URL="postgresql://..." \
  -e REDIS_URL="redis://..." \
  -e OPENAI_API_KEY="sk-..." \
  libral-ai-module
```

## 環境変数

### 必須設定

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/libral_ai
REDIS_URL=redis://localhost:6379
```

### AIプロバイダー設定

```bash
# OpenAI
OPENAI_API_KEY=sk-...
AI_INTERNAL_PROVIDER=openai

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...
AI_EXTERNAL_PROVIDER=anthropic

# Google Gemini
GOOGLE_API_KEY=...
```

### 制限設定

```bash
AI_INTERNAL_DAILY_LIMIT=1000
AI_EXTERNAL_DAILY_LIMIT=2
AI_MAX_TOKENS_PER_REQUEST=2000
```

### セキュリティ設定

```bash
AI_REQUIRE_CONTEXT_LOCK=true
AI_ENCRYPT_RESPONSES=true
AI_REMOVE_PII=true
AI_AUTO_DELETE_HOURS=24
```

## テスト

```bash
# AI Moduleテスト実行
python tests/test_ai_module.py

# または pytest
pytest tests/test_ai_module.py -v
```

## 使用例

### Python SDK

```python
import httpx

# AIクライアント初期化
ai_client = httpx.Client(
    base_url="http://localhost:8001",
    headers={"Authorization": f"Bearer {access_token}"}
)

# 内部AIに質問
response = ai_client.post("/api/ai/ask", json={
    "question": "FastAPIのベストプラクティスは？",
    "context": "RESTful API開発"
})
answer = response.json()["answer"]

# 使用状況確認
usage = ai_client.get("/api/ai/usage").json()
print(f"残り: {usage['internal_ai']['remaining']}回")
```

### cURL

```bash
# 内部AI質問
curl -X POST "http://localhost:8001/api/ai/ask" \
  -H "Authorization: Bearer access_token_user123" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Pythonの非同期処理について教えて",
    "context": "Web開発"
  }'

# 使用状況確認
curl -X GET "http://localhost:8001/api/ai/usage" \
  -H "Authorization: Bearer access_token_user123"
```

## トラブルシューティング

### よくある問題

#### Q: "Quota exceeded" エラーが出る
A: 1日の使用制限に達しています。翌日0時（UTC）まで待つか、外部AI評価を使用してください。

#### Q: Redis接続エラー
A: `REDIS_URL`が正しく設定されているか確認してください。Redisサーバーが起動しているか確認してください。

#### Q: AIプロバイダーエラー
A: APIキーが正しく設定されているか確認してください。プロバイダーのステータスページで障害がないか確認してください。

## パフォーマンス

- **応答時間**: 平均1-3秒（内部AI）、2-5秒（外部AI）
- **同時接続**: 最大100接続
- **Redis使用量**: 最大100MB
- **メモリ使用量**: 約200MB

## セキュリティ

- すべてのリクエストにBearer認証必須
- Context-Lock署名によるプライバシー保護
- 個人情報の自動除去
- 24時間後のデータ自動削除
- すべての操作の監査ログ

---

**プライバシー優先のデュアルAIシステムで、効率的かつ高品質なAI応答を実現！**
