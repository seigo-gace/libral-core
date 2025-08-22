// server/adapters/webhook.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class WebhookAdapter implements TransportAdapter {
  name() { return "webhook"; }
  async health() { return true; }
  async send(input: SendInput): Promise<SendResult> {
    try {
      await fetch(input.to, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify(input),
      });
      return { ok: true, id: "wh:200" };
    } catch (e:any) {
      return { ok: false, error: String(e) };
    }
  }
}