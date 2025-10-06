import { apiRequest } from "@/lib/queryClient";

export interface PRGenerateRequest {
  suggestion_id: string;
  branch_name?: string;
  commit_message?: string;
}

export interface PRGenerateResponse {
  pr_id: string;
  pr_url: string;
  status: "created" | "pending" | "failed";
  branch_name: string;
  files_changed: number;
}

export interface EvolutionTask {
  task_id: string;
  priority: number;
  category: string;
  description: string;
  status: "pending" | "in_progress" | "completed" | "cancelled";
  created_at: string;
  auto_generated: boolean;
}

export interface PrioritizationResult {
  suggestion_ids: string[];
  total_analyzed: number;
  health_score_used: number;
  mttr_stats: {
    avg_recovery_time: number;
    success_rate: number;
  };
}

export const aegApi = {
  generatePR: async (data: PRGenerateRequest): Promise<PRGenerateResponse> => {
    return apiRequest("/aeg/pr/generate", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  analyzeAndPrioritize: async (): Promise<PrioritizationResult> => {
    return apiRequest("/aeg/analyze-and-prioritize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
  },

  getTopPriorities: async (limit: number = 10): Promise<EvolutionTask[]> => {
    const res = await fetch(`/aeg/top-priorities?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch top priorities");
    return res.json();
  },

  createTask: async (task: Partial<EvolutionTask>): Promise<{ task_id: string }> => {
    return apiRequest("/aeg/create-task", {
      method: "POST",
      body: JSON.stringify(task),
      headers: { "Content-Type": "application/json" },
    });
  },

  getDashboard: async () => {
    const res = await fetch("/aeg/dashboard");
    if (!res.ok) throw new Error("Failed to fetch AEG dashboard");
    return res.json();
  },
};
