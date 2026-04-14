# Libral Core — プロジェクト構成（LeadMe 正式ツリー）

**最終更新**: 2026-02  
**方針**: 見やすく・わかりやすく・最新トレンドに合わせた構成。このツリーが**正式なディレクトリ基準**です。

---

## クイックマップ

| 役割 | パス | 説明 |
|------|------|------|
| **フロント** | `client/` | React + Vite。C3 Console・Dashboard・KB Editor。 |
| **バックエンド** | `server/` | Fastify。API・Webhook・WebSocket・モジュールレジストリ。 |
| **共通** | `shared/` | 型・スキーマ（Zod）。Node とクライアントで共有。 |
| **E2E** | `e2e/` | Playwright による稼働・E2E テスト。 |
| **ドキュメント** | `docs/` | 索引・契約・環境変数・レポート・モジュール説明。 |
| **Python コア** | `libral-core/` | FastAPI。AI・認証・決済・統合モジュール（LIC/LEB/LAS/LGL）。 |

---

## ディレクトリツリー

```
libral-core/
├── .env.example                    # Node 用環境変数テンプレート
├── .env.prod.example                # 本番用例（任意）
├── .cursor/
│   └── rules/
│       └── module-development.mdc  # モジュール開発時の AI ルール
│
├── package.json
├── package-lock.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts                 # 単体・API テスト
├── playwright.config.ts             # E2E テスト（稼働確認）
│
├── README.md                        # プロジェクト概要・セットアップ（入口）
├── PROJECT_STRUCTURE.md             # 本ファイル（正式ツリー）
├── replit.md                        # アーキテクチャ・設計（任意）
│
├── client/                          # フロントエンド (React + Vite)
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── api/                     # API クライアント
│       ├── components/
│       │   ├── dashboard/
│       │   ├── payment/
│       │   └── ui/
│       ├── hooks/
│       ├── layouts/
│       │   └── C3Layout.tsx         # C3 用レイアウト
│       ├── lib/
│       └── pages/
│
├── server/                          # バックエンド (Fastify)
│   ├── index.ts                     # エントリ（listen + WebSocket + AI 初期化）
│   ├── app.ts                       # アプリビルダー（テスト・稼働両用）
│   ├── routes.ts                    # ルート一括登録
│   ├── vite.ts                      # Vite 開発 / 静的配信
│   ├── db.ts
│   ├── storage.ts
│   ├── storage.test.ts
│   ├── api.routes.test.ts           # API ルート Vitest
│   ├── adapters/
│   │   ├── email.ts
│   │   ├── telegram.ts
│   │   └── webhook.ts
│   ├── core/
│   │   ├── ai-bridge/
│   │   ├── ai-router.ts
│   │   └── transport/
│   ├── crypto/
│   │   └── aegisClient.ts
│   ├── data/
│   │   └── fixtures.ts
│   ├── modules/
│   │   ├── aegis-pgp.ts
│   │   ├── embedding.ts
│   │   ├── evaluator.ts
│   │   ├── kb-system.ts
│   │   ├── oss-manager.ts
│   │   ├── registry.ts
│   │   └── stamp-creator.ts
│   ├── routes/
│   │   └── aegis.ts
│   ├── services/
│   │   ├── events.ts
│   │   ├── redis.ts
│   │   ├── telegram.ts
│   │   └── websocket.ts
│   ├── utils/
│   │   ├── asyncHandler.ts
│   │   └── asyncHandler.test.ts
│   └── standalone/                  # スタンドアロン配信用
│       ├── Dockerfile
│       ├── package.json
│       ├── server.ts
│       └── tsconfig.json
│
├── shared/                          # 共通スキーマ・型
│   ├── schema.ts                    # Drizzle + Zod（DB/ユーザー等）
│   └── requestSchemas.ts            # API リクエスト用 Zod（KB/KBE/Aegis）
│
├── e2e/                             # E2E（Playwright）
│   └── health.spec.ts               # 稼働確認用 GET /api/health
│
├── docs/                            # ドキュメント
│   ├── INDEX.md                     # ドキュメント索引（入口）
│   ├── modules.yaml                 # モジュールマニフェスト
│   ├── MODULE_REGISTRY.md
│   ├── MODULE_CONTRACT.md
│   ├── CORE_DEFINITIONS.md          # コア定義（型・パス・チェックリスト）
│   ├── MODULE_DEVELOPMENT_LIFECYCLE.md
│   ├── MODULE_CREATION.md
│   ├── APPS_MODULES.md
│   ├── ENV_VARIABLES_CHECKLIST.md
│   ├── STARTUP_CHECK.md
│   ├── PRODUCTION_READINESS.md
│   ├── AUDIT_AND_UPDATE_PROPOSAL.md
│   ├── DEVELOPMENT.md
│   ├── TESTING.md
│   ├── SECURITY_POLICY.md
│   ├── GDPR_COMPLIANCE.md
│   ├── AUDIT_TRAIL.md
│   ├── IDEAS_ROADMAP.md
│   ├── LIBRAL_CORE_PYTHON_REFERENCE.md
│   ├── API_KB.md
│   ├── API_SELFEVOLUTION.md
│   ├── API_COMMUNICATION.md
│   ├── UI_C3_CONSOLE.md
│   ├── UI_DASHBOARD.md
│   ├── PAYMENT_SYSTEM.md
│   ├── modules/                     # モジュール別説明
│   │   ├── AEG.md
│   │   ├── AEGIS_PGP.md
│   │   ├── KBE.md
│   │   ├── LPO.md
│   │   ├── VAPORIZATION.md
│   │   ├── COMMUNICATION.md
│   │   └── PERSONAL_LOG.md
│   ├── reports                      # プラグインマーケット完了報告（拡張子なし）
│   ├── REFACTOR_VERIFICATION_REPORT.md
│   ├── LIBRAL_CORE_MIGRATION_STRATEGY.md
│   ├── TELEGRAM_PERSONAL_LOG_PROTOCOL.md
│   ├── TELEGRAM_TOPICS_HASHTAGS_IMPROVEMENT_REPORT.md
│   ├── WEEK_1_COMPLETION_REPORT.md
│   ├── WEEK_3_AUTH_COMPLETION_REPORT.md
│   ├── WEEK_4_COMMUNICATION_COMPLETION_REPORT.md
│   ├── WEEK_5_EVENTS_COMPLETION_REPORT.md
│   ├── WEEK_6_PAYMENTS_COMPLETION_REPORT.md
│   └── WEEK_7_API_HUB_COMPLETION_REPORT.md
│
├── libral-core/                     # Python (FastAPI) サブプロジェクト
│   ├── .env.example
│   ├── main.py
│   ├── pyproject.toml
│   ├── README.md
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── docs/
│   ├── libral_core/                 # 統合モジュール・ライブラリ
│   │   ├── config.py
│   │   ├── integrated_modules/      # LIC, LEB, LAS, LGL
│   │   ├── library/
│   │   └── modules/                 # auth, ai, app, payments, etc.
│   ├── models/
│   │   └── README.md                # GGUF 取得手順
│   ├── policies/
│   ├── src/                         # プロトコルモジュール
│   └── tests/
│
├── archive/                         # 廃止・参照用（最小限）
│   └── README.md
│
├── attached_assets/                 # 添付画像・スクショ（任意）
│
└── dist/                            # ビルド出力 (gitignore)
    ├── index.js
    └── public/
```

---

## 運用のポイント

- **起動**: `npm run dev`（Node）。Python は `libral-core` で `uvicorn` 等。
- **テスト**: `npm run test`（Vitest）, `npm run test:e2e`（Playwright。事前にサーバー起動）。
- **環境変数**: `docs/ENV_VARIABLES_CHECKLIST.md` とルート `.env.example`。
- **モジュール開発**: `docs/CORE_DEFINITIONS.md` と `docs/MODULE_DEVELOPMENT_LIFECYCLE.md` に従う。

---

## 参照

- ドキュメント入口: [docs/INDEX.md](docs/INDEX.md)
- 本番・稼働: [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md)
- 環境変数: [docs/ENV_VARIABLES_CHECKLIST.md](docs/ENV_VARIABLES_CHECKLIST.md)
