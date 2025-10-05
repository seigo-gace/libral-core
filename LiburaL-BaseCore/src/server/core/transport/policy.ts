// server/core/transport/policy.ts
import fs from "node:fs";
import path from "node:path";
import yaml from "yaml";

export type RoutingRule = { 
  if: Record<string, string>; 
  then: { priority: string[] }; 
};

export type RoutingConfig = {
  routing: {
    default: { priority: string[] };
    by_tenant?: Record<string, { priority: string[] }>;
    by_usecase?: Record<string, { priority: string[] }>;
    rules?: RoutingRule[];
  };
  retry: { 
    max_attempts: number; 
    backoff_ms: number[]; 
  };
  circuit_breaker: { 
    failure_threshold: number; 
    cool_down_sec: number; 
  };
};

export function loadRoutingConfig(file = path.resolve(process.cwd(), "config/routing.yaml")): RoutingConfig {
  try {
    const content = fs.readFileSync(file, "utf-8");
    return yaml.parse(content) as RoutingConfig;
  } catch (error) {
    console.warn(`Failed to load routing config from ${file}, using defaults:`, error);
    return getDefaultConfig();
  }
}

function getDefaultConfig(): RoutingConfig {
  return {
    routing: {
      default: { priority: ["telegram", "email", "webhook"] }
    },
    retry: {
      max_attempts: 3,
      backoff_ms: [1000, 2000, 5000]
    },
    circuit_breaker: {
      failure_threshold: 5,
      cool_down_sec: 60
    }
  };
}

export function decidePriority(
  cfg: RoutingConfig,
  meta: { tenant_id: string; usecase: string; sensitivity: string; size_bytes: number }
): string[] {
  // Check tenant-specific routing first
  if (cfg.routing.by_tenant?.[meta.tenant_id]) {
    return cfg.routing.by_tenant[meta.tenant_id].priority;
  }

  // Check usecase-specific routing
  if (cfg.routing.by_usecase?.[meta.usecase]) {
    return cfg.routing.by_usecase[meta.usecase].priority;
  }

  // Check conditional rules
  if (cfg.routing.rules) {
    for (const rule of cfg.routing.rules) {
      const matches = Object.entries(rule.if).every(([key, value]) => {
        if (key === "sensitivity") {
          return meta.sensitivity === value;
        }
        if (key === "data_size_mb") {
          const operator = value.slice(0, 2);
          const threshold = Number(value.slice(2));
          const sizeMB = meta.size_bytes / (1024 * 1024);
          
          if (operator === ">=") return sizeMB >= threshold;
          if (operator === "<=") return sizeMB <= threshold;
          return false;
        }
        return false;
      });
      
      if (matches) {
        return rule.then.priority;
      }
    }
  }

  // Fall back to default
  return cfg.routing.default.priority;
}