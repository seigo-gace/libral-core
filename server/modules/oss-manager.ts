/**
 * OSS Manager - Open Source AI Model Management (Sovereign Autarchy)
 * Delegates inference to Python Local LLM Worker when LIBRAL_PYTHON_URL is set.
 * Otherwise returns a fallback error so callers can handle Judge path.
 */

import { eventService } from "../services/events";

const PYTHON_BASE_URL = (process.env.LIBRAL_PYTHON_URL ?? "").replace(/\/$/, "");
const PYTHON_TIMEOUT_MS = Math.min(
  Math.max(parseInt(process.env.LIBRAL_PYTHON_TIMEOUT_MS ?? "60000", 10), 5000),
  120000
);
const LIBRAL_INTERNAL_SECRET = process.env.LIBRAL_INTERNAL_SECRET ?? "";

export interface OSSModel {
  id: string;
  name: string;
  category: 'general' | 'speed' | 'context' | 'audio' | 'vision';
  status: 'loaded' | 'unloaded' | 'loading' | 'error';
  memory_mb: number;
  last_used: string;
}

export interface ModelLoadRequest {
  model_id: string;
  priority: 'high' | 'normal' | 'low';
  auto_unload_after_ms?: number;
}

class OSSManager {
  readonly module_id = "oss-manager";
  readonly module_name = "OSS AI Model Manager";
  readonly version = "1.0.0";

  private models: Map<string, OSSModel> = new Map();
  private loaded_models: Set<string> = new Set();
  private readonly MAX_LOADED_MODELS = 3; // Memory constraint

  private readonly MODEL_REGISTRY: OSSModel[] = [
    {
      id: "llama3",
      name: "LLaMA 3",
      category: "general",
      status: "unloaded",
      memory_mb: 4096,
      last_used: new Date().toISOString()
    },
    {
      id: "mistral",
      name: "Mistral",
      category: "speed",
      status: "unloaded",
      memory_mb: 2048,
      last_used: new Date().toISOString()
    },
    {
      id: "falcon",
      name: "Falcon",
      category: "context",
      status: "unloaded",
      memory_mb: 8192,
      last_used: new Date().toISOString()
    },
    {
      id: "whisper",
      name: "Whisper",
      category: "audio",
      status: "unloaded",
      memory_mb: 1536,
      last_used: new Date().toISOString()
    },
    {
      id: "clip",
      name: "CLIP",
      category: "vision",
      status: "unloaded",
      memory_mb: 2048,
      last_used: new Date().toISOString()
    }
  ];

  async initialize(): Promise<void> {
    console.log(`[${this.module_id}] Initializing OSS Manager...`);

    // Register all models
    for (const model of this.MODEL_REGISTRY) {
      this.models.set(model.id, model);
    }

    // Pre-load default models
    await this.loadModel({ model_id: "mistral", priority: "normal" }); // Fast default

    console.log(`[${this.module_id}] OSS Manager initialized with ${this.models.size} models`);
  }

  async loadModel(request: ModelLoadRequest): Promise<boolean> {
    const model = this.models.get(request.model_id);

    if (!model) {
      console.error(`[${this.module_id}] Model ${request.model_id} not found`);
      return false;
    }

    if (model.status === "loaded") {
      console.log(`[${this.module_id}] Model ${request.model_id} already loaded`);
      model.last_used = new Date().toISOString();
      return true;
    }

    // Check if we need to unload models to make space
    if (this.loaded_models.size >= this.MAX_LOADED_MODELS) {
      await this.unloadLeastRecentlyUsed();
    }

    console.log(`[${this.module_id}] Loading model: ${model.name} (${model.memory_mb}MB)`);

    model.status = "loading";
    this.models.set(request.model_id, model);

    // Simulate loading time
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    model.status = "loaded";
    model.last_used = new Date().toISOString();
    this.loaded_models.add(request.model_id);
    this.models.set(request.model_id, model);

    // Log event
    await eventService.logEvent('oss_model_loaded', {
      model_id: request.model_id,
      model_name: model.name,
      category: model.category
    });

    // Auto-unload if specified
    if (request.auto_unload_after_ms) {
      setTimeout(() => {
        this.unloadModel(request.model_id);
      }, request.auto_unload_after_ms);
    }

    console.log(`[${this.module_id}] Model ${model.name} loaded successfully`);

    return true;
  }

