# AEG (Auto Evolution Gateway)

## 概要

**AEG (Auto Evolution Gateway)**は、Libral Coreの自律進化システムです。AI駆動の開発優先順位付け、GitHub PR生成、タスク管理を提供し、プラットフォームの継続的な進化を実現します。

## 主要機能

### 1. AI駆動の開発優先順位付け

システム使用状況、ユーザーフィードバック、技術的負債を分析し、次に開発すべき機能を自動的に優先順位付けします。

```typescript
interface DevelopmentPriority {
  id: string;
  feature: string;
  priority: number;        // 0-100
  reasoning: string;       // AI による理由説明
  estimatedImpact: {
    users: number;         // 影響を受けるユーザー数
    revenue: number;       // 予想収益影響
    techDebt: number;      // 技術的負債削減
  };
  dependencies: string[];  // 依存する他の機能
  effort: "low" | "medium" | "high" | "epic";
}
```

**優先順位決定要因:**
- ユーザー要求頻度
- ビジネス価値
- 技術的負債
- セキュリティ重要度
- 実装コスト
- 依存関係の複雑さ

### 2. GitHub PR 自動生成

AIが機能仕様からコードを生成し、自動的にPRを作成します。

**プロセス:**
1. **仕様分析**: 機能要求を解析
2. **コード生成**: AI（GPT-4/Gemini）がコード生成
3. **テスト生成**: ユニットテスト・E2Eテスト自動生成
4. **PR作成**: GitHubに自動的にPRを作成
5. **レビュー要求**: 適切なレビュアーに自動アサイン

```typescript
interface AutoPR {
  prNumber: number;
  title: string;
  description: string;
  branch: string;
  filesChanged: string[];
  tests: {
    unit: string[];
    e2e: string[];
  };
  reviewers: string[];
  labels: string[];
  estimatedReviewTime: number;  // 分
}
```

### 3. タスク管理

開発タスクを自動的に管理します。

```typescript
interface DevelopmentTask {
  id: string;
  title: string;
  description: string;
  status: "backlog" | "in_progress" | "review" | "done";
  assignee?: string;
  priority: number;
  tags: string[];
  linkedPRs: number[];
  createdBy: "ai" | "human";
  aiConfidence: number;      // AIの確信度 0-1
}
```

### 4. 自動コードレビュー

PRに対してAIが自動的にコードレビューを実施します。

**レビュー観点:**
- コード品質
- セキュリティ脆弱性
- パフォーマンス問題
- ベストプラクティス準拠
- テストカバレッジ

```typescript
interface AICodeReview {
  prNumber: number;
  overall: "approved" | "changes_requested" | "commented";
  score: number;  // 0-100
  findings: {
    type: "security" | "performance" | "quality" | "style";
    severity: "critical" | "major" | "minor" | "info";
    file: string;
    line: number;
    message: string;
    suggestion?: string;
  }[];
  testCoverage: number;  // %
}
```

### 5. 技術的負債追跡

技術的負債を自動的に検出・追跡します。

```typescript
interface TechnicalDebt {
  id: string;
  type: "code_smell" | "deprecated_api" | "security" | "performance";
  severity: "low" | "medium" | "high" | "critical";
  file: string;
  description: string;
  estimatedEffort: number;  // 時間
  impact: number;           // ビジネス影響度 0-100
  autoFixable: boolean;
  suggestedFix?: string;
}
```

## アーキテクチャ

### Python モジュール構成

```python
# libral-core/src/modules/aeg/

├── __init__.py
├── core.py              # AEGコアロジック
├── prioritization.py    # 優先順位付けアルゴリズム
├── git_pr.py           # GitHub PR管理
└── router.py           # FastAPI ルーター
```

### Node.js API クライアント

```typescript
// client/src/api/aeg.ts

export const aegApi = {
  getPriorities: () => fetch('/api/aeg/priorities'),
  createAutoTask: (spec) => fetch('/api/aeg/tasks/create', { 
    method: 'POST', 
    body: JSON.stringify(spec) 
  }),
  generatePR: (taskId) => fetch(`/api/aeg/pr/generate/${taskId}`, { 
    method: 'POST' 
  }),
  getTechnicalDebt: () => fetch('/api/aeg/tech-debt')
};
```

