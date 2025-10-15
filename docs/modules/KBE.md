# KBE (Knowledge Booster Engine)

## 概要

**KBE (Knowledge Booster Engine)**は、プライバシーファーストの集合知システムです。連合学習と準同型暗号化を活用し、ユーザーのプライバシーを保護しながら知識を共有・蓄積します。

## 主要機能

### 1. プライバシーファースト集合知

ユーザーデータを中央サーバーに送信せずに知識を共有します。

- **連合学習**: ローカルで学習、モデルパラメータのみ共有
- **準同型暗号化**: 暗号化されたデータで計算実行
- **差分プライバシー**: 個人情報の保護
- **匿名知識投稿**: 投稿者を特定できない仕組み

### 2. 独立KBシステム

KBEから完全に独立した知識ベースシステムを提供します。

**機能:**
- 80+言語対応の多言語KB
- Web UI (`/kb-editor`) による直感的な管理
- RESTful API による CRUD操作
- カテゴリ管理と検索機能
- バージョン管理と履歴追跡

```typescript
interface KBEntry {
  id: string;
  title: string;
  content: string;
  category: string;
  language: string;
  tags: string[];
  metadata: {
    author?: string;
    createdAt: Date;
    updatedAt: Date;
    version: number;
  };
}
```

### 3. 連合学習 (Federated Learning)

分散環境で機械学習モデルを訓練します。

**プロセス:**
1. **初期化**: 中央サーバーがグローバルモデルを配布
2. **ローカル訓練**: 各クライアントがローカルデータで訓練
3. **モデル集約**: 更新されたパラメータを集約
4. **グローバル更新**: 新しいグローバルモデルを配布

```typescript
interface FederatedLearningRound {
  roundId: number;
  participants: number;
  modelVersion: string;
  aggregationMethod: "fedavg" | "fedprox" | "scaffold";
  convergenceMetric: number;
}
```

### 4. 準同型集約 (Homomorphic Aggregation)

暗号化されたデータで計算を実行します。

```python
# 準同型暗号化による集約
encrypted_updates = [encrypt(update) for update in client_updates]
encrypted_sum = homomorphic_sum(encrypted_updates)
aggregated_update = decrypt(encrypted_sum)
```

**利点:**
- データ内容を見ずに計算可能
- プライバシー完全保護
- 信頼できない環境でも安全

### 5. 匿名知識投稿

投稿者の身元を保護しながら知識を共有します。

**技術:**
- **ゼロ知識証明**: 知識の正当性を証明（身元は秘匿）
- **Onion ルーティング**: 送信経路の匿名化
- **グループ署名**: グループメンバーの1人が署名（誰かは不明）

```typescript
interface AnonymousSubmission {
  contentHash: string;
  zkProof: string;          // ゼロ知識証明
  groupSignature: string;   // グループ署名
  timestamp: number;
  category: string;
}
```

## アーキテクチャ

### Python モジュール構成

```python
# libral-core/src/modules/kbe/

├── __init__.py
├── core.py              # KBEコアロジック
├── federated.py         # 連合学習
├── homomorphic.py       # 準同型暗号化
└── router.py            # FastAPI ルーター
```

### Node.js KB システム

```typescript
// server/modules/kb-system.ts

export class KBSystem {
  async createEntry(entry: KBEntry): Promise<KBEntry>
  async getEntry(id: string): Promise<KBEntry | null>
  async updateEntry(id: string, data: Partial<KBEntry>): Promise<KBEntry>
  async deleteEntry(id: string): Promise<boolean>
  async search(query: string, filters?: SearchFilters): Promise<KBEntry[]>
  async getStats(): Promise<KBStats>
}
```

### Web UI コンポーネント

```typescript
// client/src/pages/kb-editor.tsx

- KB エントリー一覧表示
- CRUD 操作UI
- カテゴリ管理
- 多言語サポート
- 検索・フィルタリング
- マークダウンエディタ
```

