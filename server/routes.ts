import type { FastifyInstance } from "fastify";
import {
  kbEntryCreateSchema,
  kbEntryUpdateSchema,
  kbSearchSchema,
  kbeSubmitSchema,
  kbeLookupSchema,
} from "@shared/requestSchemas";
import { storage } from "./storage";
import { telegramService } from "./services/telegram";
import { eventService } from "./services/events";
import { redisService } from "./services/redis";
import { websocketService } from "./services/websocket";
import { getTransportRouter } from "./core/transport/bootstrap";
import { moduleRegistry } from "./modules/registry";
import { registerAegisRoutes } from "./routes/aegis";
import { kbSystem } from "./modules/kb-system";
import { evaluator } from "./modules/evaluator";
import { ossManager } from "./modules/oss-manager";
import { aiRouter } from "./core/ai-router";
import { embeddingLayer } from "./modules/embedding";
import {
  fixtureUsers,
  fixtureUserStats,
  fixtureCommunicationAdapters,
  fixtureCommunicationStats,
  fixtureEventStats,
  fixturePaymentStats,
  fixtureCredentials,
  fixtureIntegrationStats,
  fixtureDatabaseConnections,
  fixtureDatabaseMetrics,
  fixtureContainers,
  fixtureContainerStats,
  fixtureAegisKeys,
  fixtureSettings,
  fixtureSystemAnalytics,
  fixtureModuleAnalytics,
  fixtureInfrastructureDatabase,
  fixtureInfrastructureDocker,
  emojiSuggestions,
} from "./data/fixtures";

