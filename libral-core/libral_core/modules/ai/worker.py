"""
Local LLM Worker - Sovereign Autarchy
Runs OSS models (LLaMA/Mistral/Gemma via GGUF) in-process.
Sync llama_cpp is run in ThreadPoolExecutor to avoid blocking the event loop.
"""

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from llama_cpp import Llama
except Exception:
    Llama = None

# Optional: avoid loading heavy model in tests
_LOCAL_LLM_DISABLED = os.getenv("LOCAL_LLM_DISABLED", "").lower() in ("1", "true", "yes")


class LocalLLMWorker:
    """Local OSS model inference. Singleton, lazy-loads one model."""

    _instance = None
    _model = None
    _pool = ThreadPoolExecutor(max_workers=1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self) -> None:
        if _LOCAL_LLM_DISABLED:
            self._model = None
            return
        model_path = os.getenv("LOCAL_LLM_PATH", "./models/model.gguf")
        if not Llama or not os.path.exists(model_path):
            self._model = None
            return
        try:
            self._model = Llama(
                model_path=model_path,
                n_ctx=int(os.getenv("LOCAL_LLM_CTX", "4096")),
                n_gpu_layers=int(os.getenv("LOCAL_LLM_GPU_LAYERS", "-1")),
                verbose=False,
            )
        except Exception:
            self._model = None

    def _infer_sync(self, prompt: str) -> str:
        if not self._model:
            return "[local-llm:not-ready]"
        max_tokens = int(os.getenv("LOCAL_LLM_MAX_TOKENS", "512"))
        out = self._model(
            prompt,
            max_tokens=max_tokens,
            stop=["<|eot_id|>", "<|end_of_text|>"],
            echo=False,
        )
        text = (out.get("choices") or [{}])[0].get("text") or ""
        return text.strip()

    async def infer(self, user_prompt: str, system_prompt: str = "") -> str:
        prompt = (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
            f"{system_prompt}\n<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            f"{user_prompt}\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(self._pool, self._infer_sync, prompt)
