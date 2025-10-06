import { apiRequest } from "@/lib/queryClient";

export interface CRADTriggerRequest {
  recovery_type: "automatic" | "manual";
  target_service?: string;
  reason: string;
}

export interface CRADTriggerResponse {
  trigger_id: string;
  status: "initiated" | "in_progress" | "completed" | "failed";
  recovery_started_at: string;
  estimated_completion: string;
}

export interface AMMUnblockRequest {
  block_id: string;
  reason: string;
  override_code?: string;
}

export interface AMMUnblockResponse {
  success: boolean;
  unblocked_at: string;
  block_id: string;
  message: string;
}

export interface GovernanceStatus {
  amm_active: boolean;
  crad_active: boolean;
  blocked_ips_count: number;
  recovery_in_progress: boolean;
  last_audit_timestamp: string;
}

export const governanceApi = {
  triggerCRAD: async (data: CRADTriggerRequest): Promise<CRADTriggerResponse> => {
    return apiRequest("/governance/crad/trigger", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  unblockAMM: async (data: AMMUnblockRequest): Promise<AMMUnblockResponse> => {
    return apiRequest("/governance/amm/unblock", {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "Content-Type": "application/json" },
    });
  },

  getStatus: async (): Promise<GovernanceStatus> => {
    const res = await fetch("/governance/status");
    if (!res.ok) throw new Error("Failed to fetch governance status");
    return res.json();
  },

  getAuditLog: async (limit: number = 50) => {
    const res = await fetch(`/governance/audit-log?limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch audit log");
    return res.json();
  },
};
