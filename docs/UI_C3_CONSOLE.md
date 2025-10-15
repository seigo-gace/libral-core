# C3 Console (Context Command Center)

## 概要

**C3 Console**は、Libral Coreの統合管理インターフェースです。システム監視、モジュール管理、クリティカル操作を直感的なHUD UIで提供します。

## デザイン仕様

### カラースキーム

- **背景**: `#000000` (Pure Black)
- **テキスト**: `#FFFFFF` (White)
- **アクセント**: `#FFEB00` (Yellow) - スラッシュパターン、矢印、警告アイコンのみ
- **ボーダー**: `#333333` (Dark Gray)

### タイポグラフィ

- **フォント**: Major Mono Display / Share Tech Mono (Monospace)
- **サイズ**: 
  - ヘッダー: 24px-32px
  - ボディ: 14px-16px
  - キャプション: 12px
- **スタイル**: モノスペース、大文字強調

### レイアウト

- **モバイル**: 縦スクロール、フルスクリーン
- **PC**: 右側メニュー、デュアルペイン

## ページ構成

### 1. Main Dashboard (`/c3`)

C3 Consoleのエントリーポイントです。

**UI要素:**
- 幾何学的ドアアニメーション（400ms cubic-bezier遷移）
- システムステータス表示
- デュアルナビゲーション:
  - **Apps & Features** ボタン → `/c3/apps`
  - **Console Menu** ボタン → `/c3/console`

**コンポーネント:**
```typescript
// client/src/pages/c3-dashboard.tsx

export default function C3Dashboard() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* ドアアニメーション */}
      <GeometricDoorAnimation />
      
      {/* システムステータス */}
      <SystemStatus />
      
      {/* ナビゲーション */}
      <div className="grid grid-cols-2 gap-4">
        <Link to="/c3/apps">
          <Button className="w-full bg-black border border-yellow-500">
            Apps & Features ////
          </Button>
        </Link>
        <Link to="/c3/console">
          <Button className="w-full bg-black border border-yellow-500">
            Console Menu >
          </Button>
        </Link>
      </div>
    </div>
  );
}
```

### 2. Apps & Features (`/c3/apps`)

モジュール管理UIです。接続されたモジュールを自動的に検出し、カード形式で表示します。

**機能:**
- 自動生成モジュールカード
- リアルタイムステータス表示（Online/Offline/Maintenance）
- モジュール詳細へのリンク
- 統計情報の表示

**UI要素:**
```typescript
interface ModuleCard {
  id: string;
  name: string;
  status: "online" | "offline" | "maintenance";
  description: string;
  stats: {
    requests: number;
    uptime: number;
    lastActive: Date;
  };
}
```

**レイアウト:**
- モバイル: 1列グリッド
- タブレット: 2列グリッド
- PC: 3列グリッド

**コンポーネント:**
```typescript
// client/src/pages/c3-apps.tsx

export default function C3Apps() {
  const { data: modules } = useQuery({ queryKey: ['/api/modules'] });
  
  return (
    <div className="p-6 bg-black min-h-screen">
      <h1 className="text-2xl font-mono mb-6 text-white">
        //// APPS & FEATURES
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {modules?.map(module => (
          <ModuleCard 
            key={module.id} 
            module={module}
            data-testid={`card-module-${module.id}`}
          />
        ))}
      </div>
    </div>
  );
}
```

### 3. Console Menu (`/c3/console`)

システム監視とクリティカル操作のパネルです。

**機能:**
- システムメトリクス表示（CPU、メモリ、アクティブユーザー）
- クリティカル操作（Restart、Emergency Stop）
- 二重確認ロジック（CONFIRM コード入力必須）
- リアルタイムログ表示

**二重確認フロー:**
```typescript
// 危険な操作の二重確認
async function handleCriticalAction(action: string) {
  // 1. アラートダイアログ表示
  const confirmed = await showConfirmDialog({
    title: "⚠️ CRITICAL ACTION",
    message: `Are you sure you want to ${action}?`
  });
  
  if (!confirmed) return;
  
  // 2. CONFIRM コード入力
  const code = await showCodeInput({
    message: "Type 'CONFIRM' to proceed"
  });
  
  if (code !== "CONFIRM") {
    showError("Invalid confirmation code");
    return;
  }
  
  // 3. 実行
  await executeCriticalAction(action);
}
```

