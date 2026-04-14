# Libral Core - 起動確認手順

## 前提

- Node.js 18+ がインストールされていること
- プロジェクトルートは `libral-core_riplit`（本ドキュメントの親の親ディレクトリ）

## 1. 依存関係のインストール

```bash
cd libral-core_riplit
npm install
```

## 2. 型チェック（任意）

```bash
npm run check
```

エラーが出なければ TypeScript のビルドは通ります。

## 3. 開発サーバー起動

```bash
npm run dev
```

- **Windows / Mac / Linux** とも `cross-env` で `NODE_ENV=development` が設定されます。
- 起動に成功すると次のようなログが出ます:
  - `[REGISTRY] Registered module: ...`
  - `[LIBRAL-CORE] All AI modules initialized successfully` または `Continuing without AI modules...`
  - `serving on port 5000`（または `PORT` で指定した番号）

## 4. 動作確認

- ブラウザで **http://localhost:5000** を開く（クライアント＋API が同じポートで配信されます）。
- ヘルスチェック: **http://localhost:5000/api/health** にアクセスし、`{"status":"healthy",...}` が返ることを確認。

## 5. 起動に失敗する場合

| 現象 | 確認すること |
|------|----------------------|
| `npm` がない | Node.js をインストールし、PATH に `npm` が含まれるか確認。 |
| `Cannot find module 'xxx'` | ルートで `npm install` を実行。 |
| Redis 接続エラー | AI モジュール初期化は失敗しても「Continuing without AI modules...」で起動は継続。本番で Redis を使う場合は Redis を起動する。 |
| ポート使用中 | 別プロセスが 5000 番を使用している場合は、`PORT=5001 npm run dev` のように別ポートを指定。 |

## テスト（速度優先）

```bash
# Node: Vitest 単発実行（watch なし・高速）
npm run test

# Python: pytest（最初の失敗で停止・簡潔出力）
npm run test:py
```

- **Node**: `server/**/*.test.ts` を実行。タイムアウト 5s、threads プールで短時間完了。
- **Python**: `libral-core/tests/` を `-x -q --tb=line` で実行。

## 本番ビルド後の起動

```bash
npm run build
npm start
```

- 本番では `dist/index.js` と `dist/public/` が使われます。

## 本番展開前チェック（高速稼働・脆弱性）

- **基準と手順**: [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md) を参照。
- 起動・稼働テストと `npm run test` / `npm run test:py` を実行し、本番可否を判定する。
