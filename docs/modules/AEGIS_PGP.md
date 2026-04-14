# Aegis-PGP 暗号化モジュール

## 概要

**Aegis-PGP**は、Libral Coreの企業グレード暗号化モジュールです。GPG (GNU Privacy Guard)を活用し、ユーザーデータの完全な暗号化と署名検証を提供します。

## 主要機能

### 暗号化ポリシー

1. **Modern Strong Policy**
   - 鍵タイプ: ED25519, ECDSA-P256
   - 暗号化: AES-256-OCB
   - ハッシュ: SHA-512
   - 用途: 最新のセキュリティ要件

2. **Compatibility Policy**
   - 鍵タイプ: RSA-4096
   - 暗号化: AES-256-CBC
   - ハッシュ: SHA-256
   - 用途: レガシーシステムとの互換性

3. **Backup Longterm Policy**
   - 鍵タイプ: RSA-4096 + ED25519 (デュアル)
   - 暗号化: AES-256-GCM
   - ハッシュ: SHA-512
   - 用途: 長期アーカイブと冗長性

### Context-Lock 署名

特定のコンテキスト（タイムスタンプ、地理的位置、デバイスID）に署名をロックすることで、署名の再利用攻撃を防止します。

```typescript
interface ContextLockParams {
  timestamp: number;
  location?: string;
  deviceId?: string;
  customContext?: Record<string, any>;
}
```

### WKD (Web Key Directory) 統合

Web Key Directory プロトコルに対応し、公開鍵の自動検出と検証を可能にします。

## アーキテクチャ

### Python FastAPI バックエンド

```python
# libral-core/libral_core/modules/gpg/

├── __init__.py
├── router.py       # FastAPI ルーター
├── schemas.py      # Pydantic スキーマ
└── service.py      # GPG サービスロジック
```

### Node.js クライアント

```typescript
// server/crypto/aegisClient.ts

class AegisClient {
  async encrypt(data: string, recipientKey: string): Promise<string>
  async decrypt(encryptedData: string, privateKey: string): Promise<string>
  async sign(data: string, privateKey: string, context?: ContextLockParams): Promise<string>
  async verify(data: string, signature: string, publicKey: string): Promise<boolean>
}
```

## API エンドポイント

### 鍵管理

**鍵生成:**
```http
POST /api/gpg/keys/generate
Content-Type: application/json

{
  "policy": "modern_strong",
  "userId": "user@example.com",
  "passphrase": "strong-passphrase"
}
```

**公開鍵エクスポート:**
```http
GET /api/gpg/keys/{keyId}/public
```

**鍵一覧:**
```http
GET /api/gpg/keys
```

### 暗号化・復号化

**データ暗号化:**
```http
POST /api/gpg/encrypt
Content-Type: application/json

{
  "data": "sensitive data",
  "recipientKeyId": "0x1234ABCD"
}
```

**データ復号化:**
```http
POST /api/gpg/decrypt
Content-Type: application/json

{
  "encryptedData": "-----BEGIN PGP MESSAGE-----...",
  "passphrase": "private-key-passphrase"
}
```

### 署名・検証

**データ署名:**
```http
POST /api/gpg/sign
Content-Type: application/json

{
  "data": "message to sign",
  "keyId": "0x1234ABCD",
  "passphrase": "private-key-passphrase",
  "context": {
    "timestamp": 1700000000,
    "deviceId": "device-001"
  }
}
```

**署名検証:**
```http
POST /api/gpg/verify
Content-Type: application/json

{
  "data": "signed message",
  "signature": "-----BEGIN PGP SIGNATURE-----...",
  "publicKey": "-----BEGIN PGP PUBLIC KEY BLOCK-----..."
}
```

## 使用例

### TypeScript (Node.js)

```typescript
import { AegisClient } from '@/crypto/aegisClient';

const aegis = new AegisClient();

// 暗号化
const encrypted = await aegis.encrypt(
  "極秘データ",
  "0x1234ABCD"
);

// 復号化
const decrypted = await aegis.decrypt(
  encrypted,
  "my-private-key-passphrase"
);

// Context-Lock署名
const signature = await aegis.sign(
  "重要メッセージ",
  "my-private-key",
  {
    timestamp: Date.now(),
    deviceId: "device-001",
    location: "Tokyo, Japan"
  }
);

// 署名検証
const isValid = await aegis.verify(
  "重要メッセージ",
  signature,
  "sender-public-key"
);
```

### Python (FastAPI)

