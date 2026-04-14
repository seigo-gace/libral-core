# ローカル LLM モデル配置 (Sovereign Autarchy)

`worker.py` は **GGUF** 形式のモデルを読み込み、ローカルで推論します。  
モデルを置かない場合も起動は可能で、その場合は `[local-llm:not-ready]` を返し、Judge（外部 API）にフォールバックできます。

## 配置手順

1. **このディレクトリに `model.gguf` を置く**

   - 環境変数 `LOCAL_LLM_PATH` 未設定時は、**カレントディレクトリが libral-core のとき** `./models/model.gguf` が参照されます。
   - 例: `libral-core/models/model.gguf`

2. **推奨モデル例（Hugging Face 等）**

   - **Llama 3**: `Llama-3-8B-Instruct-Q4_K_M.gguf` などをダウンロードし、`model.gguf` にリネームして配置。
   - **Mistral**: `Mistral-7B-Instruct-v0.2-Q4_K_M.gguf` など。
   - **Gemma**: 対応 GGUF を同様に配置。

3. **ダウンロード例**

   **手動**: [Hugging Face](https://huggingface.co/models?library=gguf) で GGUF を検索 → ファイルをダウンロード → このフォルダに `model.gguf` として保存。

   **スクリプト例**（Hugging Face から取得する場合。要 `curl`。URL はモデルページの "Files and versions" で取得）:

   ```bash
   # このディレクトリ (libral-core/models) で実行
   # 例: 3B モデル（軽量）。8B を使う場合は該当 GGUF の URL に差し替え
   # export HF_URL="https://huggingface.co/<repo>/resolve/main/<filename>.gguf"
   # curl -L -o model.gguf "$HF_URL"
   ```

   `huggingface-cli` を使う場合: `pip install huggingface_hub` のあと、`huggingface-cli download <repo_id> <filename> --local-dir .` でこのフォルダに保存し、`model.gguf` にリネーム。

## 環境変数（任意）

| 変数 | デフォルト | 説明 |
|------|------------|------|
| `LOCAL_LLM_PATH` | `./models/model.gguf` | モデルファイルのパス |
| `LOCAL_LLM_CTX` | `4096` | コンテキスト長 |
| `LOCAL_LLM_GPU_LAYERS` | `-1` | GPU に載せるレイヤー数（-1 は全て） |
| `LOCAL_LLM_MAX_TOKENS` | `512` | 最大出力トークン数 |
| `LOCAL_LLM_DISABLED` | 未設定 | `1` / `true` にするとローカル推論を無効化 |

## 依存（オプション）

ローカル推論を使う場合:

```bash
pip install llama-cpp-python
```

未インストールでもアプリは起動し、該当時は `[local-llm:not-ready]` を返します。