## API エンドポイント

### KB 管理

**エントリー作成:**
```http
POST /api/kb/entries
Content-Type: application/json

{
  "title": "TypeScript型推論のベストプラクティス",
  "content": "型推論を効果的に...",
  "category": "programming",
  "language": "ja",
  "tags": ["typescript", "best-practices"]
}
```

**エントリー検索:**
```http
POST /api/kb/search
Content-Type: application/json

{
  "query": "型推論",
  "filters": {
    "category": "programming",
    "language": "ja",
    "tags": ["typescript"]
  }
}
```

**統計情報:**
```http
GET /api/kb/stats
```

**レスポンス:**
```json
{
  "totalEntries": 1250,
  "byCategory": {
    "programming": 450,
    "security": 320,
    "design": 280,
    "other": 200
  },
  "byLanguage": {
    "en": 650,
    "ja": 380,
    "zh": 120,
    "other": 100
  },
  "recentActivity": {
    "today": 45,
    "thisWeek": 230,
    "thisMonth": 890
  }
}
```

### 連合学習

**学習ラウンド開始:**
```http
POST /api/kbe/federated/start-round
Content-Type: application/json

{
  "modelType": "text-classification",
  "aggregationMethod": "fedavg",
  "minParticipants": 10
}
```

**ローカル更新送信:**
```http
POST /api/kbe/federated/submit-update
Content-Type: application/json

{
  "roundId": 42,
  "encryptedUpdate": "...",  # 準同型暗号化された更新
  "zkProof": "..."            # ゼロ知識証明
}
```

**グローバルモデル取得:**
```http
GET /api/kbe/federated/global-model?version=latest
```

### 匿名投稿

**匿名知識投稿:**
```http
POST /api/kbe/anonymous/submit
Content-Type: application/json

{
  "content": "暗号化されたコンテンツ",
  "zkProof": "...",
  "groupSignature": "...",
  "category": "security-tips"
}
```

**投稿検証:**
```http
POST /api/kbe/anonymous/verify
Content-Type: application/json

{
  "submissionId": "anon-123",
  "zkProof": "..."
}
```

## 使用例

### KB エントリー管理

```typescript
import { kbeApi } from '@/api/kbe';

// エントリー作成
const newEntry = await kbeApi.createEntry({
  title: "React Hooks パターン集",
  content: "useEffect の依存配列...",
  category: "react",
  language: "ja",
  tags: ["react", "hooks", "patterns"]
});

// 検索
const results = await kbeApi.search({
  query: "hooks",
  filters: {
    category: "react",
    language: "ja"
  }
});

// 統計取得
const stats = await kbeApi.getStats();
console.log(`総エントリー数: ${stats.totalEntries}`);
```

### 連合学習への参加

```typescript
// 1. グローバルモデル取得
const globalModel = await kbeApi.getGlobalModel();

// 2. ローカルデータで訓練
const localUpdate = await trainLocally(globalModel, localData);

// 3. 準同型暗号化
const encryptedUpdate = await homomorphicEncrypt(localUpdate);

// 4. ゼロ知識証明生成
const zkProof = await generateZKProof(localUpdate);

// 5. 更新送信
await kbeApi.submitFederatedUpdate({
  roundId: currentRound.id,
  encryptedUpdate,
  zkProof
});
```

### 匿名知識投稿

```typescript
// 1. コンテンツ準備
const knowledge = {
  title: "セキュリティ脆弱性の発見",
  content: "CVE-2025-XXXX の詳細...",
  category: "security"
};

// 2. 暗号化
const encrypted = await encryptContent(knowledge);

// 3. ZK証明生成（知識の正当性を証明）
const zkProof = await generateValidityProof(knowledge);

// 4. グループ署名
const groupSig = await signAsGroupMember(encrypted);

// 5. 匿名投稿
const submission = await kbeApi.submitAnonymous({
  content: encrypted,
  zkProof,
  groupSignature: groupSig,
  category: knowledge.category
});

console.log('匿名投稿ID:', submission.id);
```