```python
from libral_core.modules.gpg.service import GPGService

gpg_service = GPGService()

# 鍵生成
key_result = gpg_service.generate_key(
    policy="modern_strong",
    user_id="user@example.com",
    passphrase="strong-passphrase"
)

# 暗号化
encrypted = gpg_service.encrypt(
    data="極秘データ",
    recipient_key_id="0x1234ABCD"
)

# 復号化
decrypted = gpg_service.decrypt(
    encrypted_data=encrypted,
    passphrase="strong-passphrase"
)
```

## セキュリティ仕様

### 暗号化アルゴリズム

| アルゴリズム | 用途 | 鍵長/設定 |
|------------|------|----------|
| AES-256-OCB | データ暗号化 (Modern) | 256-bit |
| AES-256-CBC | データ暗号化 (Compat) | 256-bit |
| AES-256-GCM | データ暗号化 (Backup) | 256-bit |
| RSA | 鍵交換 | 4096-bit |
| ED25519 | 署名・鍵交換 | Curve25519 |
| ECDSA-P256 | 署名 | NIST P-256 |

### ハッシュアルゴリズム

- **SHA-512**: Modern Strong, Backup Longterm
- **SHA-256**: Compatibility Policy
- **SHA-384**: オプション（中間レベル）

### パスフレーズ要件

- 最小長: 12文字
- 推奨: 16文字以上
- 要件: 大文字、小文字、数字、記号を含む
- エントロピー: 最低80ビット推奨

## パーソナルログサーバー統合

Aegis-PGPは、Telegramパーソナルログサーバーと統合され、すべてのユーザーアクティビティを暗号化してログ保存します。

### ログ暗号化フロー

1. **イベント発生**: ユーザーアクション（ログイン、決済、データ変更）
2. **データ収集**: イベントデータを構造化
3. **GPG暗号化**: ユーザーの公開鍵で暗号化
4. **Telegram送信**: 暗号化データをユーザーのSupergroupに送信
5. **ハッシュタグ付与**: `#login`, `#payment`, `#data_change` などのタグを追加

### ログ検索・復号化

```typescript
// Telegramからログ取得
const encryptedLogs = await telegram.getLogsByHashtag("#payment");

// 各ログを復号化
for (const log of encryptedLogs) {
  const decrypted = await aegis.decrypt(
    log.encryptedContent,
    userPrivateKeyPassphrase
  );
  console.log(decrypted);
}
```

## トラブルシューティング

### よくある問題

**Q: 鍵生成に失敗する**
- A: パスフレーズが要件を満たしているか確認してください（最低12文字、複雑性要件）

**Q: 暗号化データが復号化できない**
- A: 正しい秘密鍵とパスフレーズを使用しているか確認してください

**Q: 署名検証が失敗する**
- A: Context-Lock署名の場合、コンテキストパラメータが一致しているか確認してください

**Q: WKD統合が動作しない**
- A: DNSレコードとWKD設定が正しく構成されているか確認してください

## 設定

### 環境変数

```env
# Aegis-PGP設定
AEGIS_GPG_HOME=/path/to/gpg/home
AEGIS_DEFAULT_POLICY=modern_strong
AEGIS_KEY_EXPIRY_DAYS=730  # 2年

# Python FastAPIエンドポイント
AEGIS_API_URL=http://localhost:8000
AEGIS_API_KEY=your-api-key
```

### 設定ファイル (libral-core/config.py)

```python
class AegisConfig:
    GPG_HOME = "/path/to/gpg/home"
    DEFAULT_POLICY = "modern_strong"
    KEY_EXPIRY_DAYS = 730
    WKD_ENABLED = True
    CONTEXT_LOCK_REQUIRED = True
```

## 開発ガイド

### カスタムポリシーの追加

```python
# libral-core/libral_core/modules/gpg/service.py

CUSTOM_POLICY = {
    "key_type": "ED25519",
    "encryption_algo": "AES-256-GCM",
    "hash_algo": "SHA-512",
    "expiry_days": 365
}

def generate_key(self, policy="custom_policy", ...):
    if policy == "custom_policy":
        return self._generate_with_policy(CUSTOM_POLICY, ...)
```

### テスト

```bash
# Python テスト
cd libral-core
pytest tests/test_gpg_module.py

# Node.js テスト
npm test -- --grep "Aegis-PGP"
```

## リファレンス

- [GPG公式ドキュメント](https://gnupg.org/documentation/)
- [WKD仕様](https://datatracker.ietf.org/doc/draft-koch-openpgp-webkey-service/)
- [Context-Lock署名仕様](./CONTEXT_LOCK_SPEC.md)
- [Libral Core セキュリティポリシー](../SECURITY_POLICY.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core Security Team
