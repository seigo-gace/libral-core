import { apiRequest } from "@/lib/queryClient";

export interface ChatRequest {
  message: string;
  model: "gemini" | "gpt" | "dual";
  context?: string;
  enforce_moonlight?: boolean;
}

export interface ChatResponse {
  response: string;
  model_used: string;
  dual_verification?: {
    gemini_response: string;
    gpt_response: string;
    discrepancy_detected: boolean;
    discrepancy_details?: string;
  };
  timestamp: string;
}

export interface AIEvalRequest {
  prompt: string;
  enable_dual_verification: boolean;
}

export interface AIEvalResponse {
  result: string;
  gemini_result?: string;
  gpt_result?: string;
  verification_status: "OK" | "DISCREPANCY" | "N/A";
  execution_time_ms: number;
}

export const aiApi = {
  chat: async (data: ChatRequest): Promise<ChatResponse> => {
    return apiRequest("/api/ai/chat", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  eval: async (data: AIEvalRequest): Promise<AIEvalResponse> => {
    return apiRequest("/api/ai/eval", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  ask: async (question: string, model: "gemini" | "gpt" = "gemini"): Promise<{ answer: string }> => {
    return apiRequest("/api/ai/ask", {
      method: "POST",
      body: JSON.stringify({ question, model }),
      headers: { "Content-Type": "application/json" },
    });
  },
};