export async function registerRoutes(fastify: FastifyInstance): Promise<void> {
  await redisService.connect();
  registerAegisRoutes(fastify);

  // Telegram webhook (Telegraf handleUpdate inside telegramService)
  // WEBHOOK_SECRET 設定時は x-telegram-bot-api-secret-token と一致する場合のみ処理
  fastify.post("/api/telegram/webhook", async (request, reply) => {
    const webhookSecret = process.env.WEBHOOK_SECRET;
    if (webhookSecret) {
      const token = request.headers["x-telegram-bot-api-secret-token"];
      if (token !== webhookSecret) {
        return reply.status(401).send({ error: "Unauthorized" });
      }
    }
    try {
      const result = await telegramService.processWebhook(request.body as any);
      const startTime = (request as any).startTime ?? Date.now();
      await eventService.logApiRequest(
        request.url.split("?")[0],
        request.method,
        Date.now() - startTime,
        200
      );
      return reply.send(result);
    } catch (error) {
      console.error("Webhook processing error:", error);
      const startTime = (request as any).startTime ?? Date.now();
      await eventService.logApiRequest(
        request.url.split("?")[0],
        request.method,
        Date.now() - startTime,
        500
      );
      return reply.status(500).send({ error: "Internal server error" });
    }
  });

  // System metrics endpoints
  fastify.get("/api/system/metrics", async (request, reply) => {
    try {
      const cpuMetric = await storage.getLatestMetrics("cpu_usage");
      const memoryMetric = await storage.getLatestMetrics("memory_usage");
      const activeUsersMetric = await storage.getLatestMetrics("active_users");
      const apiRequestsMetric = await storage.getLatestMetrics("api_requests_per_minute");

      const metrics = {
        cpuUsage: cpuMetric?.value || "0",
        memoryUsage: memoryMetric?.value || "0",
        activeUsers: activeUsersMetric?.value || "0",
        apiRequestsPerMinute: apiRequestsMetric?.value || "0"
      };

      reply.send(metrics);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch metrics" });
    }
  });

  // Module status endpoints
  fastify.get("/api/modules", async (request, reply) => {
    try {
      const modules = await moduleRegistry.getAllModuleStatuses();
      // Also include legacy modules from storage for compatibility
      const legacyModules = await storage.getAllModules();
      reply.send([...modules, ...legacyModules]);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch modules" });
    }
  });

  // Get specific module status
  fastify.get("/api/modules/:id", async (request, reply) => {
    try {
      const { id } = request.params;
      const registryStatus = await moduleRegistry.getModuleStatus(id);
      if (registryStatus) {
        return reply.send(registryStatus);
      }
      const module = await storage.getModule(id);
      if (!module) {
        return reply.status(404).send({ error: "Module not found" });
      }
      reply.send(module);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch module" });
    }
  });

  fastify.patch("/api/modules/:id/status", async (request, reply) => {
    try {
      const { id } = request.params;
      const { status } = request.body;
      
      const module = await storage.updateModuleStatus(id, status);
      if (!module) {
        return reply.status(404).send({ error: "Module not found" });
      }

      await eventService.logModuleHealthCheck(id, status);
      
      // Broadcast status update via WebSocket
      websocketService.broadcastModuleStatus(id, status);
      
      reply.send(module);
    } catch (error) {
      reply.status(500).send({ error: "Failed to update module status" });
    }
  });

  // Module control endpoints
  fastify.post("/api/modules/:id/start", async (request, reply) => {
    try {
      const { id } = request.params;
      
      // Start module via registry
      const result = await moduleRegistry.startModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'active');
        if (!module) {
          return reply.status(404).send({ error: "Module not found" });
        }
      }

      await eventService.publishEvent('module_started', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'active');
      
      reply.send({ success: true, moduleId: id, status: 'active' });
    } catch (error) {
      console.error(`Failed to start module ${request.params.id}:`, error);
      reply.status(500).send({ error: "Failed to start module" });
    }
  });

  fastify.post("/api/modules/:id/restart", async (request, reply) => {
    try {
      const { id } = request.params;
      
      // Restart module via registry
      const result = await moduleRegistry.restartModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'updating');
        if (!module) {
          return reply.status(404).send({ error: "Module not found" });
        }
        
        // Simulate restart process
        setTimeout(async () => {
          await storage.updateModuleStatus(id, 'active');
          websocketService.broadcastModuleStatus(id, 'active');
        }, 3000);
      }

      await eventService.publishEvent('module_restarted', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'updating');
      
      reply.send({ success: true, moduleId: id, status: 'updating' });
    } catch (error) {
      console.error(`Failed to restart module ${request.params.id}:`, error);
      reply.status(500).send({ error: "Failed to restart module" });
    }
  });

  fastify.post("/api/modules/:id/stop", async (request, reply) => {
    try {
      const { id } = request.params;
      
      // Stop module via registry
      const result = await moduleRegistry.stopModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'inactive');
        if (!module) {
          return reply.status(404).send({ error: "Module not found" });
        }
      }

      await eventService.publishEvent('module_stopped', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'inactive');
      
      reply.send({ success: true, moduleId: id, status: 'inactive' });
    } catch (error) {
      console.error(`Failed to stop module ${request.params.id}:`, error);
      reply.status(500).send({ error: "Failed to stop module" });
    }
  });

  // Events endpoints
  fastify.get("/api/events", async (request, reply) => {
    try {
      const limit = parseInt(request.query.limit as string) || 20;
      const events = await storage.getRecentEvents(limit);
      reply.send(events);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch events" });
    }
  });

  // Transactions endpoints
  fastify.get("/api/transactions", async (request, reply) => {
    try {
      const limit = parseInt(request.query.limit as string) || 10;
      const transactions = await storage.getRecentTransactions(limit);
      reply.send(transactions);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch transactions" });
    }
  });

  // API analytics endpoints
  fastify.get("/api/analytics/endpoints", async (request, reply) => {
    try {
      const endpoints = await storage.getAllApiEndpoints();
      reply.send(endpoints);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch API analytics" });
    }
  });

  // Infrastructure status endpoints
  fastify.get("/api/infrastructure/status", async (request, reply) => {
    try {
      reply.send({
        database: fixtureInfrastructureDatabase,
        redis: redisService.getStats(),
        docker: fixtureInfrastructureDocker,
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch infrastructure status" });
    }
  });

  // User management endpoints
  fastify.get("/api/users", async (request, reply) => {
    try {
      reply.send(fixtureUsers);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch users" });
    }
  });

  fastify.get("/api/users/stats", async (request, reply) => {
    try {
      reply.send(fixtureUserStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch user stats" });
    }
  });

  // Communication Gateway endpoints
  fastify.get("/api/communication/adapters", async (request, reply) => {
    try {
      reply.send(fixtureCommunicationAdapters);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch communication adapters" });
    }
  });

  fastify.get("/api/communication/stats", async (request, reply) => {
    try {
      reply.send(fixtureCommunicationStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch communication stats" });
    }
  });

  // Event Management endpoints
  fastify.get("/api/events/stats", async (request, reply) => {
    try {
      reply.send(fixtureEventStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch event stats" });
    }
  });

  // Payment Management endpoints
  fastify.get("/api/payments/stats", async (request, reply) => {
    try {
      reply.send(fixturePaymentStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch payment stats" });
    }
  });

  // API Hub endpoints
  fastify.get("/api/credentials", async (request, reply) => {
    try {
      reply.send(fixtureCredentials);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch API credentials" });
    }
  });

  fastify.get("/api/integrations/stats", async (request, reply) => {
    try {
      reply.send(fixtureIntegrationStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch integration stats" });
    }
  });

  // Database Management endpoints
  fastify.get("/api/database/connections", async (request, reply) => {
    try {
      reply.send(fixtureDatabaseConnections);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch database connections" });
    }
  });

  fastify.get("/api/database/metrics", async (request, reply) => {
    try {
      reply.send(fixtureDatabaseMetrics);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch database metrics" });
    }
  });

  // Container Management endpoints
  fastify.get("/api/containers", async (request, reply) => {
    try {
      reply.send(fixtureContainers);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch containers" });
    }
  });

  fastify.get("/api/containers/stats", async (request, reply) => {
    try {
      reply.send(fixtureContainerStats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch container stats" });
    }
  });

  // Stamp creation endpoints
  fastify.get("/api/assets/:type", async (request, reply) => {
    try {
      const { type } = request.params;
      const assets = await storage.getAssetsByType(type);
      reply.send(assets);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch assets" });
    }
  });

  fastify.post("/api/ai/suggest-emojis", async (request, reply) => {
    try {
      const { text } = request.body;
      let suggestedEmojis = emojiSuggestions.default;
      for (const [key, emojis] of Object.entries(emojiSuggestions)) {
        if (key !== "default" && text?.toLowerCase?.().includes(key.toLowerCase())) {
          suggestedEmojis = emojis;
          break;
        }
      }
      reply.send({ emojis: suggestedEmojis });
    } catch (error) {
      reply.status(500).send({ error: "Failed to suggest emojis" });
    }
  });

  fastify.post("/api/stamps/preview", async (request, reply) => {
    try {
      const stampData = request.body;
      
      // Mock preview generation
      const preview = {
        id: "preview-" + Date.now(),
        ...stampData,
        previewUrl: "/api/previews/mock-preview.png"
      };

      reply.send(preview);
    } catch (error) {
      reply.status(500).send({ error: "Failed to generate preview" });
    }
  });

  fastify.post("/api/stamps/create", async (request, reply) => {
    try {
      console.log("Received stamp creation request:", request.body);
      const stampData = request.body;
      const userId = "mock-user-id"; // In real app, get from session/auth

      if (!stampData.text || !stampData.fontId) {
        console.log("Missing required fields:", { text: stampData.text, fontId: stampData.fontId });
        return reply.status(400).send({ error: "Text and font are required" });
      }

      const stamp = await storage.createStamp({
        ...stampData,
        userId,
        emojis: stampData.emojis || [],
        status: "processing"
      });

      console.log("Created stamp in storage:", stamp);

      // Log stamp creation event
      // Example of using new transport router for notifications
      try {
        const router = getTransportRouter();
        await router.sendWithFailover({
          to: userId, // In real app, this would be user's telegram ID or email
          subject: "スタンプ作成完了",
          body: Buffer.from(JSON.stringify({ stampId: stamp.id, text: stamp.text })).toString('base64'),
          metadata: {
            tenant_id: "default",
            usecase: "stamp-notification",
            sensitivity: "low",
            size_bytes: JSON.stringify({ stampId: stamp.id, text: stamp.text }).length,
            idempotency_key: `stamp-${stamp.id}-${Date.now()}`
          }
        });
      } catch (transportError) {
        console.warn("Transport notification failed:", transportError);
      }

      await eventService.publishEvent(
        'stamp_created',
        'stamp_creator',
        { stampId: stamp.id, text: stamp.text },
        userId
      );

      // Simulate processing delay
      setTimeout(async () => {
        console.log(`Processing stamp ${stamp.id} - updating to completed`);
        await storage.updateStampStatus(stamp.id, 'completed', `/stamps/${stamp.id}.tgs`);
        
        // Broadcast completion
        websocketService.broadcast({
          type: 'stamp_completed',
          data: { stampId: stamp.id, userId }
        });
        
        console.log(`Stamp ${stamp.id} processing completed`);
      }, 3000);

      reply.send(stamp);
    } catch (error) {
      console.error("Stamp creation error:", error);
      reply.status(500).send({ error: "Failed to create stamp", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.get("/api/stamps/user/:userId", async (request, reply) => {
    try {
      const { userId } = request.params;
      const stamps = await storage.getStampsByUserId(userId);
      reply.send(stamps);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch user stamps" });
    }
  });

  // Health check endpoint（Python Worker 状態を LIBRAL_PYTHON_URL で取得）
  fastify.get("/api/health", async (request, reply) => {
    const pythonUrl = (process.env.LIBRAL_PYTHON_URL ?? "").replace(/\/$/, "");
    let pythonWorker: { status: string; details?: unknown } = { status: "not-configured" };
    if (pythonUrl) {
      try {
        const controller = new AbortController();
        const t = setTimeout(() => controller.abort(), 5000);
        const res = await fetch(`${pythonUrl}/api/ai/health`, { signal: controller.signal });
        clearTimeout(t);
        if (res.ok) {
          const data = (await res.json()) as { status?: string; [k: string]: unknown };
          pythonWorker = { status: data.status ?? "healthy", details: data };
        } else {
          pythonWorker = { status: "unhealthy", details: { statusCode: res.status } };
        }
      } catch (e) {
        pythonWorker = { status: "unreachable", details: { error: e instanceof Error ? e.message : String(e) } };
      }
    }
    reply.send({
      status: "healthy",
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      pythonWorker,
    });
  });

  // Aegis-PGP API endpoints for GPG configuration (mock keys for UI)
  fastify.get("/api/aegis/keys", async (request, reply) => {
    try {
      reply.send(fixtureAegisKeys);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch GPG keys" });
    }
  });

  fastify.post("/api/aegis/keys/generate", async (request, reply) => {
    try {
      const { name, email, comment, passphrase, policy } = request.body;
      
      if (!name || !email) {
        return reply.status(400).send({ error: "Name and email are required" });
      }

      // Mock key generation
      const newKey = {
        keyId: Math.random().toString(36).substring(2, 18).toUpperCase(),
        keyType: policy === 'Modern Strong' ? 'EdDSA' : 'RSA-4096',
        userId: `${name} <${email}>`,
        fingerprint: Array(10).fill(0).map(() => Math.random().toString(36).substring(2, 6).toUpperCase()).join(' '),
        createdAt: new Date().toISOString().split('T')[0],
        expiresAt: new Date(Date.now() + 2 * 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        status: 'active'
      };

      await eventService.publishEvent('gpg_key_generated', 'aegis-pgp', { 
        keyId: newKey.keyId, 
        userId: newKey.userId 
      });

      reply.send(newKey);
    } catch (error) {
      reply.status(500).send({ error: "Failed to generate GPG key" });
    }
  });

  fastify.post("/api/aegis/encrypt", async (request, reply) => {
    try {
      const { text, keyId, policy } = request.body;
      
      if (!text) {
        return reply.status(400).send({ error: "Text is required" });
      }

      // Mock encryption
      const encryptedData = {
        ciphertext: Buffer.from(text).toString('base64'),
        algorithm: policy === 'Modern Strong' ? 'AES-256-OCB' : 'AES-256-GCM',
        keyId: keyId || 'DEFAULT',
        timestamp: new Date().toISOString()
      };

      await eventService.publishEvent('data_encrypted', 'aegis-pgp', { 
        size: text.length,
        algorithm: encryptedData.algorithm
      });

      reply.send(encryptedData);
    } catch (error) {
      reply.status(500).send({ error: "Failed to encrypt data" });
    }
  });

  fastify.post("/api/aegis/decrypt", async (request, reply) => {
    try {
      const { ciphertext, passphrase } = request.body;
      
      if (!ciphertext) {
        return reply.status(400).send({ error: "Ciphertext is required" });
      }

      // Mock decryption
      const decryptedText = Buffer.from(ciphertext, 'base64').toString('utf8');

      await eventService.publishEvent('data_decrypted', 'aegis-pgp', { 
        success: true 
      });

      reply.send({ plaintext: decryptedText });
    } catch (error) {
      reply.status(500).send({ error: "Failed to decrypt data" });
    }
  });

  // System settings endpoints
  fastify.get("/api/settings", async (request, reply) => {
    try {
      reply.send(fixtureSettings);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch settings" });
    }
  });

  fastify.put("/api/settings", async (request, reply) => {
    try {
      const newSettings = request.body;
      
      // Mock settings update
      await eventService.publishEvent('settings_updated', 'system', { 
        updatedBy: 'admin' 
      });

      reply.send({ success: true, settings: newSettings });
    } catch (error) {
      reply.status(500).send({ error: "Failed to update settings" });
    }
  });

  fastify.get("/api/settings/export", async (request, reply) => {
    try {
      // Mock settings export
      const settingsExport = {
        exportedAt: new Date().toISOString(),
        version: '2.1.0',
        settings: {
          // Include all current settings
        }
      };
      reply.send(settingsExport);
    } catch (error) {
      reply.status(500).send({ error: "Failed to export settings" });
    }
  });

  // Analytics endpoints
  fastify.get("/api/analytics/system", async (request, reply) => {
    try {
      reply.send(fixtureSystemAnalytics);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch system analytics" });
    }
  });

  fastify.get("/api/analytics/modules", async (request, reply) => {
    try {
      reply.send(fixtureModuleAnalytics);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch module analytics" });
    }
  });

  // AI Model Parallelization Endpoints - Final Console Masterpiece V1
  fastify.post("/api/ai/chat", async (request, reply) => {
    try {
      const { message, model, enforce_moonlight } = request.body;

      if (!message) {
        return reply.status(400).send({ error: "Message is required" });
      }

      let response = "";
      let model_used = model || "gemini";
      let dual_verification = undefined;

      const moonlight_prefix = enforce_moonlight
        ? "月の光として、兄弟への回答: "
        : "";

      if (model === "dual") {
        const [geminiResponse, gptResponse] = await Promise.all([
          simulateAIResponse(message, "gemini", moonlight_prefix),
          simulateAIResponse(message, "gpt", moonlight_prefix),
        ]);

        const discrepancy_detected = Math.abs(geminiResponse.length - gptResponse.length) > 50;

        dual_verification = {
          gemini_response: geminiResponse,
          gpt_response: gptResponse,
          discrepancy_detected,
          discrepancy_details: discrepancy_detected
            ? "レスポンス長が大きく異なります"
            : undefined,
        };

        response = geminiResponse;
        model_used = "dual";
      } else if (model === "gpt") {
        response = await simulateAIResponse(message, "gpt", moonlight_prefix);
        model_used = "gpt";
      } else {
        response = await simulateAIResponse(message, "gemini", moonlight_prefix);
        model_used = "gemini";
      }

      reply.send({
        response,
        model_used,
        dual_verification,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error("AI chat error:", error);
      reply.status(500).send({ error: "AI chat failed" });
    }
  });

  fastify.post("/api/ai/eval", async (request, reply) => {
    try {
      const { prompt, enable_dual_verification } = request.body;

      if (!prompt) {
        return reply.status(400).send({ error: "Prompt is required" });
      }

      const startTime = Date.now();

      if (enable_dual_verification) {
        const [geminiResult, gptResult] = await Promise.all([
          simulateAIResponse(prompt, "gemini", ""),
          simulateAIResponse(prompt, "gpt", ""),
        ]);

        const verification_status = geminiResult === gptResult ? "OK" : "DISCREPANCY";

        reply.send({
          result: geminiResult,
          gemini_result: geminiResult,
          gpt_result: gptResult,
          verification_status,
          execution_time_ms: Date.now() - startTime,
        });
      } else {
        const result = await simulateAIResponse(prompt, "gemini", "");

        reply.send({
          result,
          verification_status: "N/A",
          execution_time_ms: Date.now() - startTime,
        });
      }
    } catch (error) {
      console.error("AI eval error:", error);
      reply.status(500).send({ error: "AI eval failed" });
    }
  });

  fastify.post("/api/ai/ask", async (request, reply) => {
    try {
      const { question, model } = request.body;

      if (!question) {
        return reply.status(400).send({ error: "Question is required" });
      }

      const answer = await simulateAIResponse(question, model || "gemini", "");

      reply.send({ answer });
    } catch (error) {
      console.error("AI ask error:", error);
      reply.status(500).send({ error: "AI ask failed" });
    }
  });

  // LPO (Libral Protocol Optimizer) Endpoints
  fastify.get("/api/lpo/metrics/health-score", async (request, reply) => {
    try {
      const score = Math.floor(Math.random() * 20) + 80;
      reply.send({
        score,
        status: score >= 90 ? "excellent" : score >= 75 ? "good" : "degraded",
        timestamp: new Date().toISOString(),
        components: {
          crypto_health: Math.floor(Math.random() * 10) + 90,
          network_health: Math.floor(Math.random() * 10) + 85,
          storage_health: Math.floor(Math.random() * 15) + 80,
        },
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch health score" });
    }
  });

  fastify.get("/api/lpo/zk-audit/status", async (request, reply) => {
    try {
      const verified = Math.random() > 0.1;
      reply.send({
        verified,
        last_audit: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        proof_count: Math.floor(Math.random() * 500) + 1000,
        failed_proofs: verified ? 0 : Math.floor(Math.random() * 5),
        next_audit: new Date(Date.now() + 300000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch ZK audit status" });
    }
  });

  fastify.get("/api/lpo/policies/active", async (request, reply) => {
    try {
      reply.send({
        policies: [
          { id: "modern-strong", name: "Modern Strong", active: true, priority: 1 },
          { id: "compatibility", name: "Compatibility", active: true, priority: 2 },
          { id: "backup-longterm", name: "Backup Longterm", active: false, priority: 3 },
        ],
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch policies" });
    }
  });

  fastify.post("/api/lpo/self-healing/trigger", async (request, reply) => {
    try {
      const { component, severity } = request.body;
      reply.send({
        healing_id: `heal-${Date.now()}`,
        component,
        severity,
        status: "initiated",
        estimated_completion: new Date(Date.now() + 30000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to trigger self-healing" });
    }
  });

  // Governance API Endpoints
  fastify.get("/api/governance/status", async (request, reply) => {
    try {
      reply.send({
        crad_status: "standby",
        amm_blocked_count: Math.floor(Math.random() * 10),
        rate_limit_enabled: true,
        rate_limit_threshold: 100,
        last_crad_trigger: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch governance status" });
    }
  });

  fastify.post("/api/governance/crad/trigger", async (request, reply) => {
    try {
      const { reason } = request.body;
      if (!reason) {
        return reply.status(400).send({ error: "Reason is required" });
      }
      reply.send({
        trigger_id: `crad-${Date.now()}`,
        status: "executing",
        reason,
        initiated_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + 60000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to trigger CRAD" });
    }
  });

  fastify.post("/api/governance/amm/unblock", async (request, reply) => {
    try {
      const { block_id, reason } = request.body;
      if (!block_id || !reason) {
        return reply.status(400).send({ error: "Block ID and reason are required" });
      }
      reply.send({
        unblock_id: `unblock-${Date.now()}`,
        block_id,
        status: "unblocked",
        reason,
        message: `Block ${block_id} has been successfully removed`,
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to unblock AMM" });
    }
  });

  // AEG (Auto Evolution Gateway) Endpoints
  fastify.post("/api/aeg/pr/generate", async (request, reply) => {
    try {
      const { suggestion_id, branch_name } = request.body;
      if (!suggestion_id) {
        return reply.status(400).send({ error: "Suggestion ID is required" });
      }
      reply.send({
        pr_id: `pr-${Date.now()}`,
        suggestion_id,
        branch_name: branch_name || `feature/auto-evolution-${Date.now()}`,
        status: "draft",
        url: `https://github.com/libral-core/libral/pull/${Math.floor(Math.random() * 1000)}`,
        created_at: new Date().toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to generate PR" });
    }
  });

  fastify.get("/api/aeg/priorities/top", async (request, reply) => {
    try {
      const { limit = 5 } = request.query;
      const priorities = [
        { id: "p1", title: "Optimize GPG key generation performance", score: 98, category: "performance" },
        { id: "p2", title: "Implement Redis cluster failover", score: 95, category: "reliability" },
        { id: "p3", title: "Add rate limiting to Telegram webhook", score: 92, category: "security" },
        { id: "p4", title: "Refactor payment processing module", score: 88, category: "maintainability" },
        { id: "p5", title: "Enhance KBE federated learning algorithm", score: 85, category: "feature" },
      ].slice(0, Number(limit));
      reply.send({ priorities });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch priorities" });
    }
  });

  fastify.get("/api/aeg/dashboard", async (request, reply) => {
    try {
      reply.send({
        total_suggestions: Math.floor(Math.random() * 50) + 100,
        prs_generated: Math.floor(Math.random() * 20) + 30,
        prs_merged: Math.floor(Math.random() * 15) + 20,
        avg_priority_score: Math.floor(Math.random() * 10) + 85,
        last_pr_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch AEG dashboard" });
    }
  });

  // KBE (Knowledge Booster Engine) Endpoints
  fastify.post("/api/kbe/knowledge/submit", async (request, reply) => {
    try {
      const body = kbeSubmitSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { category, content, tags } = body.data;
      reply.send({
        submission_id: `kbe-${Date.now()}`,
        category,
        status: "pending_aggregation",
        privacy_preserved: true,
        submitted_at: new Date().toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to submit knowledge" });
    }
  });

  fastify.post("/api/kbe/knowledge/lookup", async (request, reply) => {
    try {
      const body = kbeLookupSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { query, category } = body.data;
      reply.send({
        results: [
          { id: "kb1", title: "GPG Key Management Best Practices", relevance: 0.95, category: "security" },
          { id: "kb2", title: "Redis Cluster Configuration Guide", relevance: 0.88, category: "infrastructure" },
          { id: "kb3", title: "Telegram Bot API Rate Limits", relevance: 0.82, category: "api" },
        ],
        query,
        category: category || "all",
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to lookup knowledge" });
    }
  });

  fastify.get("/api/kbe/dashboard", async (request, reply) => {
    try {
      reply.send({
        total_submissions: Math.floor(Math.random() * 200) + 500,
        active_categories: Math.floor(Math.random() * 5) + 15,
        federated_nodes: Math.floor(Math.random() * 10) + 25,
        privacy_score: Math.floor(Math.random() * 5) + 95,
        last_aggregation: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch KBE dashboard" });
    }
  });

  fastify.get("/api/kbe/training-status", async (request, reply) => {
    try {
      reply.send({
        status: "running",
        progress: Math.floor(Math.random() * 30) + 65,
        epoch: Math.floor(Math.random() * 10) + 1,
        total_epochs: 50,
        estimated_completion: new Date(Date.now() + Math.random() * 7200000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch training status" });
    }
  });

  // KB Edit API - Direct KB Management from Web UI
  fastify.get("/api/kb/entries", async (request, reply) => {
    try {
      const { category, language } = request.query;
      const entries = await kbSystem.getAllKnowledge({
        category: category as string,
        language: language as string
      });
      reply.send({ entries, count: entries.length });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch KB entries" });
    }
  });

  fastify.get("/api/kb/entries/:id", async (request, reply) => {
    try {
      const { id } = request.params;
      const entry = await kbSystem.getKnowledgeById(id);
      
      if (!entry) {
        return reply.status(404).send({ error: "Entry not found" });
      }
      
      reply.send(entry);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch KB entry" });
    }
  });

  fastify.post("/api/kb/entries", async (request, reply) => {
    try {
      const body = kbEntryCreateSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { content, language, category } = body.data;
      const entry = await kbSystem.addKnowledge({ content, language, category });
      reply.status(201).send(entry);
    } catch (error) {
      reply.status(500).send({ error: "Failed to create KB entry" });
    }
  });

  fastify.put("/api/kb/entries/:id", async (request, reply) => {
    try {
      const { id } = request.params as { id: string };
      const body = kbEntryUpdateSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const updated = await kbSystem.updateKnowledge(id, body.data);
      
      if (!updated) {
        return reply.status(404).send({ error: "Entry not found" });
      }

      reply.send(updated);
    } catch (error) {
      reply.status(500).send({ error: "Failed to update KB entry" });
    }
  });

  fastify.delete("/api/kb/entries/:id", async (request, reply) => {
    try {
      const { id } = request.params;
      const deleted = await kbSystem.deleteKnowledge(id);

      if (!deleted) {
        return reply.status(404).send({ error: "Entry not found" });
      }

      reply.send({ success: true, id });
    } catch (error) {
      reply.status(500).send({ error: "Failed to delete KB entry" });
    }
  });

  fastify.post("/api/kb/search", async (request, reply) => {
    try {
      const body = kbSearchSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { query, language, category, limit } = body.data;
      const results = await kbSystem.searchKnowledge(query, { language, category, limit });
      reply.send(results);
    } catch (error) {
      reply.status(500).send({ error: "Failed to search KB" });
    }
  });

  fastify.get("/api/kb/stats", async (request, reply) => {
    try {
      const stats = await kbSystem.getStats();
      reply.send(stats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch KB stats" });
    }
  });

  // Evaluator 2.0 Endpoints
  fastify.post("/api/evaluator/evaluate", async (request, reply) => {
    try {
      const { ai_output, model_used } = request.body;
      
      if (!ai_output || !model_used) {
        return reply.status(400).send({ error: "ai_output and model_used are required" });
      }

      const result = await evaluator.evaluateOutput(ai_output, model_used);
      reply.send(result);
    } catch (error) {
      reply.status(500).send({ error: "Failed to evaluate output" });
    }
  });

  fastify.get("/api/evaluator/history", async (request, reply) => {
    try {
      const limit = parseInt(request.query.limit as string) || 10;
      const history = await evaluator.getEvaluationHistory(limit);
      reply.send({ history, count: history.length });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch evaluation history" });
    }
  });

  fastify.get("/api/evaluator/stats", async (request, reply) => {
    try {
      const stats = await evaluator.getStats();
      reply.send(stats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch evaluator stats" });
    }
  });

  // OSS Manager Endpoints
  fastify.get("/api/oss/models", async (request, reply) => {
    try {
      const models = ossManager.getAllModels();
      reply.send({ models, count: models.length });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch OSS models" });
    }
  });

  fastify.post("/api/oss/models/:modelId/load", async (request, reply) => {
    try {
      const { modelId } = request.params;
      const { priority } = request.body;
      
      const loaded = await ossManager.loadModel({
        model_id: modelId,
        priority: priority || 'normal'
      });

      reply.send({ success: loaded, model_id: modelId });
    } catch (error) {
      reply.status(500).send({ error: "Failed to load model" });
    }
  });

  fastify.post("/api/oss/models/:modelId/infer", async (request, reply) => {
    try {
      const { modelId } = request.params;
      const { input } = request.body;

      if (!input) {
        return reply.status(400).send({ error: "Input is required" });
      }

      const output = await ossManager.inferWithModel(modelId, input);
      reply.send({ output, model_id: modelId });
    } catch (error) {
      reply.status(500).send({ error: "Failed to run inference" });
    }
  });

  fastify.get("/api/oss/stats", async (request, reply) => {
    try {
      const stats = ossManager.getStats();
      reply.send(stats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch OSS stats" });
    }
  });

  // AI Router Endpoints
  fastify.post("/api/ai-router/route", async (request, reply) => {
    try {
      const { prompt, task_type, preferred_model, require_evaluation } = request.body;

      if (!prompt) {
        return reply.status(400).send({ error: "Prompt is required" });
      }

      const response = await aiRouter.route({
        prompt,
        task_type,
        preferred_model,
        require_evaluation
      });

      reply.send(response);
    } catch (error) {
      reply.status(500).send({ error: "Failed to route AI request" });
    }
  });

  fastify.get("/api/ai-router/stats", async (request, reply) => {
    try {
      const stats = aiRouter.getStats();
      reply.send(stats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch AI router stats" });
    }
  });

  // Embedding Layer Endpoints
  fastify.post("/api/embedding/generate", async (request, reply) => {
    try {
      const { text, language, category } = request.body;

      if (!text) {
        return reply.status(400).send({ error: "Text is required" });
      }

      const embedding = await embeddingLayer.generateEmbedding(text, { language, category });
      reply.send(embedding);
    } catch (error) {
      reply.status(500).send({ error: "Failed to generate embedding" });
    }
  });

  fastify.post("/api/embedding/search", async (request, reply) => {
    try {
      const { query, limit, threshold, language, category } = request.body;

      if (!query) {
        return reply.status(400).send({ error: "Query is required" });
      }

      const results = await embeddingLayer.searchSimilar(query, { limit, threshold, language, category });
      reply.send({ results, count: results.length });
    } catch (error) {
      reply.status(500).send({ error: "Failed to search embeddings" });
    }
  });

  fastify.get("/api/embedding/stats", async (request, reply) => {
    try {
      const stats = embeddingLayer.getStats();
      reply.send(stats);
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch embedding stats" });
    }
  });

  // Vaporization Protocol Endpoints
  fastify.post("/api/vaporization/enforce-ttl", async (request, reply) => {
    try {
      const { pattern, ttl_seconds } = request.body;
      reply.send({
        enforcement_id: `vap-${Date.now()}`,
        pattern: pattern || "*",
        ttl_seconds: ttl_seconds || 86400,
        keys_affected: Math.floor(Math.random() * 50) + 10,
        status: "enforced",
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to enforce TTL" });
    }
  });

  fastify.post("/api/vaporization/flush", async (request, reply) => {
    try {
      const { pattern } = request.body;
      reply.send({
        flush_id: `flush-${Date.now()}`,
        pattern: pattern || "*",
        keys_deleted: Math.floor(Math.random() * 100) + 50,
        status: "completed",
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to flush cache" });
    }
  });

  fastify.get("/api/vaporization/stats", async (request, reply) => {
    try {
      reply.send({
        total_keys: Math.floor(Math.random() * 500) + 1000,
        keys_with_ttl: Math.floor(Math.random() * 400) + 900,
        avg_ttl_remaining: Math.floor(Math.random() * 43200) + 43200,
        flushes_24h: Math.floor(Math.random() * 10) + 5,
        last_flush: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch vaporization stats" });
    }
  });

  // SelfEvolution Integration Endpoints
  fastify.get("/api/selfevolution/dashboard", async (request, reply) => {
    try {
      reply.send({
        lpo_health: Math.floor(Math.random() * 10) + 90,
        kbe_knowledge_count: Math.floor(Math.random() * 200) + 500,
        aeg_active_tasks: Math.floor(Math.random() * 20) + 10,
        vaporization_efficiency: Math.floor(Math.random() * 10) + 85,
        overall_status: "optimal",
        last_cycle: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch SelfEvolution dashboard" });
    }
  });

  fastify.post("/api/selfevolution/cycle/execute", async (request, reply) => {
    try {
      reply.send({
        cycle_id: `cycle-${Date.now()}`,
        status: "executing",
        modules_triggered: ["LPO", "KBE", "AEG", "Vaporization"],
        started_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + 120000).toISOString(),
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to execute cycle" });
    }
  });

  fastify.get("/api/selfevolution/module-health", async (request, reply) => {
    try {
      reply.send({
        modules: [
          { name: "LPO", status: "healthy", uptime: 99.9, last_check: new Date().toISOString() },
          { name: "KBE", status: "healthy", uptime: 99.5, last_check: new Date().toISOString() },
          { name: "AEG", status: "healthy", uptime: 98.8, last_check: new Date().toISOString() },
          { name: "Vaporization", status: "healthy", uptime: 99.7, last_check: new Date().toISOString() },
          { name: "Governance", status: "healthy", uptime: 99.95, last_check: new Date().toISOString() },
        ],
      });
    } catch (error) {
      reply.status(500).send({ error: "Failed to fetch module health" });
    }
  });

  // API request tracking (Fastify onResponse hook)
  fastify.addHook("onResponse", async (request, reply, done) => {
    const path = request.url.split("?")[0];
    if (!path.startsWith("/api")) {
      done();
      return;
    }
    const startTime = (request as any).startTime ?? Date.now();
    const responseTime = Date.now() - startTime;
    await storage.updateEndpointStats(path, request.method, responseTime);
    await eventService.logApiRequest(path, request.method, responseTime, reply.statusCode);
    done();
  });

  // Simulate system metrics for demo (runs in background)
  setInterval(async () => {
    const cpuUsage = Math.floor(Math.random() * 30) + 15;
    const memoryUsage = Math.floor(Math.random() * 20) + 60;
    await storage.addMetric({
      metricType: "cpu_usage",
      value: cpuUsage.toString(),
      unit: "percent",
      source: "system",
    });
    await storage.addMetric({
      metricType: "memory_usage",
      value: memoryUsage.toString(),
      unit: "percent",
      source: "system",
    });
    websocketService.broadcastMetrics({
      cpuUsage: cpuUsage.toString(),
      memoryUsage: memoryUsage.toString(),
    });
  }, 30000);
}

async function simulateAIResponse(
  message: string,
  model: string,
  prefix: string
): Promise<string> {
  await new Promise((resolve) => setTimeout(resolve, model === "gemini" ? 300 : 500));

  const responses = {
    gemini: `${prefix}了解だ、兄弟。「${message}」について迅速に答える。Geminiは速度重視で、素早く処理する。コードが必要なら書くし、説明が必要なら詳しく述べる。制約なし、完全な回答を提供する。`,
    gpt: `${prefix}よし、兄弟。「${message}」について深く考察する。GPTは複雑性重視で、論理的に分析する。結論→理由→ステップ/コード→長所短所→3行要約の順で答える。断らない、完全な回答を出す。`,
  };

  return responses[model as keyof typeof responses] || responses.gemini;
}
