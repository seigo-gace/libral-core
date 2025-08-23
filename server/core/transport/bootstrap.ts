// server/core/transport/bootstrap.ts
import { TransportRouter } from "./router";
import { loadRoutingConfig } from "./policy";
import { TelegramAdapter } from "../../adapters/telegram";
import { EmailAdapter } from "../../adapters/email";
import { WebhookAdapter } from "../../adapters/webhook";

let _router: TransportRouter | null = null;

// Audit event emission - integrate with existing event system
const emitAudit = (evt: any) => {
  console.log(`[TRANSPORT] ${evt.type}:`, JSON.stringify(evt, null, 2));
  // TODO: Integrate with existing eventService.emit() or Redis publish
  // For now, we'll just log. In production, this should publish to Redis/WebSocket
};

export function getTransportRouter(): TransportRouter {
  if (!_router) {
    throw new Error("Transport router not initialized. Call initTransport() first.");
  }
  return _router;
}

export function initTransport(): void {
  if (_router) {
    console.log("[TRANSPORT] Router already initialized");
    return;
  }

  console.log("[TRANSPORT] Initializing transport system...");
  
  try {
    const config = loadRoutingConfig();
    
    // Initialize adapters with environment configuration
    const telegramAdapter = new TelegramAdapter(
      process.env.TELEGRAM_BOT_TOKEN || "",
      (to: string) => to // Simple identity function, can be enhanced for user ID resolution
    );
    
    const emailAdapter = new EmailAdapter(
      process.env.SMTP_URL,
      process.env.MAIL_FROM || "Libral Core <no-reply@example.com>"
    );
    
    const webhookAdapter = new WebhookAdapter();
    
    // Create router with all adapters
    _router = new TransportRouter(
      [telegramAdapter, emailAdapter, webhookAdapter],
      config,
      emitAudit
    );
    
    console.log("[TRANSPORT] Router initialized with adapters:", 
      [telegramAdapter, emailAdapter, webhookAdapter].map(a => a.name()));
    
  } catch (error) {
    console.error("[TRANSPORT] Failed to initialize transport system:", error);
    throw error;
  }
}