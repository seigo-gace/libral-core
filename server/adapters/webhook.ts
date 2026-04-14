// server/adapters/webhook.ts
import { TransportAdapter, SendInput, SendResult } from "../core/transport/adapter";

export class WebhookAdapter implements TransportAdapter {
  name(): string {
    return "webhook";
  }

  async health(): Promise<boolean> {
    // Webhook adapter is always available as it doesn't require pre-configuration
    return true;
  }

  async send(input: SendInput): Promise<SendResult> {
    try {
      // Validate that destination is a valid URL
      let webhookUrl: URL;
      try {
        webhookUrl = new URL(input.to);
      } catch (urlError) {
        return {
          ok: false,
          error: `Invalid webhook URL: ${input.to}`
        };
      }

      // Prepare payload
      const payload = {
        timestamp: new Date().toISOString(),
        subject: input.subject,
        encrypted_data: input.body,
        metadata: input.metadata,
        source: "libral-transport-core"
      };

      const response = await fetch(webhookUrl.toString(), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Libral-Transport-Core/1.0'
        },
        body: JSON.stringify(payload),
        // 10 second timeout
        signal: AbortSignal.timeout(10000)
      });

      if (!response.ok) {
        return {
          ok: false,
          error: `Webhook returned ${response.status}: ${response.statusText}`
        };
      }

      return {
        ok: true,
        id: `webhook:${webhookUrl.hostname}:${Date.now()}`,
        transport: "webhook"
      };

    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          ok: false,
          error: "Webhook request timeout"
        };
      }
      
      return {
        ok: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
}