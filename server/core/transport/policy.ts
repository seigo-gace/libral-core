// server/core/transport/policy.ts
import fs from "node:fs";
import path from "node:path";
import yaml from "yaml";

export type RoutingRule = { if: Record<string, string>, then: { priority: string[] } };
export type RoutingConfig = {
  routing: {
    default: { priority: string[] };
    by_tenant?: Record<string, { priority: string[] }>;
    by_usecase?: Record<string, { priority: string[] }>;
    rules?: RoutingRule[];
  };
  retry: { max_attempts: number; backoff_ms: number[] };
  circuit_breaker: { failure_threshold: number; cool_down_sec: number };
};

export function loadRoutingConfig(
  file = path.resolve(process.cwd(), "config/routing.yaml")
): RoutingConfig {
  const raw = fs.readFileSync(file, "utf-8");
  return yaml.parse(raw) as RoutingConfig;
}

export function decidePriority(
  cfg: RoutingConfig,
  meta: { tenant_id: string; usecase: string; sensitivity: string; size_bytes: number }
): string[] {
  if (cfg.routing.by_tenant?.[meta.tenant_id]) return cfg.routing.by_tenant[meta.tenant_id].priority;
  if (cfg.routing.by_usecase?.[meta.usecase])  return cfg.routing.by_usecase[meta.usecase].priority;

  if (cfg.routing.rules) {
    for (const r of cfg.routing.rules) {
      const cond = r.if || {};
      const ok = Object.entries(cond).every(([k, v]) => {
        if (k === "sensitivity") return meta.sensitivity === v;
        if (k === "data_size_mb") {
          const op = v.slice(0,2); const num = Number(v.slice(2));
          const mb = meta.size_bytes / (1024*1024);
          return op === ">=" ? mb >= num : op === "<=" ? mb <= num : false;
        }
        return false;
      });
      if (ok) return r.then.priority;
    }
  }
  return cfg.routing.default.priority;
}