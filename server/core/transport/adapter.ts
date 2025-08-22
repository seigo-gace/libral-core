// server/core/transport/adapter.ts
export type SendInput = {
  to: string;                 // Telegram userId / email / webhook URL 等
  subject?: string;
  body: string;               // Base64（原則：暗号化済み）
  metadata: {
    tenant_id: string;
    usecase: string;          // 例: "secure-mail" | "artifact-sign"
    sensitivity: 'low'|'med'|'high';
    size_bytes: number;
    idempotency_key: string;  // 冪等化キー
  };
};

export type SendResult = { ok: boolean; id?: string; error?: string; transport?: string };

export interface TransportAdapter {
  name(): string;                              // "telegram" | "email" | "webhook" | ...
  health(): Promise<boolean>;                  // 簡易ヘルス
  send(input: SendInput): Promise<SendResult>; // 平文ログ禁止
}