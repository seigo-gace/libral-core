// server/adapters/telegram.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class TelegramAdapter implements TransportAdapter {
  constructor(
    private token: string,
    private resolveChatId: (to: string) => string
  ) {}

  name(): string {
    return "telegram";
  }

  async health(): Promise<boolean> {
    return Boolean(this.token);
  }

  async send(input: SendInput): Promise<SendResult> {
    try {
      if (!this.token) {
        return { ok: false, error: "TELEGRAM_BOT_TOKEN not configured" };
      }

      const chatId = this.resolveChatId(input.to);
      
      // For encrypted data, we send as a document to preserve formatting
      const formData = new FormData();
      formData.append('chat_id', chatId);
      formData.append('document', new Blob([input.body], { type: 'application/pgp-encrypted' }), 'encrypted_message.pgp');
      
      if (input.subject) {
        formData.append('caption', input.subject);
      }

      const response = await fetch(`https://api.telegram.org/bot${this.token}/sendDocument`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return { 
          ok: false, 
          error: `Telegram API error: ${response.status} ${errorData.description || response.statusText}` 
        };
      }

      const result = await response.json();
      return { 
        ok: true, 
        id: `tg:${result.result.message_id}`,
        transport: "telegram"
      };

    } catch (error) {
      return { 
        ok: false, 
        error: error instanceof Error ? error.message : String(error) 
      };
    }
  }
}