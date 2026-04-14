# Libral Core - コア定義（開発AI・人間共通）

モジュールを**企画からビルド・デバッグまで**一貫して開発するための**唯一の参照**です。  
開発AIも人間も、この定義と [MODULE_CONTRACT.md](./MODULE_CONTRACT.md) に従って実装します。

---

## 1. 参照の優先順位

| 順位 | ドキュメント | 用途 |
|------|--------------|------|
| 1 | **本ファイル (CORE_DEFINITIONS.md)** | ファイルパス・型の要約・チェックリストの軸 |
| 2 | [MODULE_CONTRACT.md](./MODULE_CONTRACT.md) | インターフェースの正式定義（IStorage, StampModule, TransportAdapter 等） |
| 3 | [modules.yaml](./modules.yaml) | モジュール一覧（機械可読）・レイヤー・依存関係 |
| 4 | [MODULE_REGISTRY.md](./MODULE_REGISTRY.md) | 運用フロー・交換手順・一覧表 |
| 5 | [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) | 企画→実装→ビルド→デバッグの手順 |

---

## 2. 登録モジュール（StampModule）の必須定義

**実装場所:** `server/modules/<module-id>.ts`  
**契約の詳細:** MODULE_CONTRACT.md の「3. StampModule」

### 2.1 型（TypeScript）

```ts
// server/modules/stamp-creator.ts で定義。新規モジュールはこれを実装する。
interface StampModule {
  id: string;           // 英数字ハイフン（例: my-feature）
  name: string;        // 表示名（例: マイ機能）
  version: string;     // セマンティック（例: v1.0.0）
  status: 'active' | 'inactive' | 'maintenance';
  port?: number;
  endpoints: string[]; // このモジュールが提供する API パス一覧
  capabilities: string[]; // 能力キーワード（C3・検索用）
}
```

### 2.2 実装が持つメソッド（ランタイムで使用）

| メソッド | 必須 | 戻り値 | 用途 |
|----------|:----:|--------|------|
| `getInfo()` | ✅ | `Promise<ModuleInfo>` | `/api/modules` および C3 サイドバーで表示。下記 ModuleInfo を返すこと。 |
| `health()` | 推奨 | `Promise<boolean>` | ヘルスチェック・CRAD 連携 |

### 2.3 getInfo() が返す型（ModuleInfo）

`/api/modules` と C3 の動的メニューはこの形を前提にしています。

```ts
type ModuleInfo = {
  id: string;
  name: string;
  version: string;
  status: string;
  endpoints: string[];
  capabilities: string[];
  uptime?: number;
  lastCheck?: string;  // ISO 8601
  category?: "core" | "app" | "system";  // C3 表示用
  path: string;        // 必須: `/c3/apps/${id}` 形式
  [key: string]: unknown;  // モジュール固有の追加フィールド可
};
```

---

## 3. ファイルパス定義（変更時はここを更新）

| 役割 | パス |
|------|------|
| モジュール実装（Node） | `server/modules/<module-id>.ts` |
| モジュール登録 | `server/modules/registry.ts`（`registerModule()` の呼び出し） |
| マニフェスト（機械可読） | `docs/modules.yaml`（layer-registered-modules にエントリ追加） |
| ルート登録 | `server/routes.ts`（モジュール用 API をここに追加、または `server/routes/<domain>.ts` に分割して読み込み） |
| スキーマ・型 | `shared/schema.ts`（DB や API の型を追加する場合） |
| C3 モジュール詳細 UI | `client/src/pages/c3-module-detail.tsx`（`moduleConfigs` に id を追加すると詳細ページで表示） |
| ストレージ契約 | `server/storage.ts`（IStorage。永続化が必要な場合） |

---

## 4. レジストリ API（変更禁止で参照のみ）

- `moduleRegistry.registerModule(module: StampModule): void`
- `moduleRegistry.getModule(id: string): StampModule | undefined`
- `moduleRegistry.getAllModules(): StampModule[]`
- `moduleRegistry.getModuleStatus(id: string): Promise<ModuleInfo | null>`
- `moduleRegistry.getAllModuleStatuses(): Promise<ModuleInfo[]>`
- `moduleRegistry.startModule(id: string): Promise<boolean>`
- `moduleRegistry.restartModule(id: string): Promise<boolean>`

HTTP: `GET /api/modules` → `getAllModuleStatuses()` の結果を返す。C3 サイドバーはこれを利用。

---

## 5. 運用フロー（交換優先）

1. **トラブル検知** → ログ・メトリクス・`/api/health`・アラート
2. **モジュール特定** → `docs/modules.yaml` / MODULE_REGISTRY.md で ID を特定
3. **変更** → 契約（MODULE_CONTRACT）を満たす実装に**交換**、または設定・バージョンアップ

CRAD（Python）は 1 のアラートに基づきリカバリ。Node 側は手動またはイベントログで 2→3 につなげる。

---

## 6. 新規モジュール追加時のチェックリスト（要約）

- [ ] `StampModule` を実装したクラスを `server/modules/<id>.ts` に作成
- [ ] `getInfo()` で `category` と `path: /c3/apps/${id}` を返す
- [ ] `server/modules/registry.ts` のコンストラクタで `this.registerModule(instance)` を呼ぶ
- [ ] `docs/modules.yaml` の `layer-registered-modules` にエントリを追加
- [ ] 必要なら `server/routes.ts` に API を追加（または routes 分割）
- [ ] C3 詳細ページが必要なら `client/src/pages/c3-module-detail.tsx` の `moduleConfigs[id]` を追加
- [ ] [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) のビルド・デバッグ手順で確認

詳細は [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) を参照。
