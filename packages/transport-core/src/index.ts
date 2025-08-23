// packages/transport-core/src/index.ts

// Core transport interfaces and types
export type {
  SendInput,
  SendResult,
  TransportAdapter
} from "../../../server/core/transport/adapter";

export type {
  RoutingRule,
  RoutingConfig
} from "../../../server/core/transport/policy";

export { 
  loadRoutingConfig, 
  decidePriority 
} from "../../../server/core/transport/policy";

export { TransportRouter } from "../../../server/core/transport/router";
export { initTransport, getTransportRouter } from "../../../server/core/transport/bootstrap";

// Re-export adapters for external use
export { TelegramAdapter } from "../../../server/adapters/telegram";
export { EmailAdapter } from "../../../server/adapters/email";
export { WebhookAdapter } from "../../../server/adapters/webhook";

// Re-export crypto client
export {
  encrypt,
  decrypt,
  sign,
  verify,
  getWkdPath,
  inspect,
  aegisClient,
  mockAegisClient
} from "../../../server/crypto/aegisClient";

// Version info
export const version = "1.0.0";