// server/adapters/email.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class EmailAdapter implements TransportAdapter {
  constructor(
    private smtpUrl?: string,
    private fromAddress?: string
  ) {}

  name(): string {
    return "email";
  }

  async health(): Promise<boolean> {
    return Boolean(this.smtpUrl && this.fromAddress);
  }

  async send(input: SendInput): Promise<SendResult> {
    try {
      if (!this.smtpUrl || !this.fromAddress) {
        return { 
          ok: false, 
          error: "SMTP_URL or MAIL_FROM not configured" 
        };
      }

      // TODO: Implement actual SMTP sending using nodemailer or similar
      // For now, this is a mock implementation
      console.log(`[EMAIL] Mock sending to ${input.to}:`);
      console.log(`  From: ${this.fromAddress}`);
      console.log(`  Subject: ${input.subject || 'Encrypted Message'}`);
      console.log(`  Body size: ${input.body.length} characters (Base64)`);
      console.log(`  Metadata:`, input.metadata);

      // Simulate network delay
      await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));

      // Mock success with high probability
      const shouldSucceed = Math.random() > 0.1; // 90% success rate
      
      if (shouldSucceed) {
        return {
          ok: true,
          id: `email:${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          transport: "email"
        };
      } else {
        return {
          ok: false,
          error: "Mock SMTP timeout"
        };
      }

    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
}