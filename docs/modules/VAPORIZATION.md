# Vaporization Protocol

## 概要

**Vaporization Protocol**は、Libral Coreのプライバシーファーストキャッシュ管理システムです。Redis TTL強制、KBEフラッシュフック、個人データのパターン保護を提供し、ユーザーのプライバシーを最大限に保護します。

## 主要機能

### 1. プライバシーファーストキャッシュ管理

ユーザーの個人データをキャッシュから自動的に削除します。

**原則:**
- **最小保持**: 必要最小限の期間のみ保持
- **自動削除**: TTL（Time To Live）による自動削除
- **パターン保護**: 個人情報パターンの自動検出と保護
- **暗号化保存**: キャッシュデータは常に暗号化

```typescript
interface VaporizationPolicy {
  dataType: string;
  ttl: number;              // 秒
  encryption: boolean;
  autoVaporize: boolean;
  pattern?: RegExp;         // 検出パターン
  onExpire?: (key: string) => Promise<void>;
}
```

### 2. Redis TTL 強制

すべてのキャッシュキーに強制的にTTLを設定します。

**TTL ポリシー:**
- **セッション**: 24時間
- **一時データ**: 1時間
- **個人情報**: 5分
- **匿名データ**: 7日

```typescript
const TTL_POLICIES = {
  session: 24 * 60 * 60,      // 24時間
  temporary: 60 * 60,         // 1時間
  personal: 5 * 60,           // 5分
  anonymous: 7 * 24 * 60 * 60 // 7日
};
```

### 3. KBE フラッシュフック

KBE（Knowledge Booster Engine）と連携し、学習済みデータをフラッシュします。

**フラッシュトリガー:**
- ユーザーによるデータ削除要求
- GDPRコンプライアンス要求
- データ保持期間満了
- システムメンテナンス

```typescript
interface FlushHook {
  trigger: "user_request" | "gdpr" | "retention" | "maintenance";
  scope: "user" | "global" | "category";
  targetData: {
    userId?: string;
    category?: string;
    dateRange?: { from: Date; to: Date };
  };
  cascadeDelete: boolean;   // 関連データも削除
}
```

### 4. パターン保護

個人情報パターンを自動検出し、保護します。

**保護対象パターン:**
- メールアドレス
- 電話番号
- クレジットカード番号
- 住所
- 個人識別番号
- GPS座標
- IPアドレス

```typescript
const PROTECTED_PATTERNS = {
  email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/,
  phone: /\+?[\d\s-]{10,}/,
  creditCard: /\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}/,
  ipAddress: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,
  gps: /[-+]?\d{1,2}\.\d+,\s*[-+]?\d{1,3}\.\d+/
};
```

### 5. 監査ログ

すべてのVaporization操作を監査ログに記録します。

```typescript
interface VaporizationAuditLog {
  timestamp: Date;
  action: "vaporize" | "flush" | "pattern_detect" | "ttl_enforce";
  dataType: string;
  userId?: string;
  reason: string;
  success: boolean;
  metadata: {
    keysAffected: number;
    dataSize: number;       // bytes
    encryptedLog: string;   // GPG暗号化
  };
}
```

## アーキテクチャ

### Python モジュール構成

```python
# libral-core/src/modules/vaporization/

├── __init__.py
├── core.py              # Vaporizationコアロジック
├── redis_ttl.py         # Redis TTL管理
├── flush_hook.py        # KBEフラッシュフック
└── router.py            # FastAPI ルーター
```

### Redis キー設計

```
vaporization:policy:{dataType}      # ポリシー設定
vaporization:queue:{priority}       # 削除キュー
vaporization:audit:{timestamp}      # 監査ログ
vaporization:pattern:{patternType}  # 保護パターン
```

## API エンドポイント

### ポリシー管理

**ポリシー一覧取得:**
```http
GET /api/vaporization/policies
```

**レスポンス:**
```json
{
  "policies": [
    {
      "dataType": "session",
      "ttl": 86400,
      "encryption": true,
      "autoVaporize": true,
      "pattern": null
    },
    {
      "dataType": "personal",
      "ttl": 300,
      "encryption": true,
      "autoVaporize": true,
      "pattern": "email|phone|creditCard"
    }
  ]
}
```

**ポリシー作成:**
```http
POST /api/vaporization/policies
Content-Type: application/json

{
  "dataType": "custom_data",
  "ttl": 3600,
  "encryption": true,
  "autoVaporize": true,
  "pattern": "custom-pattern-\\d+"
}
```

