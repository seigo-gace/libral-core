/**
 * Mock / fixture data for API endpoints.
 * Replace with real storage (DB) when implementing production.
 */

export const fixtureUsers = [
  { id: "1", username: "admin", email: "admin@libral.core", telegramId: "123456789", status: "active", role: "admin", createdAt: "2024-01-01T00:00:00Z", lastActive: new Date().toISOString(), personalServerEnabled: true },
  { id: "2", username: "developer", email: "dev@libral.core", status: "active", role: "developer", createdAt: "2024-01-15T00:00:00Z", lastActive: new Date().toISOString(), personalServerEnabled: true },
  { id: "3", username: "user1", email: "user@libral.core", status: "active", role: "user", createdAt: "2024-02-01T00:00:00Z", lastActive: "2024-02-28T10:30:00Z", personalServerEnabled: false },
];

export const fixtureUserStats = {
  totalUsers: 3,
  activeUsers: 2,
  newUsersToday: 1,
  personalServersActive: 2,
};

export const fixtureCommunicationAdapters = [
  { id: "telegram-1", name: "Telegram Bot API", type: "telegram", status: "active", messagesProcessed: 1247, lastActivity: new Date().toISOString(), config: {} },
  { id: "email-1", name: "SMTP Gateway", type: "email", status: "active", messagesProcessed: 856, lastActivity: new Date().toISOString(), config: {} },
  { id: "webhook-1", name: "Webhook Endpoint", type: "webhook", status: "inactive", messagesProcessed: 23, lastActivity: new Date().toISOString(), config: {} },
];

export const fixtureCommunicationStats = { totalMessages: 2126, activeAdapters: 2, errorRate: 0.05, responseTime: 150 };

export const fixtureEventStats = { totalEvents: 15420, pendingEvents: 3, resolvedToday: 127, criticalEvents: 1 };

export const fixturePaymentStats = {
  totalRevenue: 12450.75,
  monthlyRevenue: 3250.5,
  telegramStarsEarned: 8500,
  pluginCommissions: 1850.25,
  pendingPayments: 5,
  refundRate: 1.2,
};

export const fixtureCredentials = [
  { id: "openai-1", name: "OpenAI GPT-4", provider: "openai", status: "active", usage: 15000, limit: 100000, cost: 125.5, currency: "USD", lastUsed: new Date().toISOString(), createdAt: "2024-01-01T00:00:00Z", encrypted: true },
  { id: "anthropic-1", name: "Claude 3.5 Sonnet", provider: "anthropic", status: "active", usage: 8500, limit: 50000, cost: 85.25, currency: "USD", lastUsed: new Date().toISOString(), createdAt: "2024-01-15T00:00:00Z", encrypted: true },
];

export const fixtureIntegrationStats = { totalCredentials: 5, activeIntegrations: 3, monthlyApiCalls: 285000, totalCost: 485.75 };

export const fixtureDatabaseConnections = [
  { id: "postgres-1", name: "PostgreSQL Primary", type: "postgresql", status: "connected", connections: "23/100", responseTime: 15, uptime: 99.9, dataSize: "2.5 GB" },
  { id: "redis-1", name: "Redis Cache", type: "redis", status: "connected", connections: "5/50", responseTime: 2, uptime: 99.8, dataSize: "256 MB" },
  { id: "neon-1", name: "Neon Serverless", type: "neon", status: "connected", connections: "12/unlimited", responseTime: 8, uptime: 99.9, dataSize: "1.8 GB" },
];

export const fixtureDatabaseMetrics = { totalConnections: "23/100", queryPerSecond: 156, cacheHitRate: 94.2, diskUsage: "2.5 GB" };

export const fixtureContainers = [
  { id: "app-1", name: "libral-core-app", image: "node:22-alpine", status: "running", cpuUsage: 15, memoryUsage: 68, networkIO: "1.2MB/s", uptime: "2d 15h", ports: ["5000:5000"] },
  { id: "db-1", name: "postgres-db", image: "postgres:16", status: "running", cpuUsage: 5, memoryUsage: 25, networkIO: "0.5MB/s", uptime: "2d 15h", ports: ["5432:5432"] },
];

export const fixtureContainerStats = { totalContainers: 2, runningContainers: 2, cpuTotal: 20, memoryTotal: 46.5 };

export const fixtureAegisKeys = [
  { keyId: "F1B2C3D4E5F6G7H8", keyType: "EdDSA", userId: "Libral Admin <admin@libral.core>", fingerprint: "F1B2 C3D4 E5F6 G7H8 I9J0 K1L2 M3N4 O5P6 Q7R8 S9T0", createdAt: "2024-01-01", expiresAt: "2026-01-01", status: "active" },
  { keyId: "A9B8C7D6E5F4G3H2", keyType: "RSA-4096", userId: "System Backup <backup@libral.core>", fingerprint: "A9B8 C7D6 E5F4 G3H2 I1J0 K9L8 M7N6 O5P4 Q3R2 S1T0", createdAt: "2024-01-15", expiresAt: "2029-01-15", status: "active" },
];

export const fixtureSettings = {
  general: { systemName: "Libral Core", adminEmail: "admin@libral.core", maintenanceMode: false, debugMode: false, logLevel: "info" },
  security: { sessionTimeout: 24, maxLoginAttempts: 3, passwordPolicy: "strong", twoFactorRequired: true, encryptionLevel: "aegis-pgp" },
  notifications: { emailNotifications: true, telegramNotifications: true, webhookNotifications: false, notificationThreshold: "medium" },
  performance: { cacheEnabled: true, cacheTTL: 3600, maxConcurrentUsers: 1000, rateLimitEnabled: true, rateLimitPerMinute: 100 },
};

export const fixtureSystemAnalytics = { totalRequests: 125847, averageResponseTime: 45, uptime: 99.8, errorRate: 0.12, peakConcurrentUsers: 156, dataTransferred: "2.8 TB" };

export const fixtureModuleAnalytics = { totalModules: 8, activeModules: 7, healthyModules: 6, moduleRestarts: 3, averageUptime: 99.5 };

export const fixtureInfrastructureDatabase = { connections: "23/100", size: "2.4 GB", queriesPerSecond: 156, replicationStatus: "同期済み" };
export const fixtureInfrastructureDocker = { runningContainers: "7/8", cpuUsage: "31%", memoryUsage: "2.1 GB", volumes: 12 };

export const emojiSuggestions: Record<string, string[]> = {
  楽しい: ["😊", "🎉", "✨"],
  おつかれ: ["😌", "🌟", "💪"],
  ありがとう: ["🙏", "💖", "🌸"],
  おめでとう: ["🎊", "🎈", "🏆"],
  がんばって: ["💪", "🔥", "⭐"],
  default: ["😊", "✨", "🎈"],
};
