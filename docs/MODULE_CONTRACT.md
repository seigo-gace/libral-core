# Libral Core - モジュール契約（インターフェース）

**交換可能なモジュール**が満たすべき契約（型・インターフェース）です。  
問題発生時は、この契約を満たす別実装に差し替えることで対応します。

---

## 1. IStorage（永続化）

**ファイル:** `server/storage.ts`  
**用途:** ユーザー・イベント・モジュール・メトリクス・スタンプ・アセット等の永続化。  
**交換例:** MemStorage → PostgreSQL / Drizzle 実装に差し替え。

```ts
interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByTelegramId(telegramId: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: string, updates: Partial<User>): Promise<User | undefined>;
  getActiveUsers(): Promise<User[]>;

  createTransaction(transaction: InsertTransaction): Promise<Transaction>;
  getTransaction(id: string): Promise<Transaction | undefined>;
  getRecentTransactions(limit?: number): Promise<Transaction[]>;
  updateTransactionStatus(id: string, status: string): Promise<Transaction | undefined>;

  createEvent(event: InsertEvent): Promise<Event>;
  getRecentEvents(limit?: number): Promise<Event[]>;
  getEventsByType(type: string, limit?: number): Promise<Event[]>;

  upsertModule(module: InsertModule): Promise<Module>;
  getModule(id: string): Promise<Module | undefined>;
  getAllModules(): Promise<Module[]>;
  updateModuleStatus(id: string, status: string): Promise<Module | undefined>;

  addMetric(metric: InsertSystemMetrics): Promise<SystemMetrics>;
  getLatestMetrics(metricType: string): Promise<SystemMetrics | undefined>;
  getMetricsHistory(metricType: string, limit?: number): Promise<SystemMetrics[]>;

  upsertApiEndpoint(endpoint: InsertApiEndpoint): Promise<ApiEndpoint>;
  getAllApiEndpoints(): Promise<ApiEndpoint[]>;
  updateEndpointStats(path: string, method: string, responseTime: number): Promise<void>;

  createStamp(stamp: InsertStamp): Promise<Stamp>;
  getStamp(id: string): Promise<Stamp | undefined>;
  getStampsByUserId(userId: string): Promise<Stamp[]>;
  updateStampStatus(id: string, status: string, fileUrl?: string): Promise<Stamp | undefined>;

  createAsset(asset: InsertAsset): Promise<Asset>;
  getAssetsByType(type: string): Promise<Asset[]>;
  getAsset(id: string): Promise<Asset | undefined>;

  createSession(session: InsertStampCreationSession): Promise<StampCreationSession>;
  getSession(id: string): Promise<StampCreationSession | undefined>;
  updateSession(id: string, sessionData: any): Promise<StampCreationSession | undefined>;
  deleteExpiredSessions(): Promise<void>;
}
```

型（User, InsertUser, Event, ...）は `@shared/schema` を参照。

---

## 2. TransportAdapter（送信アダプタ）

**ファイル:** `server/core/transport/adapter.ts`  
**用途:** トランスポート層の「1 送信経路」。Telegram / Email / Webhook 等が実装。  
**交換例:** 既存アダプタを別実装に差し替え、または新規アダプタを追加。

```ts
type SendInput = {
  to: string;
  subject?: string;
  body: string;   // Base64
  metadata: {
    tenant_id: string;
    usecase: string;
    sensitivity: 'low' | 'med' | 'high';
    size_bytes: number;
    idempotency_key: string;
  };
};

type SendResult = {
  ok: boolean;
  id?: string;
  error?: string;
  transport?: string;
  retryAfter?: number;
};

interface TransportAdapter {
  name(): string;
  health(): Promise<boolean>;
  send(input: SendInput): Promise<SendResult>;
}
```

---

## 3. StampModule（登録モジュール）

**ファイル:** `server/modules/stamp-creator.ts`（および aegis-pgp が拡張）  
**用途:** モジュールレジストリに登録する「機能モジュール」。スタンプ作成・Aegis-PGP 等。  
**交換例:** 同じ契約を満たす別クラスを `moduleRegistry.registerModule()` で登録。

```ts
interface StampModule {
  id: string;
  name: string;
  version: string;
  status: 'active' | 'inactive' | 'maintenance';
  port?: number;
  endpoints: string[];
  capabilities: string[];
}

// オプション: getInfo() が呼ばれる場合
// async getInfo(): Promise<{ id, name, version, status, endpoints, capabilities, uptime?, lastCheck? }>
// async health(): Promise<boolean>
```

レジストリは `getModule(id)` / `getAllModules()` / `getModuleStatus(id)` / `getAllModuleStatuses()` を提供。  
**新規モジュールを追加するとき:** 上記を満たすクラスを実装し、`server/modules/registry.ts` のコンストラクタで `this.registerModule(yourModule)` する。

---

## 4. AsyncRequestHandler（非同期ルート）

**ファイル:** `server/utils/asyncHandler.ts`  
**用途:** ルートハンドラをラップし、Promise の reject を Express のエラー middleware に渡す。  
**交換例:** 別の async ラッパー（例: ロギング付き）に差し替え可能。

```ts
type AsyncRequestHandler = (
  req: Request,
  res: Response,
  next: NextFunction
) => Promise<void | unknown>;

function asyncHandler(fn: AsyncRequestHandler): (req, res, next) => void
```

---

## 5. ルート登録関数

**用途:** ルートを Express にマウントする単位。差し替え・追加で API を拡張。

```ts
// 例: Aegis
function registerAegisRoutes(app: Express): void;

// 例: メイン
function registerRoutes(app: Express): Promise<Server>;
```

新規ドメインのルートを追加する場合: `registerXxxRoutes(app)` を実装し、`registerRoutes` 内で呼び出す。  
交換時は、同じシグネチャの別実装に差し替える。

---

## 契約の変更時

- **インターフェースを変える場合**（破壊的変更）: 新バージョンを別 ID で用意し、`modules.yaml` とレジストリの両方で「どちらを使うか」を切り替え可能にすると、交換優先の運用を保てます。
- **後方互換を保つ場合**: 既存メソッドを残し、新メソッドやオプション引数を追加する形にすると、既存モジュールをそのまま使い続けつつ進化させられます。

---

**参照:** `docs/MODULE_REGISTRY.md`（一覧・交換手順）、`docs/modules.yaml`（マニフェスト）。