### データVaporization

**即時Vaporization:**
```http
POST /api/vaporization/vaporize
Content-Type: application/json

{
  "keys": ["user:123:session", "user:123:temp"],
  "reason": "user_request"
}
```

**スケジュールVaporization:**
```http
POST /api/vaporization/schedule
Content-Type: application/json

{
  "pattern": "user:*:temp",
  "delay": 3600,
  "reason": "automatic_cleanup"
}
```

### KBE フラッシュ

**フラッシュ実行:**
```http
POST /api/vaporization/flush
Content-Type: application/json

{
  "trigger": "gdpr",
  "scope": "user",
  "targetData": {
    "userId": "user-123"
  },
  "cascadeDelete": true
}
```

**フラッシュ履歴:**
```http
GET /api/vaporization/flush/history?userId=user-123
```

### パターン検出

**パターンスキャン:**
```http
POST /api/vaporization/scan
Content-Type: application/json

{
  "data": "連絡先: user@example.com, 電話: 090-1234-5678",
  "detectPatterns": ["email", "phone"]
}
```

**レスポンス:**
```json
{
  "detected": [
    {
      "type": "email",
      "value": "user@example.com",
      "position": 5,
      "action": "encrypt_and_vaporize"
    },
    {
      "type": "phone",
      "value": "090-1234-5678",
      "position": 30,
      "action": "encrypt_and_vaporize"
    }
  ]
}
```

### 監査ログ

**監査ログ取得:**
```http
GET /api/vaporization/audit?from=2025-10-01&to=2025-10-15
```

**統計情報:**
```http
GET /api/vaporization/stats
```

**レスポンス:**
```json
{
  "totalVaporized": 15420,
  "byType": {
    "session": 8500,
    "personal": 4200,
    "temporary": 2720
  },
  "dataSize": 52428800,  // bytes
  "lastVaporization": "2025-10-15T08:42:00Z"
}
```

## 使用例

### 自動Vaporization設定

```typescript
import { vaporizationApi } from '@/api/vaporization';

// ポリシー作成
await vaporizationApi.createPolicy({
  dataType: "user_activity",
  ttl: 7 * 24 * 60 * 60,  // 7日
  encryption: true,
  autoVaporize: true,
  pattern: /user:\d+:activity:.*/
});

// キャッシュデータ保存（自動的にTTL設定）
await redis.setex(
  'user:123:activity:login',
  7 * 24 * 60 * 60,
  JSON.stringify({ timestamp: Date.now() })
);
```

### 個人情報の保護

```typescript
// データスキャン
const scanResult = await vaporizationApi.scan({
  data: userInput,
  detectPatterns: ['email', 'phone', 'creditCard']
});

if (scanResult.detected.length > 0) {
  console.warn('個人情報が検出されました:');
  
  for (const detection of scanResult.detected) {
    console.log(`- ${detection.type}: ${detection.value}`);
    
    // 暗号化して保存
    const encrypted = await aegis.encrypt(detection.value);
    
    // 短いTTLで保存
    await redis.setex(
      `protected:${detection.type}:${Date.now()}`,
      5 * 60,  // 5分
      encrypted
    );
  }
}
```

### GDPR 準拠のデータ削除

```typescript
// ユーザーからの削除要求
async function handleGDPRDeletion(userId: string) {
  // 1. キャッシュからVaporization
  await vaporizationApi.vaporize({
    pattern: `user:${userId}:*`,
    reason: 'gdpr_deletion_request'
  });
  
  // 2. KBEからフラッシュ
  await vaporizationApi.flush({
    trigger: 'gdpr',
    scope: 'user',
    targetData: { userId },
    cascadeDelete: true
  });
  
  // 3. データベースから削除
  await db.user.delete({ where: { id: userId } });
  
  // 4. 監査ログ記録（GPG暗号化）
  const auditLog = {
    action: 'gdpr_deletion',
    userId,
    timestamp: new Date(),
    success: true
  };
  
  const encryptedLog = await aegis.encrypt(JSON.stringify(auditLog));
  await telegram.sendToPersonalLog(userId, encryptedLog, ['#gdpr', '#deletion']);
}
```

### パターン保護の自動化

