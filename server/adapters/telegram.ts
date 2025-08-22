// server/adapters/telegram.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class TelegramAdapter implements TransportAdapter {
  constructor(private token: string, private resolveChatId: (to: string)=>string) {}
  name() { return "telegram"; }
  async health() { return Boolean(this.token); }
  async send(input: SendInput): Promise<SendResult> {
    try {
      const chatId = this.resolveChatId(input.to);
      // ここで Telegram API 呼び出し（本文の平文ログは禁止）
      // 例）fetch(`https://api.telegram.org/bot${this.token}/sendDocument`, { ... })
      return { ok: true, id: `tg:${chatId}` };
    } catch (e:any) {
      return { ok: false, error: String(e) };
    }
  }
}