**コンポーネント:**
```typescript
// client/src/pages/c3-console.tsx

export default function C3Console() {
  const metrics = useSystemMetrics();
  
  return (
    <div className="p-6 bg-black min-h-screen">
      <h1 className="text-2xl font-mono mb-6 text-white">
        > CONSOLE MENU
      </h1>
      
      {/* システムメトリクス */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <MetricCard 
          label="CPU" 
          value={`${metrics.cpu}%`}
          warning={metrics.cpu > 80}
          data-testid="metric-cpu"
        />
        <MetricCard 
          label="MEMORY" 
          value={`${metrics.memory}%`}
          warning={metrics.memory > 80}
          data-testid="metric-memory"
        />
        <MetricCard 
          label="USERS" 
          value={metrics.activeUsers}
          data-testid="metric-users"
        />
      </div>
      
      {/* クリティカル操作 */}
      <div className="space-y-4">
        <Button 
          onClick={() => handleCriticalAction("restart")}
          className="w-full bg-black border border-yellow-500"
          data-testid="button-restart"
        >
          🔄 RESTART SYSTEM
        </Button>
        <Button 
          onClick={() => handleCriticalAction("emergency_stop")}
          className="w-full bg-black border border-red-500"
          data-testid="button-emergency-stop"
        >
          ⚠️ EMERGENCY STOP
        </Button>
      </div>
      
      {/* ログ表示 */}
      <div className="mt-8">
        <h2 className="text-xl font-mono mb-4 text-white">
          //// SYSTEM LOGS
        </h2>
        <LogViewer logs={metrics.recentLogs} />
      </div>
    </div>
  );
}
```

### 4. Module Detail Pages (`/c3/apps/:moduleId`)

各モジュールの詳細ページです。動的に生成されます。

**機能:**
- モジュール概要
- 機能一覧
- アクションボタン
- ライブ統計表示

**コンポーネント:**
```typescript
// client/src/pages/c3-module-detail.tsx

export default function C3ModuleDetail() {
  const { moduleId } = useParams();
  const { data: module } = useQuery({ 
    queryKey: ['/api/modules', moduleId] 
  });
  
  return (
    <div className="p-6 bg-black min-h-screen">
      {/* ヘッダー */}
      <div className="mb-8">
        <h1 className="text-3xl font-mono text-white">
          //// {module.name.toUpperCase()}
        </h1>
        <p className="text-gray-400 mt-2">
          {module.description}
        </p>
        <StatusBadge status={module.status} />
      </div>
      
      {/* 統計 */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <StatCard 
          label="Requests/min" 
          value={module.stats.rpm}
          data-testid="stat-rpm"
        />
        <StatCard 
          label="Success Rate" 
          value={`${module.stats.successRate}%`}
          data-testid="stat-success-rate"
        />
        <StatCard 
          label="Avg Response" 
          value={`${module.stats.avgResponse}ms`}
          data-testid="stat-response-time"
        />
        <StatCard 
          label="Uptime" 
          value={module.stats.uptime}
          data-testid="stat-uptime"
        />
      </div>
      
      {/* 機能一覧 */}
      <div className="mb-8">
        <h2 className="text-xl font-mono mb-4 text-white">
          > FEATURES
        </h2>
        <ul className="space-y-2">
          {module.features.map((feature, i) => (
            <li 
              key={i} 
              className="flex items-center text-gray-300"
              data-testid={`feature-${i}`}
            >
              <span className="text-yellow-500 mr-2">////</span>
              {feature}
            </li>
          ))}
        </ul>
      </div>
      
      {/* アクション */}
      <div className="space-y-4">
        {module.actions.map(action => (
          <Button
            key={action.id}
            onClick={() => handleModuleAction(action)}
            className="w-full bg-black border border-yellow-500"
            data-testid={`button-action-${action.id}`}
          >
            {action.label} >
          </Button>
        ))}
      </div>
    </div>
  );
}
```

## UI コンポーネント

### StatusBadge

```typescript
interface StatusBadgeProps {
  status: "online" | "offline" | "maintenance";
}

function StatusBadge({ status }: StatusBadgeProps) {
  const colors = {
    online: "bg-green-500",
    offline: "bg-red-500",
    maintenance: "bg-yellow-500"
  };
  
  return (
    <span className={`px-3 py-1 rounded ${colors[status]} text-black font-mono text-xs`}>
      {status.toUpperCase()}
    </span>
  );
}
```

### MetricCard

```typescript
interface MetricCardProps {
  label: string;
  value: string | number;
  warning?: boolean;
}

function MetricCard({ label, value, warning }: MetricCardProps) {
  return (
    <div className={`p-4 border ${warning ? 'border-yellow-500' : 'border-gray-700'} bg-black`}>
      <div className="text-gray-400 text-sm font-mono mb-2">
        {label}
      </div>
      <div className={`text-2xl font-mono ${warning ? 'text-yellow-500' : 'text-white'}`}>
        {value}
      </div>
      {warning && (
        <div className="text-yellow-500 text-xs mt-2 flex items-center">
          <span className="mr-1">!</span> WARNING
        </div>
      )}
    </div>
  );
}
```

### LogViewer

