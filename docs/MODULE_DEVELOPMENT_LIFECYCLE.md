# モジュール開発ライフサイクル（企画 → ビルド → デバッグ）

開発AI・人間のどちらも、**コア定義にのみ従い**、企画から最終デバッグまで一貫してモジュールを開発します。

**必ず参照する定義:** [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) および [MODULE_CONTRACT.md](./MODULE_CONTRACT.md)

---

## フェーズ 0: 企画（要件と契約の確認）

### 0.1 やること

- モジュールの**目的**と**提供する API（エンドポイント）**を決める。
- **コア定義**で「どこに何を書くか」を確認する。

### 0.2 チェックリスト

- [ ] [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) を読んだ
- [ ] モジュール ID（英数字ハイフン）を決めた（例: `my-feature`）
- [ ] 提供する API パスを列挙した（例: `POST /api/my-feature/run`）
- [ ] StampModule 契約（[MODULE_CONTRACT.md](./MODULE_CONTRACT.md) の「3. StampModule」）を満たす方針にした
- [ ] 既存モジュール一覧（[modules.yaml](./modules.yaml) の `layer-registered-modules`）で ID の重複がないことを確認した

### 0.3 成果物（企画の出力）

- モジュール ID
- 表示名（name）
- エンドポイント一覧（endpoints）
- 能力キーワード一覧（capabilities）
- 必要なら永続化の有無（IStorage 利用の有無）

---

## フェーズ 1: 実装（コア定義に沿った実装）

### 1.1 参照する定義

- **型・契約:** [CORE_DEFINITIONS.md §2](./CORE_DEFINITIONS.md#2-登録モジュールstampmoduleの必須定義) および [MODULE_CONTRACT.md §3](./MODULE_CONTRACT.md)
- **ファイル配置:** [CORE_DEFINITIONS.md §3](./CORE_DEFINITIONS.md#3-ファイルパス定義変更時はここを更新)

### 1.2 手順

1. **モジュールクラスを作成**
   - ファイル: `server/modules/<module-id>.ts`
   - `StampModule` を実装し、`getInfo()` で **必ず** `category` と `path: /c3/apps/${id}` を返す。
   - テンプレートは [MODULE_CREATION.md § テンプレート](./MODULE_CREATION.md#stampmodule-実装テンプレート) を使用する。

2. **レジストリに登録**
   - ファイル: `server/modules/registry.ts`
   - コンストラクタ内で `this.registerModule(yourModuleInstance)` を呼ぶ。

3. **マニフェストに追加**
   - ファイル: `docs/modules.yaml`
   - `layers` → `layer-registered-modules` → `modules` に、id / path / interface: StampModule / description 等を追加。

4. **API を公開する場合**
   - ファイル: `server/routes.ts`（または `server/routes/<domain>.ts`）
   - モジュール用の `fastify.get` / `fastify.post` 等を追加。エンドポイントはモジュールの `endpoints` と一致させる。

5. **C3 詳細ページで説明を出す場合**
   - ファイル: `client/src/pages/c3-module-detail.tsx`
   - `moduleConfigs` に `[moduleId]: { name, description, icon, features, actions }` を追加。

### 1.3 チェックリスト

- [ ] `server/modules/<id>.ts` を作成し、StampModule と getInfo()（category, path 含む）を実装した
- [ ] `server/modules/registry.ts` で registerModule した
- [ ] `docs/modules.yaml` の layer-registered-modules にエントリを追加した
- [ ] API が必要なら `server/routes.ts`（または routes 分割）にルートを追加した
- [ ] C3 詳細が必要なら `c3-module-detail.tsx` の moduleConfigs に追加した

---

## フェーズ 2: ビルド（型・ビルドの確認）

### 2.1 参照する定義

- プロジェクト構成・スクリプト: ルートの `package.json`（`build`, `check`）

### 2.2 手順

1. **型チェック**
   ```bash
   npm run check
   ```
   - エラーがあれば、[MODULE_CONTRACT.md](./MODULE_CONTRACT.md) と [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) に沿っているか確認する。

2. **ビルド**
   ```bash
   npm run build
   ```
   - 失敗したら、追加したファイルの import パス・型を修正する。

### 2.3 チェックリスト

- [ ] `npm run check` が通った
- [ ] `npm run build` が通った

---

## フェーズ 3: デバッグ（起動・API・C3 表示の確認）

### 3.1 参照する定義

- 起動手順: [STARTUP_CHECK.md](./STARTUP_CHECK.md)
- 本番・高速稼働: [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md)

### 3.2 手順

1. **起動**
   ```bash
   npm run dev
   ```
   - ログに `[REGISTRY] Registered module: <your-id> (...)` が出ることを確認する。

2. **レジストリ API**
   - `GET http://localhost:5000/api/modules` を叩く。
   - 返却 JSON に当該モジュールの `id`, `name`, `path` が含まれることを確認する。

3. **C3 表示**
   - ブラウザで `http://localhost:5000/c3` を開く。
   - 左サイドバー「Active Modules」に当該モジュールが表示されることを確認する。
   - クリックして `/c3/apps/<id>` に遷移し、詳細ページ（moduleConfigs を追加した場合）または一覧が問題なく表示されることを確認する。

4. **モジュール固有 API**
   - 追加したエンドポイントを実際に呼び、期待どおり動くか確認する。

5. **エラー・ログ**
   - 問題があれば、[MODULE_REGISTRY.md](./MODULE_REGISTRY.md) の運用フローに従い「モジュール特定 → 変更」を検討する。CRAD（Python）と連携する場合はアラート・ログで対象モジュールを特定する。

### 3.3 チェックリスト

- [ ] `npm run dev` で起動し、レジストリログにモジュールが表示された
- [ ] `GET /api/modules` に当該モジュールが含まれた
- [ ] C3 サイドバーに当該モジュールが表示された
- [ ] 必要なら C3 詳細ページとモジュール固有 API を手動で確認した

---

## 開発AI向けの約束

- **企画**では必ず [CORE_DEFINITIONS.md](./CORE_DEFINITIONS.md) と [MODULE_CONTRACT.md](./MODULE_CONTRACT.md) を参照し、StampModule 契約とファイルパスを守る。
- **実装**では上記フェーズ 1 の手順と [MODULE_CREATION.md](./MODULE_CREATION.md) のテンプレートに従い、registry・modules.yaml・routes・c3-module-detail の更新を漏らさない。
- **ビルド・デバッグ**ではフェーズ 2・3 のコマンドとチェックリストで確認する。

これにより、開発AIも人間も**同じコア定義**で企画から最終デバッグまで一貫してモジュールを開発できます。
