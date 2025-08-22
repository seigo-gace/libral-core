// server/adapters/email.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class EmailAdapter implements TransportAdapter {
  constructor(private smtpUrl?: string, private from?: string) {}
  name() { return "email"; }
  async health() { return Boolean(this.smtpUrl && this.from); }
  async send(_input: SendInput): Promise<SendResult> {
    try {
      // 本番：nodemailer で PGP/MIME の暗号化済み payload を送信
      return { ok: true, id: "mail:queued" };
    } catch (e:any) {
      return { ok: false, error: String(e) };
    }
  }
}