## KB エディタ UI (`/kb-editor`)

### 機能

- **マークダウンエディタ**: リアルタイムプレビュー
- **カテゴリ管理**: ドラッグ&ドロップで整理
- **多言語切り替え**: 80+言語対応
- **検索・フィルター**: 高速全文検索
- **バージョン履歴**: 変更履歴の追跡
- **タグ管理**: オートコンプリート対応

### ショートカットキー

- `Ctrl+S`: 保存
- `Ctrl+K`: 検索
- `Ctrl+N`: 新規エントリー
- `Ctrl+/`: ヘルプ表示

## 設定

### 環境変数

```env
# KB System
KB_MAX_ENTRIES=10000
KB_DEFAULT_LANGUAGE=ja
KB_SUPPORTED_LANGUAGES=en,ja,zh,ko,es,fr,de

# 連合学習
KBE_FEDERATED_ENABLED=true
KBE_MIN_PARTICIPANTS=5
KBE_AGGREGATION_METHOD=fedavg

# 準同型暗号
KBE_HE_SCHEME=ckks        # CKKS, BFV, or TFHE
KBE_SECURITY_LEVEL=128

# 匿名投稿
KBE_ANONYMOUS_ENABLED=true
KBE_ZK_PROOF_TYPE=plonk
```

### 設定ファイル

```python
# libral-core/src/modules/kbe/config.py

class KBEConfig:
    FEDERATED_ENABLED = True
    MIN_PARTICIPANTS = 5
    AGGREGATION_METHOD = "fedavg"
    HE_SCHEME = "ckks"
    SECURITY_LEVEL = 128
    ANONYMOUS_ENABLED = True
```

## プライバシー保証

### 数学的保証

- **差分プライバシー**: ε-差分プライバシー (ε=0.1)
- **準同型暗号**: 128-bit セキュリティレベル
- **ゼロ知識証明**: Plonk/Groth16

### 監査

すべての操作はGPG暗号化されてTelegramパーソナルログサーバーに記録されます。

```typescript
// KB操作ログ例
{
  action: "kb_create",
  timestamp: 1700000000,
  entryId: "kb-123",
  encryptedMetadata: "...",  # GPG暗号化
  hashtags: ["#kb", "#create"]
}
```

## トラブルシューティング

### よくある問題

**Q: 連合学習ラウンドが開始しない**
- A: 最低参加者数（`KBE_MIN_PARTICIPANTS`）に達しているか確認してください

**Q: 準同型暗号化が遅い**
- A: CKKS スキームを使用し、精度要件を見直してください

**Q: 匿名投稿の検証に失敗する**
- A: ZK証明のパラメータが正しく設定されているか確認してください

**Q: KB検索が遅い**
- A: インデックスが正しく構築されているか確認してください（`npm run kb:reindex`）

## 開発ガイド

### カスタムカテゴリの追加

```typescript
// shared/schema.ts に追加

export const kbCategories = [
  "programming",
  "security",
  "design",
  "custom-category"  // 新しいカテゴリ
] as const;
```

### カスタム集約アルゴリズム

```python
# libral-core/src/modules/kbe/federated.py

class CustomAggregation:
    def aggregate(self, client_updates):
        # カスタム集約ロジック
        weighted_sum = sum(
            update * weight 
            for update, weight in zip(client_updates, self.weights)
        )
        return weighted_sum / sum(self.weights)
```

## リファレンス

- [連合学習アルゴリズム](./KBE_FEDERATED.md)
- [準同型暗号化仕様](./KBE_HOMOMORPHIC.md)
- [匿名投稿プロトコル](./KBE_ANONYMOUS.md)
- [KB API リファレンス](../API_KB.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core Knowledge Team