```typescript
interface LogEntry {
  timestamp: Date;
  level: "info" | "warn" | "error";
  message: string;
}

function LogViewer({ logs }: { logs: LogEntry[] }) {
  const levelColors = {
    info: "text-white",
    warn: "text-yellow-500",
    error: "text-red-500"
  };
  
  return (
    <div className="bg-black border border-gray-700 p-4 h-64 overflow-y-auto font-mono text-sm">
      {logs.map((log, i) => (
        <div key={i} className="mb-1">
          <span className="text-gray-500">
            [{log.timestamp.toLocaleTimeString()}]
          </span>
          <span className={`ml-2 ${levelColors[log.level]}`}>
            {log.level.toUpperCase()}
          </span>
          <span className="ml-2 text-gray-300">
            {log.message}
          </span>
        </div>
      ))}
    </div>
  );
}
```

## アニメーション

### 幾何学的ドアアニメーション

```typescript
function GeometricDoorAnimation() {
  const [isOpen, setIsOpen] = useState(false);
  
  useEffect(() => {
    setTimeout(() => setIsOpen(true), 100);
  }, []);
  
  return (
    <div className="relative h-screen flex items-center justify-center">
      {/* 左ドア */}
      <div 
        className={`absolute inset-y-0 left-0 w-1/2 bg-black border-r-2 border-yellow-500 
          transition-transform duration-400 ease-cubic-bezier(0.4, 0.0, 0.2, 1)
          ${isOpen ? '-translate-x-full' : 'translate-x-0'}`}
        style={{ clipPath: 'polygon(0 0, 100% 0, 80% 100%, 0 100%)' }}
      />
      
      {/* 右ドア */}
      <div 
        className={`absolute inset-y-0 right-0 w-1/2 bg-black border-l-2 border-yellow-500
          transition-transform duration-400 ease-cubic-bezier(0.4, 0.0, 0.2, 1)
          ${isOpen ? 'translate-x-full' : 'translate-x-0'}`}
        style={{ clipPath: 'polygon(20% 0, 100% 0, 100% 100%, 0 100%)' }}
      />
      
      {/* コンテンツ */}
      <div className={`z-10 transition-opacity duration-400 ${isOpen ? 'opacity-100' : 'opacity-0'}`}>
        <h1 className="text-4xl font-mono text-white">
          //// C3 CONSOLE
        </h1>
      </div>
    </div>
  );
}
```

## レスポンシブデザイン

### モバイル (< 768px)

- 縦スクロール
- 1列グリッド
- フルスクリーンUI
- タッチ最適化ボタン（44px最小タッチターゲット）

### タブレット (768px - 1024px)

- 2列グリッド
- サイドメニュー折りたたみ可能
- ジェスチャーナビゲーション

### PC (> 1024px)

- 3列グリッド
- 固定右側メニュー
- キーボードショートカット対応

## キーボードショートカット

- `Ctrl+K`: 検索を開く
- `Ctrl+/`: ヘルプを表示
- `Ctrl+1`: Apps & Features
- `Ctrl+2`: Console Menu
- `Esc`: モーダルを閉じる

## データフロー

```
1. ページロード
   ↓
2. useQuery でモジュールデータ取得
   ↓
3. WebSocket 接続（リアルタイム更新用）
   ↓
4. Redis Pub/Sub でイベント受信
   ↓
5. UI自動更新
```

## テスト

### E2Eテスト例

```typescript
// tests/c3-console.spec.ts

test('C3 Console - Critical Action Double Confirmation', async ({ page }) => {
  await page.goto('/c3/console');
  
  // Restartボタンクリック
  await page.click('[data-testid="button-restart"]');
  
  // 1st confirmation
  await page.click('text=Confirm');
  
  // 2nd confirmation - CONFIRM code
  await page.fill('input[name="confirmCode"]', 'CONFIRM');
  await page.click('text=Execute');
  
  // 成功メッセージ確認
  await expect(page.locator('text=System restart initiated')).toBeVisible();
});
```

## トラブルシューティング

**Q: モジュールカードが表示されない**
- A: `/api/modules` エンドポイントが正しく応答しているか確認してください

**Q: リアルタイム更新が動作しない**
- A: WebSocket接続を確認してください（`useWebSocket` フック）

**Q: 二重確認が機能しない**
- A: AlertDialogコンポーネントが正しくインポートされているか確認してください

## リファレンス

- [Shadcn/UI Components](https://ui.shadcn.com/)
- [Wouter Routing](https://github.com/molefrog/wouter)
- [TanStack Query](https://tanstack.com/query/latest)
- [WebSocket Integration](./WEBSOCKET.md)

---

**最終更新**: 2025-10-15  
**バージョン**: 3.0.0  
**メンテナー**: Libral Core UI Team
