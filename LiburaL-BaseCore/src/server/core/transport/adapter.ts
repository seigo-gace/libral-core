// server/core/transport/adapter.ts

export type SendInput = {
  to: string;                 // telegram userId / email / webhook URL
  subject?: string;
  body: string;               // Base64 (encrypted data)
  metadata: {
    tenant_id: string;
    usecase: string;          // "secure-mail" | "artifact-sign" | "notification"
    sensitivity: 'low' | 'med' | 'high';
    size_bytes: number;
    idempotency_key: string;  // For deduplication
  };
};

export type SendResult = { 
  ok: boolean; 
  id?: string; 
  error?: string; 
  transport?: string;
  retryAfter?: number; // seconds
};

export interface TransportAdapter {
  name(): string;
  health(): Promise<boolean>;
  send(input: SendInput): Promise<SendResult>;
}