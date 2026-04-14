# 新規モジュール作成ガイド

コア定義に従い、**企画からビルド・デバッグまで**同じ基準でモジュールを作成します。

**必読:** [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) と [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md)

---

## 1. モジュールの種類

| 種類 | 場所 | 契約 |
|------|------|------|
| **Node 登録モジュール** | `server/modules/*.ts` | StampModule（[MODULE_CONTRACT.md §3](./MODULE_CONTRACT.md)） |
| **Python モジュール** | `libral-core/src/modules/*` または `libral_core/modules/*` | プロトコル別（LPO, KBE 等）。本ガイドは **Node の StampModule** を対象とする。 |

---

## 2. 作成手順（要約）

1. [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) で契約とファイルパスを確認する。
2. [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) の**フェーズ 0（企画）**で ID・エンドポイント・capabilities を決める。
3. 下記 **StampModule 実装テンプレート** を使って `server/modules/<id>.ts` を作成する。
4. `server/modules/registry.ts` で `registerModule(instance)` する。
5. `docs/modules.yaml` の `layer-registered-modules` にエントリを追加する。
6. 必要に応じて `server/routes.ts` に API を追加し、`client/src/pages/c3-module-detail.tsx` の `moduleConfigs` に追加する。
7. [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) の**フェーズ 2・3**でビルドとデバッグを行う。

---

## 3. StampModule 実装テンプレート

以下を `server/modules/<module-id>.ts` として保存し、`<MODULE_ID>`, `<表示名>`, エンドポイント・capabilities を置き換えてください。

```ts
// server/modules/<MODULE_ID>.ts
import type { StampModule } from "./stamp-creator";

export class MyFeatureModule implements StampModule {
  public readonly id = "<MODULE_ID>";           // 例: my-feature
  public readonly name = "<表示名>";             // 例: マイ機能
  public readonly version = "v1.0.0";
  public status: "active" | "inactive" | "maintenance" = "active";
  public readonly endpoints = [
    "/api/<MODULE_ID>/health",
    // "/api/<MODULE_ID>/run" など
  ];
  public readonly capabilities = [
    "capability-1",
    "capability-2",
  ];

  constructor() {
    this.initialize();
  }

  private async initialize() {
    console.log(`[${this.id}] Initializing ${this.name} ${this.version}`);
    this.status = "active";
  }

  async health(): Promise<boolean> {
    return this.status === "active";
  }

  async getInfo() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      status: this.status,
      endpoints: this.endpoints,
      capabilities: this.capabilities,
      uptime: process.uptime(),
      lastCheck: new Date().toISOString(),
      category: "app" as const,
      path: `/c3/apps/${this.id}`,
    };
  }
}

export const myFeatureModule = new MyFeatureModule();
```

---

## 4. レジストリ登録

`server/modules/registry.ts` で:

1. 先頭でインスタンスを import する。
2. コンストラクタ内で `this.registerModule(myFeatureModule)` を呼ぶ。

```ts
import { myFeatureModule } from "./my-feature";

export class ModuleRegistry {
  // ...
  constructor() {
    this.registerModule(stampCreatorModule);
    this.registerModule(aegisPgpModule);
    this.registerModule(myFeatureModule);  // 追加
  }
}
```

---

## 5. modules.yaml への追加

`docs/modules.yaml` の `layer-registered-modules` → `modules` に、次の形でエントリを追加する。

```yaml
      - id: module-<MODULE_ID>
        path: server/modules/<MODULE_ID>.ts
        interface: StampModule
        description: <一言説明>
        dependencies: []
        replaceable: true
        version: "1.0.0"
```

---

## 6. C3 詳細ページ（任意）

`client/src/pages/c3-module-detail.tsx` の `moduleConfigs` に、既存エントリを参考に追加する。

```ts
"<MODULE_ID>": {
  name: "<表示名>",
  description: "<説明文>",
  icon: FileText,  // または Lock, Zap 等
  apiEndpoint: "/api/<MODULE_ID>/health",  // 任意
  features: ["機能1", "機能2"],
  actions: [
    { label: "実行", path: "/c3/apps/<MODULE_ID>/run", testId: "button-run" },
  ],
},
```

---

## 7. 参照一覧

| ドキュメント | 用途 |
|--------------|------|
| [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) | コア定義の一元参照（型・パス・チェックリスト） |
| [MODULE_CONTRACT.md](./MODULE_CONTRACT.md) | 契約の正式定義（IStorage, StampModule, TransportAdapter 等） |
| [MODULE_DEVELOPMENT_LIFECYCLE.md](./MODULE_DEVELOPMENT_LIFECYCLE.md) | 企画→実装→ビルド→デバッグの手順 |
| [MODULE_REGISTRY.md](./MODULE_REGISTRY.md) | 運用フロー・交換手順・一覧 |
| [modules.yaml](./modules.yaml) | モジュールマニフェスト（機械可読） |

開発AIは上記を**コア定義**として参照し、企画段階から最終ビルド・デバッグまで同じ基準でモジュールを開発する。
