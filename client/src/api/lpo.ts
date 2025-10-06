import { apiRequest } from "@/lib/queryClient";

export interface HealthScoreResponse {
  health_score: number;
  status: string;
  message: string;
  metrics: {
    amm_blocked_count: number;
    crad_recovery_success_rate: number;
    system_uptime_percentage: number;
    avg_response_time_ms: number;
    error_rate_percentage: number;
  };
}

export interface PolicyUpdateRequest {
  policy_type: string;
  enabled: boolean;
  threshold?: number;
}

export interface ZKAuditResponse {
  audit_id: string;
  status: "passed" | "failed" | "pending";
  proof_valid: boolean;
  timestamp: string;
}

export interface SelfHealingResponse {
  suggestions: Array<{
    id: string;
    priority: number;
    category: string;
    description: string;
    recovery_steps: string[];
  }>;
}

export interface FinanceMetrics {
  total_cost_7days: number;
  ai_api_costs: {
    openai: number;
    gemini: number;
    total: number;
  };
  plugin_revenue: number;
  cost_trend: "increasing" | "stable" | "decreasing";
}

export interface PredictiveAlert {
  alert_id: string;
  severity: "low" | "medium" | "high" | "critical";
  metric_name: string;
  current_value: number;
  z_score: number;
  predicted_issue: string;
}

export const lpoApi = {
  getHealthScore: async (): Promise<HealthScoreResponse> => {
    const res = await fetch("/lpo/metrics/health-score");
    if (!res.ok) throw new Error("Failed to fetch health score");
    return res.json();
  },

  updatePolicy: async (data: PolicyUpdateRequest): Promise<{ success: boolean }> => {
    return apiRequest("/lpo/control/update-policy", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  getZKAuditStatus: async (): Promise<ZKAuditResponse> => {
    const res = await fetch("/lpo/zk-audit/status");
    if (!res.ok) throw new Error("Failed to fetch ZK audit status");
    return res.json();
  },

  getSelfHealingSuggestions: async (): Promise<SelfHealingResponse> => {
    const res = await fetch("/lpo/self-healing/suggestions");
    if (!res.ok) throw new Error("Failed to fetch self-healing suggestions");
    return res.json();
  },

  getFinanceMetrics: async (days: number = 7): Promise<FinanceMetrics> => {
    const res = await fetch(`/lpo/finance/metrics?days=${days}`);
    if (!res.ok) throw new Error("Failed to fetch finance metrics");
    return res.json();
  },

  getPredictiveAlerts: async (): Promise<PredictiveAlert[]> => {
    const res = await fetch("/lpo/predictive/alerts");
    if (!res.ok) throw new Error("Failed to fetch predictive alerts");
    return res.json();
  },

  getDashboard: async () => {
    const res = await fetch("/lpo/dashboard");
    if (!res.ok) throw new Error("Failed to fetch LPO dashboard");
    return res.json();
  },
};