  async unloadModel(model_id: string): Promise<boolean> {
    const model = this.models.get(model_id);

    if (!model) {
      return false;
    }

    if (model.status !== "loaded") {
      return false;
    }

    console.log(`[${this.module_id}] Unloading model: ${model.name}`);

    model.status = "unloaded";
    this.loaded_models.delete(model_id);
    this.models.set(model_id, model);

    await eventService.logEvent('oss_model_unloaded', {
      model_id,
      model_name: model.name
    });

    return true;
  }

  private async unloadLeastRecentlyUsed(): Promise<void> {
    let oldestModel: OSSModel | null = null;
    let oldestTime = Date.now();

    for (const modelId of this.loaded_models) {
      const model = this.models.get(modelId)!;
      const lastUsed = new Date(model.last_used).getTime();

      if (lastUsed < oldestTime) {
        oldestTime = lastUsed;
        oldestModel = model;
      }
    }

    if (oldestModel) {
      console.log(`[${this.module_id}] Auto-unloading least recently used: ${oldestModel.name}`);
      await this.unloadModel(oldestModel.id);
    }
  }

  async getModelByCategory(category: OSSModel['category']): Promise<OSSModel | null> {
    for (const model of this.models.values()) {
      if (model.category === category) {
        // Load if not loaded
        if (model.status !== "loaded") {
          await this.loadModel({ model_id: model.id, priority: "normal" });
        }
        return model;
      }
    }
    return null;
  }

  async inferWithModel(modelId: string, input: string): Promise<string> {
    const model = this.models.get(modelId);

    if (!model) {
      throw new Error(`Model ${modelId} not found`);
    }

    if (PYTHON_BASE_URL) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), PYTHON_TIMEOUT_MS);
        const headers: Record<string, string> = { "Content-Type": "application/json" };
        if (LIBRAL_INTERNAL_SECRET) headers["X-Internal-Secret"] = LIBRAL_INTERNAL_SECRET;
        const res = await fetch(`${PYTHON_BASE_URL}/api/ai/infer_local`, {
          method: "POST",
          headers,
          body: JSON.stringify({
            model_id: modelId,
            prompt: input,
            system_prompt: "You are a helpful assistant running locally.",
          }),
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        if (!res.ok) return "[local-infer:error]";
        const data = (await res.json()) as { text?: string };
        const text = data?.text ?? "";
        if (text.startsWith("[local-infer:error]") || text.startsWith("[local-llm:not-ready]"))
          return text;
        model.last_used = new Date().toISOString();
        this.models.set(modelId, model);
        return text;
      } catch (e) {
        const msg = (e as Error).name === "AbortError" ? "timeout" : (e as Error).message;
        return `[local-infer:error] ${msg}`;
      }
    }

    // No Python Worker: update metadata and return fallback
    model.last_used = new Date().toISOString();
    this.models.set(modelId, model);
    return "[local-infer:error] LIBRAL_PYTHON_URL not set";
  }

  getAllModels(): OSSModel[] {
    return Array.from(this.models.values());
  }

  getLoadedModels(): OSSModel[] {
    return Array.from(this.models.values()).filter(m => m.status === "loaded");
  }

  getStats() {
    const totalModels = this.models.size;
    const loadedModels = this.loaded_models.size;
    const totalMemoryMB = Array.from(this.models.values())
      .filter(m => m.status === "loaded")
      .reduce((sum, m) => sum + m.memory_mb, 0);

    return {
      total_models: totalModels,
      loaded_models: loadedModels,
      available_models: totalModels - loadedModels,
      total_memory_mb: totalMemoryMB,
      max_loaded_models: this.MAX_LOADED_MODELS
    };
  }

  async shutdown(): Promise<void> {
    console.log(`[${this.module_id}] Shutting down OSS Manager...`);

    // Unload all models
    for (const modelId of this.loaded_models) {
      await this.unloadModel(modelId);
    }

    this.models.clear();
    this.loaded_models.clear();
  }
}

// Singleton instance
export const ossManager = new OSSManager();