## API エンドポイント

### 優先順位管理

**優先順位一覧取得:**
```http
GET /api/aeg/priorities
```

**レスポンス:**
```json
{
  "priorities": [
    {
      "id": "feat-001",
      "feature": "リアルタイム通知システム",
      "priority": 95,
      "reasoning": "ユーザーからの要求が最も多く、エンゲージメント向上に直結",
      "estimatedImpact": {
        "users": 5000,
        "revenue": 25000,
        "techDebt": -10
      },
      "effort": "medium"
    }
  ]
}
```

**優先順位再計算:**
```http
POST /api/aeg/priorities/recalculate
```

### タスク管理

**タスク作成:**
```http
POST /api/aeg/tasks/create
Content-Type: application/json

{
  "title": "WebSocket接続の最適化",
  "description": "再接続ロジックの改善",
  "priority": 85,
  "tags": ["performance", "websocket"]
}
```

**タスク一覧:**
```http
GET /api/aeg/tasks?status=backlog&assignee=ai
```

### GitHub PR管理

**PR自動生成:**
```http
POST /api/aeg/pr/generate
Content-Type: application/json

{
  "taskId": "task-123",
  "specification": "WebSocket再接続ロジックの実装...",
  "targetBranch": "develop"
}
```

**レスポンス:**
```json
{
  "prNumber": 456,
  "url": "https://github.com/org/repo/pull/456",
  "branch": "feat/websocket-reconnect",
  "filesChanged": [
    "server/services/websocket.ts",
    "client/src/hooks/use-websocket.ts",
    "tests/websocket.test.ts"
  ],
  "reviewers": ["senior-dev-1", "security-team"],
  "status": "pending_review"
}
```

**AIコードレビュー実行:**
```http
POST /api/aeg/pr/review/{prNumber}
```

### 技術的負債

**負債一覧取得:**
```http
GET /api/aeg/tech-debt?severity=high
```

**自動修正実行:**
```http
POST /api/aeg/tech-debt/{debtId}/auto-fix
```

## 使用例

### 優先順位付けシステム

```typescript
import { aegApi } from '@/api/aeg';

// 優先順位取得
const priorities = await aegApi.getPriorities();

// 上位5つの機能を表示
priorities.priorities
  .slice(0, 5)
  .forEach((item, i) => {
    console.log(`${i + 1}. ${item.feature} (優先度: ${item.priority})`);
    console.log(`   理由: ${item.reasoning}`);
    console.log(`   工数: ${item.effort}`);
  });

// 優先順位再計算（新しいデータ反映）
await aegApi.recalculatePriorities();
```

### AI駆動のタスク作成

```typescript
// 機能仕様からタスク自動生成
const task = await aegApi.createAutoTask({
  feature: "ダッシュボードのリアルタイム更新",
  requirements: [
    "WebSocket接続の確立",
    "自動再接続機能",
    "オフライン時のキュー機能"
  ],
  constraints: {
    deadline: "2025-11-01",
    budget: "medium"
  }
});

console.log('生成されたタスク:', task.title);
console.log('AI確信度:', task.aiConfidence);
```

### GitHub PR 自動生成

```typescript
// タスクからPR自動生成
const pr = await aegApi.generatePR('task-123');

console.log(`PR作成成功: ${pr.url}`);
console.log(`変更ファイル: ${pr.filesChanged.length}件`);
console.log(`レビュアー: ${pr.reviewers.join(', ')}`);

// AIレビュー実行
const review = await aegApi.reviewPR(pr.prNumber);

if (review.overall === 'changes_requested') {
  console.warn('改善が必要:');
  review.findings
    .filter(f => f.severity === 'critical')
    .forEach(f => {
      console.log(`  ${f.file}:${f.line} - ${f.message}`);
    });
}
```

### 技術的負債管理

