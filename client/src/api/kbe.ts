import { apiRequest } from "@/lib/queryClient";

export interface KnowledgeSubmitRequest {
  content: string;
  category: string;
  tags?: string[];
  user_id?: string;
}

export interface KnowledgeSubmitResponse {
  knowledge_id: string;
  submitted_at: string;
  privacy_preserved: boolean;
}

export interface KnowledgeLookupRequest {
  query: string;
  category?: string;
  limit?: number;
}

export interface KnowledgeRecord {
  id: string;
  content: string;
  category: string;
  tags: string[];
  relevance_score: number;
  created_at: string;
}

export interface FederatedTrainingStatus {
  training_active: boolean;
  participants_count: number;
  current_round: number;
  model_accuracy: number;
}

export const kbeApi = {
  submitKnowledge: async (data: KnowledgeSubmitRequest): Promise<KnowledgeSubmitResponse> => {
    return apiRequest("/kbe/submit-knowledge", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  lookupKnowledge: async (data: KnowledgeLookupRequest): Promise<KnowledgeRecord[]> => {
    const params = new URLSearchParams({
      query: data.query,
      ...(data.category && { category: data.category }),
      ...(data.limit && { limit: data.limit.toString() }),
    });
    const res = await fetch(`/kbe/knowledge-lookup?${params}`);
    if (!res.ok) throw new Error("Failed to lookup knowledge");
    return res.json();
  },

  getFederatedStatus: async (): Promise<FederatedTrainingStatus> => {
    const res = await fetch("/kbe/federated/status");
    if (!res.ok) throw new Error("Failed to fetch federated status");
    return res.json();
  },

  getDashboard: async () => {
    const res = await fetch("/kbe/dashboard");
    if (!res.ok) throw new Error("Failed to fetch KBE dashboard");
    return res.json();
  },
};
