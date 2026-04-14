# Libral Core (Python)

RIPLIT 向けアプリのオプション Python バックエンド。Node サーバーとは独立して利用可能。

## 構成

| ディレクトリ | 役割 |
|-------------|------|
| **`libral_core/`** | 統合モジュール（auth, ai, app, communication, events, gpg, marketplace, payments, api_hub）と共通ライブラリ（utils, api_clients, file_handlers）。テストから参照。 |
| **`src/`** | プロトコルモジュール（AEG, KBE, LPO, Vaporization）とガバナンス。`src/library/components/` で日時・暗号・バリデーションを共有。 |

## テスト

```bash
cd libral-core
pip install -e .
pytest tests/ -v
```

## モジュール管理（トラブル検知 → モジュール特定 → 変更）

- **`docs/modules.yaml`** — Python モジュール一覧（機械可読）。
- **`docs/MODULE_REGISTRY.md`** — 運用フロー・一覧・交換手順。**CRAD（自動debug）** はトラブル検知の中心で、アラートに基づきリカバリし、モジュール特定 → 変更につなげる。

## Sovereign Autarchy（ローカル Worker）

- **`libral_core/modules/ai/worker.py`** — ローカル OSS モデル（LLaMA/Mistral 等 GGUF）で推論。Node の OSS Manager は `LIBRAL_PYTHON_URL` 経由で `POST /api/ai/infer_local` を呼ぶ。
- 環境変数: `LOCAL_LLM_PATH`（.gguf パス）, `LOCAL_LLM_CTX`, `LOCAL_LLM_GPU_LAYERS`, `LOCAL_LLM_MAX_TOKENS`, `LOCAL_LLM_DISABLED`（未設定時は Worker 有効）。
- **llama-cpp-python** は任意。未インストール時は `[local-llm:not-ready]` を返し、Judge 側にフォールバック可能。

## 重複について

- `libral_core/library/utils/` と `src/library/components/` は別目的で存在（統合用 vs プロトコル用）。将来的に一本化する場合は `libral_core.library` を共通化して `src` から参照する形を推奨。
