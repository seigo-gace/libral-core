import { apiRequest } from "@/lib/queryClient";

export interface VaporizationStats {
  vaporization_enabled: boolean;
  max_ttl_hours: number;
  ttl_enforced_count: number;
  flush_executed_count: number;
  patterns_protected: string[];
}

export interface TTLEnforcementRequest {
  pattern: string;
  ttl_seconds: number;
}

export interface FlushRequest {
  pattern: string;
  reason: string;
}

export const vaporizationApi = {
  getStats: async (): Promise<VaporizationStats> => {
    const res = await fetch("/vaporization/stats");
    if (!res.ok) throw new Error("Failed to fetch vaporization stats");
    return res.json();
  },

  enforceTTL: async (data: TTLEnforcementRequest): Promise<{ success: boolean }> => {
    return apiRequest("/vaporization/ttl/enforce", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  flush: async (data: FlushRequest): Promise<{ success: boolean; items_flushed: number }> => {
    return apiRequest("/vaporization/flush", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  getDashboard: async () => {
    const res = await fetch("/vaporization/dashboard");
    if (!res.ok) throw new Error("Failed to fetch vaporization dashboard");
    return res.json();
  },
};