```typescript
// 高優先度の技術的負債を取得
const debts = await aegApi.getTechnicalDebt();

const criticalDebts = debts.filter(d => d.severity === 'critical');

console.log(`クリティカルな負債: ${criticalDebts.length}件`);

// 自動修正可能な負債を修正
for (const debt of criticalDebts) {
  if (debt.autoFixable) {
    console.log(`自動修正中: ${debt.description}`);
    await aegApi.autoFixDebt(debt.id);
  }
}
```

## AI モデル設定

### 使用モデル

- **コード生成**: GPT-4 Turbo / Gemini Pro
- **優先順位付け**: GPT-3.5 / Gemini Flash
- **コードレビュー**: Claude 3 / GPT-4
- **負債検出**: 特化型MLモデル + GPT-3.5

### モデル選択ロジック

```typescript
interface AIModelSelection {
  task: "code_gen" | "prioritization" | "review" | "debt_detection";
  primaryModel: string;
  fallbackModel: string;
  criteria: {
    speed: number;      // 0-10
    quality: number;    // 0-10
    cost: number;       // 0-10
  };
}
```

## 設定

### 環境変数

```env
# AEG設定
AEG_ENABLED=true
AEG_AUTO_PR_ENABLED=true
AEG_PR_APPROVAL_REQUIRED=true

# GitHub統合
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=org/libral-core
GITHUB_DEFAULT_BRANCH=main

# AI設定
AEG_CODE_GEN_MODEL=gpt-4-turbo
AEG_REVIEW_MODEL=claude-3-opus
AEG_PRIORITIZATION_MODEL=gemini-pro

# 技術的負債
AEG_AUTO_FIX_ENABLED=true
AEG_DEBT_THRESHOLD=high
```

### 設定ファイル

```python
# libral-core/src/modules/aeg/config.py

class AEGConfig:
    ENABLED = True
    AUTO_PR_ENABLED = True
    PR_APPROVAL_REQUIRED = True
    CODE_GEN_MODEL = "gpt-4-turbo"
    REVIEW_MODEL = "claude-3-opus"
    AUTO_FIX_ENABLED = True
```

## トラブルシューティング

### よくある問題

**Q: PR自動生成に失敗する**
- A: GitHub トークンの権限を確認してください（repo, workflow スコープが必要）

**Q: AIレビューの精度が低い**
- A: レビューモデルを `claude-3-opus` または `gpt-4` に変更してください

**Q: 優先順位付けが期待と異なる**
- A: 優先順位決定の重み付けを調整してください（`prioritization.py` の `WEIGHTS` 定数）

**Q: 技術的負債の自動修正が失敗する**
- A: 修正対象のコードが複雑すぎる可能性があります。手動レビューをお勧めします

## 開発ガイド

### カスタム優先順位アルゴリズム

```python
# libral-core/src/modules/aeg/prioritization.py

class CustomPrioritization:
    WEIGHTS = {
        "user_demand": 0.35,
        "business_value": 0.30,
        "tech_debt": 0.20,
        "security": 0.10,
        "implementation_cost": 0.05
    }
    
    def calculate_priority(self, feature):
        score = sum(
            feature[key] * weight 
            for key, weight in self.WEIGHTS.items()
        )
        return min(100, max(0, score))
```

### カスタムPRテンプレート

```typescript
// server/modules/aeg/pr-template.ts

export const customPRTemplate = (task: DevelopmentTask): string => `
## 概要
${task.description}

## 変更内容
<!-- AI生成コードの説明 -->

## テスト
- [ ] ユニットテスト追加
- [ ] E2Eテスト追加
- [ ] 手動テスト実施

## チェックリスト
- [ ] TypeScript型チェック通過
- [ ] ESLint警告なし
- [ ] セキュリティスキャン通過

## 関連Issue
Closes #${task.id}
`;
```

## リファレンス

- [優先順位アルゴリズム詳細](./AEG_PRIORITIZATION.md)
- [AI PR生成プロトコル](./AEG_PR_GENERATION.md)
- [技術的負債検出手法](./AEG_TECH_DEBT.md)
- [GitHub統合ガイド](./AEG_GITHUB.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core Evolution Team