```typescript
// カスタムパターンの追加
await vaporizationApi.addProtectedPattern({
  name: 'japanese_my_number',
  pattern: /\d{4}-\d{4}-\d{4}/,  // マイナンバー
  ttl: 60,  // 1分
  action: 'encrypt_and_vaporize'
});

// データ保存時の自動スキャン
async function safeSaveToCache(key: string, data: string) {
  // パターンスキャン
  const scanResult = await vaporizationApi.scan({
    data,
    detectPatterns: ['all']  // すべてのパターン
  });
  
  if (scanResult.detected.length > 0) {
    // 個人情報を暗号化
    let sanitizedData = data;
    for (const detection of scanResult.detected) {
      const encrypted = await aegis.encrypt(detection.value);
      sanitizedData = sanitizedData.replace(
        detection.value,
        `[ENCRYPTED:${encrypted.substring(0, 20)}...]`
      );
    }
    
    // 短いTTLで保存
    await redis.setex(key, 300, sanitizedData);
  } else {
    // 通常のTTL
    await redis.setex(key, 3600, data);
  }
}
```

## 設定

### 環境変数

```env
# Vaporization設定
VAPORIZATION_ENABLED=true
VAPORIZATION_AUTO_SCAN=true
VAPORIZATION_DEFAULT_TTL=3600

# TTLポリシー
VAPORIZATION_SESSION_TTL=86400
VAPORIZATION_PERSONAL_TTL=300
VAPORIZATION_TEMP_TTL=3600

# パターン検出
VAPORIZATION_PATTERN_DETECTION=true
VAPORIZATION_CUSTOM_PATTERNS=japanese_my_number,passport_number

# 監査
VAPORIZATION_AUDIT_ENABLED=true
VAPORIZATION_AUDIT_ENCRYPTION=true
```

### 設定ファイル

```python
# libral-core/src/modules/vaporization/config.py

class VaporizationConfig:
    ENABLED = True
    AUTO_SCAN = True
    DEFAULT_TTL = 3600
    
    TTL_POLICIES = {
        "session": 86400,
        "personal": 300,
        "temporary": 3600,
        "anonymous": 604800
    }
    
    AUDIT_ENABLED = True
    AUDIT_ENCRYPTION = True
```

## プライバシー保証

### GDPR 準拠

- **削除権**: ユーザーは自身のデータを完全に削除可能
- **データ最小化**: 必要最小限のデータのみ保持
- **透明性**: すべてのVaporization操作を監査ログに記録
- **暗号化**: 保存データは常に暗号化

### データライフサイクル

```
1. 生成 → 2. 暗号化 → 3. キャッシュ保存（TTL設定）
                ↓
4. 使用 ← 5. 復号化 ← 6. 取得
                ↓
7. TTL満了 → 8. 自動削除 → 9. 監査ログ記録
```

## トラブルシューティング

### よくある問題

**Q: Vaporizationが実行されない**
- A: `VAPORIZATION_ENABLED=true` が設定されているか確認してください

**Q: TTLが設定されないキーがある**
- A: すべてのRedis SET操作に `SETEX` を使用しているか確認してください

**Q: パターン検出の誤検出が多い**
- A: 正規表現パターンを調整するか、ホワイトリストを追加してください

**Q: 監査ログが暗号化されない**
- A: `VAPORIZATION_AUDIT_ENCRYPTION=true` とAegis-PGP設定を確認してください

## 開発ガイド

### カスタムパターンの追加

```python
# libral-core/src/modules/vaporization/core.py

CUSTOM_PATTERNS = {
    "passport_number": r"[A-Z]{2}\d{7}",
    "drivers_license": r"\d{12}",
    "japanese_my_number": r"\d{4}-\d{4}-\d{4}"
}

def add_custom_pattern(name: str, pattern: str, ttl: int = 300):
    CUSTOM_PATTERNS[name] = pattern
    VAPORIZATION_POLICIES[name] = {
        "ttl": ttl,
        "encryption": True,
        "autoVaporize": True
    }
```

### カスタムフラッシュフック

```python
# libral-core/src/modules/vaporization/flush_hook.py

class CustomFlushHook:
    async def on_flush(self, trigger: str, scope: str, target_data: dict):
        # カスタムフラッシュロジック
        if scope == "user":
            await self.flush_user_data(target_data["userId"])
            await self.notify_user(target_data["userId"], "data_flushed")
```

## リファレンス

- [Redis TTL管理仕様](./VAPORIZATION_TTL.md)
- [パターン検出アルゴリズム](./VAPORIZATION_PATTERNS.md)
- [KBEフラッシュプロトコル](./VAPORIZATION_FLUSH.md)
- [GDPR準拠ガイド](../GDPR_COMPLIANCE.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core Privacy Team
