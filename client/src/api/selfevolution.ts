import { apiRequest } from "@/lib/queryClient";

export interface SelfEvolutionDashboard {
  selfevolution_v1: {
    version: string;
    manifest: string;
    last_updated: string;
  };
  health_status: {
    overall_health_score: number;
    status: string;
    lpo_auto_recovery_count: number;
  };
  knowledge_base: {
    total_knowledge_records: number;
    privacy_mode: boolean;
    unique_contributors: number;
  };
  evolution_queue: {
    pending_tasks: number;
    in_progress: number;
    completed: number;
    top_priorities: any[];
  };
  privacy_guarantees: {
    max_cache_ttl_hours: number;
    vaporization_enabled: boolean;
    ttl_enforced_count: number;
    flush_executed_count: number;
  };
  financial_health: {
    cost_summary_7days: any;
    ai_cost_optimization_active: boolean;
  };
}

export interface ExecuteCycleRequest {
  trigger_source: "scheduled" | "manual" | "alert";
}

export interface ExecuteCycleResponse {
  cycle_id: string;
  trigger_source: string;
  executed_at: string;
  results: {
    health_score: {
      score: number;
      status: string;
      message: string;
    };
    knowledge_analysis: any;
    prioritization: {
      suggestions_generated: number;
      tasks_created: number;
      task_ids: string[];
    };
    vaporization: {
      cache_items_flushed: number;
      privacy_maintained: boolean;
    };
  };
  next_cycle: string;
}

export interface ModuleHealth {
  lpo: {
    status: string;
    health_score: number;
    last_check: string;
  };
  kbe: {
    status: string;
    privacy_mode: boolean;
    records_count: number;
  };
  aeg: {
    status: string;
    auto_evolution_enabled: boolean;
    total_tasks: number;
  };
  vaporization: {
    status: string;
    vaporization_enabled: boolean;
    max_ttl_hours: number;
  };
}

export const selfEvolutionApi = {
  getDashboard: async (): Promise<SelfEvolutionDashboard> => {
    const res = await fetch("/selfevolution/dashboard");
    if (!res.ok) throw new Error("Failed to fetch SelfEvolution dashboard");
    return res.json();
  },

  executeCycle: async (data: ExecuteCycleRequest): Promise<ExecuteCycleResponse> => {
    return apiRequest("/selfevolution/execute-cycle", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  getModuleHealth: async (): Promise<ModuleHealth> => {
    const res = await fetch("/selfevolution/module-health");
    if (!res.ok) throw new Error("Failed to fetch module health");
    return res.json();
  },

  getManifest: async () => {
    const res = await fetch("/selfevolution/manifest");
    if (!res.ok) throw new Error("Failed to fetch manifest");
    return res.json();
  },
};
