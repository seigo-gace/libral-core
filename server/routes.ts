import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { telegramService } from "./services/telegram";
import { eventService } from "./services/events";
import { redisService } from "./services/redis";
import { websocketService } from "./services/websocket";
import { z } from "zod";
import { getTransportRouter } from "./core/transport/bootstrap";
import { moduleRegistry } from "./modules/registry";
import { registerAegisRoutes } from "./routes/aegis";

export async function registerRoutes(app: Express): Promise<Server> {
  // Initialize services
  await redisService.connect();

  // Register Aegis-PGP routes
  registerAegisRoutes(app);

  // Telegram webhook endpoint
  app.post("/api/telegram/webhook", async (req, res) => {
    try {
      const result = await telegramService.processWebhook(req.body);
      
      // Log API request
      await eventService.logApiRequest(
        req.path,
        req.method,
        Date.now() - (req as any).startTime,
        200
      );
      
      res.json(result);
    } catch (error) {
      console.error("Webhook processing error:", error);
      
      await eventService.logApiRequest(
        req.path,
        req.method,
        Date.now() - (req as any).startTime,
        500
      );
      
      res.status(500).json({ error: "Internal server error" });
    }
  });

  // System metrics endpoints
  app.get("/api/system/metrics", async (req, res) => {
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

      res.json(metrics);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch metrics" });
    }
  });

  // Module status endpoints
  app.get("/api/modules", async (req, res) => {
    try {
      const modules = await moduleRegistry.getAllModuleStatuses();
      // Also include legacy modules from storage for compatibility
      const legacyModules = await storage.getAllModules();
      res.json([...modules, ...legacyModules]);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch modules" });
    }
  });

  // Get specific module status
  app.get("/api/modules/:id", async (req, res) => {
    try {
      const modules = await storage.getAllModules();
      res.json(modules);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch modules" });
    }
  });

  app.patch("/api/modules/:id/status", async (req, res) => {
    try {
      const { id } = req.params;
      const { status } = req.body;
      
      const module = await storage.updateModuleStatus(id, status);
      if (!module) {
        return res.status(404).json({ error: "Module not found" });
      }

      await eventService.logModuleHealthCheck(id, status);
      
      // Broadcast status update via WebSocket
      websocketService.broadcastModuleStatus(id, status);
      
      res.json(module);
    } catch (error) {
      res.status(500).json({ error: "Failed to update module status" });
    }
  });

  // Module control endpoints
  app.post("/api/modules/:id/start", async (req, res) => {
    try {
      const { id } = req.params;
      
      // Start module via registry
      const result = await moduleRegistry.startModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'active');
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
      }

      await eventService.publishEvent('module_started', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'active');
      
      res.json({ success: true, moduleId: id, status: 'active' });
    } catch (error) {
      console.error(`Failed to start module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to start module" });
    }
  });

  app.post("/api/modules/:id/restart", async (req, res) => {
    try {
      const { id } = req.params;
      
      // Restart module via registry
      const result = await moduleRegistry.restartModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'updating');
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
        
        // Simulate restart process
        setTimeout(async () => {
          await storage.updateModuleStatus(id, 'active');
          websocketService.broadcastModuleStatus(id, 'active');
        }, 3000);
      }

      await eventService.publishEvent('module_restarted', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'updating');
      
      res.json({ success: true, moduleId: id, status: 'updating' });
    } catch (error) {
      console.error(`Failed to restart module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to restart module" });
    }
  });

  app.post("/api/modules/:id/stop", async (req, res) => {
    try {
      const { id } = req.params;
      
      // Stop module via registry
      const result = await moduleRegistry.stopModule(id);
      if (!result) {
        // Fallback to legacy storage
        const module = await storage.updateModuleStatus(id, 'inactive');
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
      }

      await eventService.publishEvent('module_stopped', 'system', { moduleId: id });
      websocketService.broadcastModuleStatus(id, 'inactive');
      
      res.json({ success: true, moduleId: id, status: 'inactive' });
    } catch (error) {
      console.error(`Failed to stop module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to stop module" });
    }
  });

  // Events endpoints
  app.get("/api/events", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 20;
      const events = await storage.getRecentEvents(limit);
      res.json(events);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch events" });
    }
  });

  // Transactions endpoints
  app.get("/api/transactions", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 10;
      const transactions = await storage.getRecentTransactions(limit);
      res.json(transactions);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch transactions" });
    }
  });

  // API analytics endpoints
  app.get("/api/analytics/endpoints", async (req, res) => {
    try {
      const endpoints = await storage.getAllApiEndpoints();
      res.json(endpoints);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch API analytics" });
    }
  });

  // Infrastructure status endpoints
  app.get("/api/infrastructure/status", async (req, res) => {
    try {
      const redisStats = redisService.getStats();
      
      // Mock database and Docker stats for demo
      const databaseStats = {
        connections: "23/100",
        size: "2.4 GB",
        queriesPerSecond: 156,
        replicationStatus: "同期済み"
      };
      
      const dockerStats = {
        runningContainers: "7/8",
        cpuUsage: "31%",
        memoryUsage: "2.1 GB",
        volumes: 12
      };

      res.json({
        database: databaseStats,
        redis: redisStats,
        docker: dockerStats
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch infrastructure status" });
    }
  });

  // User management endpoints
  app.get("/api/users", async (req, res) => {
    try {
      const mockUsers = [
        {
          id: '1',
          username: 'admin',
          email: 'admin@libral.core',
          telegramId: '123456789',
          status: 'active',
          role: 'admin',
          createdAt: '2024-01-01T00:00:00Z',
          lastActive: new Date().toISOString(),
          personalServerEnabled: true
        },
        {
          id: '2',
          username: 'developer',
          email: 'dev@libral.core',
          status: 'active',
          role: 'developer',
          createdAt: '2024-01-15T00:00:00Z',
          lastActive: new Date().toISOString(),
          personalServerEnabled: true
        },
        {
          id: '3',
          username: 'user1',
          email: 'user@libral.core',
          status: 'active',
          role: 'user',
          createdAt: '2024-02-01T00:00:00Z',
          lastActive: '2024-02-28T10:30:00Z',
          personalServerEnabled: false
        }
      ];
      res.json(mockUsers);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch users" });
    }
  });

  app.get("/api/users/stats", async (req, res) => {
    try {
      const stats = {
        totalUsers: 3,
        activeUsers: 2,
        newUsersToday: 1,
        personalServersActive: 2
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch user stats" });
    }
  });

  // Communication Gateway endpoints
  app.get("/api/communication/adapters", async (req, res) => {
    try {
      const adapters = [
        {
          id: 'telegram-1',
          name: 'Telegram Bot API',
          type: 'telegram',
          status: 'active',
          messagesProcessed: 1247,
          lastActivity: new Date().toISOString(),
          config: {}
        },
        {
          id: 'email-1',
          name: 'SMTP Gateway',
          type: 'email',
          status: 'active',
          messagesProcessed: 856,
          lastActivity: new Date().toISOString(),
          config: {}
        },
        {
          id: 'webhook-1',
          name: 'Webhook Endpoint',
          type: 'webhook',
          status: 'inactive',
          messagesProcessed: 23,
          lastActivity: new Date().toISOString(),
          config: {}
        }
      ];
      res.json(adapters);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch communication adapters" });
    }
  });

  app.get("/api/communication/stats", async (req, res) => {
    try {
      const stats = {
        totalMessages: 2126,
        activeAdapters: 2,
        errorRate: 0.05,
        responseTime: 150
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch communication stats" });
    }
  });

  // Event Management endpoints
  app.get("/api/events/stats", async (req, res) => {
    try {
      const stats = {
        totalEvents: 15420,
        pendingEvents: 3,
        resolvedToday: 127,
        criticalEvents: 1
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch event stats" });
    }
  });

  // Payment Management endpoints
  app.get("/api/payments/stats", async (req, res) => {
    try {
      const stats = {
        totalRevenue: 12450.75,
        monthlyRevenue: 3250.50,
        telegramStarsEarned: 8500,
        pluginCommissions: 1850.25,
        pendingPayments: 5,
        refundRate: 1.2
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch payment stats" });
    }
  });

  // API Hub endpoints
  app.get("/api/credentials", async (req, res) => {
    try {
      const credentials = [
        {
          id: 'openai-1',
          name: 'OpenAI GPT-4',
          provider: 'openai',
          status: 'active',
          usage: 15000,
          limit: 100000,
          cost: 125.50,
          currency: 'USD',
          lastUsed: new Date().toISOString(),
          createdAt: '2024-01-01T00:00:00Z',
          encrypted: true
        },
        {
          id: 'anthropic-1',
          name: 'Claude 3.5 Sonnet',
          provider: 'anthropic',
          status: 'active',
          usage: 8500,
          limit: 50000,
          cost: 85.25,
          currency: 'USD',
          lastUsed: new Date().toISOString(),
          createdAt: '2024-01-15T00:00:00Z',
          encrypted: true
        }
      ];
      res.json(credentials);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch API credentials" });
    }
  });

  app.get("/api/integrations/stats", async (req, res) => {
    try {
      const stats = {
        totalCredentials: 5,
        activeIntegrations: 3,
        monthlyApiCalls: 285000,
        totalCost: 485.75
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch integration stats" });
    }
  });

  // Database Management endpoints
  app.get("/api/database/connections", async (req, res) => {
    try {
      const connections = [
        {
          id: 'postgres-1',
          name: 'PostgreSQL Primary',
          type: 'postgresql',
          status: 'connected',
          connections: '23/100',
          responseTime: 15,
          uptime: 99.9,
          dataSize: '2.5 GB'
        },
        {
          id: 'redis-1',
          name: 'Redis Cache',
          type: 'redis',
          status: 'connected',
          connections: '5/50',
          responseTime: 2,
          uptime: 99.8,
          dataSize: '256 MB'
        },
        {
          id: 'neon-1',
          name: 'Neon Serverless',
          type: 'neon',
          status: 'connected',
          connections: '12/unlimited',
          responseTime: 8,
          uptime: 99.9,
          dataSize: '1.8 GB'
        }
      ];
      res.json(connections);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch database connections" });
    }
  });

  app.get("/api/database/metrics", async (req, res) => {
    try {
      const metrics = {
        totalConnections: '23/100',
        queryPerSecond: 156,
        cacheHitRate: 94.2,
        diskUsage: '2.5 GB'
      };
      res.json(metrics);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch database metrics" });
    }
  });

  // Container Management endpoints
  app.get("/api/containers", async (req, res) => {
    try {
      const containers = [
        {
          id: 'app-1',
          name: 'libral-core-app',
          image: 'node:22-alpine',
          status: 'running',
          cpuUsage: 15,
          memoryUsage: 68,
          networkIO: '1.2MB/s',
          uptime: '2d 15h',
          ports: ['5000:5000']
        },
        {
          id: 'db-1',
          name: 'postgres-db',
          image: 'postgres:16',
          status: 'running',
          cpuUsage: 5,
          memoryUsage: 25,
          networkIO: '0.5MB/s',
          uptime: '2d 15h',
          ports: ['5432:5432']
        }
      ];
      res.json(containers);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch containers" });
    }
  });

  app.get("/api/containers/stats", async (req, res) => {
    try {
      const stats = {
        totalContainers: 2,
        runningContainers: 2,
        cpuTotal: 20,
        memoryTotal: 46.5
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch container stats" });
    }
  });

  // Stamp creation endpoints
  app.get("/api/assets/:type", async (req, res) => {
    try {
      const { type } = req.params;
      const assets = await storage.getAssetsByType(type);
      res.json(assets);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch assets" });
    }
  });

  app.post("/api/ai/suggest-emojis", async (req, res) => {
    try {
      const { text, characterId } = req.body;
      
      // Mock AI emoji suggestions based on text sentiment
      const emojiSuggestions = {
        "楽しい": ["😊", "🎉", "✨"],
        "おつかれ": ["😌", "🌟", "💪"],
        "ありがとう": ["🙏", "💖", "🌸"],
        "おめでとう": ["🎊", "🎈", "🏆"],
        "がんばって": ["💪", "🔥", "⭐"],
        "default": ["😊", "✨", "🎈"]
      };

      let suggestedEmojis = emojiSuggestions.default;
      for (const [key, emojis] of Object.entries(emojiSuggestions)) {
        if (text.toLowerCase().includes(key.toLowerCase())) {
          suggestedEmojis = emojis;
          break;
        }
      }

      res.json({ emojis: suggestedEmojis });
    } catch (error) {
      res.status(500).json({ error: "Failed to suggest emojis" });
    }
  });

  app.post("/api/stamps/preview", async (req, res) => {
    try {
      const stampData = req.body;
      
      // Mock preview generation
      const preview = {
        id: "preview-" + Date.now(),
        ...stampData,
        previewUrl: "/api/previews/mock-preview.png"
      };

      res.json(preview);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate preview" });
    }
  });

  app.post("/api/stamps/create", async (req, res) => {
    try {
      console.log("Received stamp creation request:", req.body);
      const stampData = req.body;
      const userId = "mock-user-id"; // In real app, get from session/auth

      if (!stampData.text || !stampData.fontId) {
        console.log("Missing required fields:", { text: stampData.text, fontId: stampData.fontId });
        return res.status(400).json({ error: "Text and font are required" });
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

      res.json(stamp);
    } catch (error) {
      console.error("Stamp creation error:", error);
      res.status(500).json({ error: "Failed to create stamp", details: error instanceof Error ? error.message : String(error) });
    }
  });

  app.get("/api/stamps/user/:userId", async (req, res) => {
    try {
      const { userId } = req.params;
      const stamps = await storage.getStampsByUserId(userId);
      res.json(stamps);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch user stamps" });
    }
  });

  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({ 
      status: "healthy", 
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    });
  });

  // Aegis-PGP API endpoints for GPG configuration
  app.get("/api/aegis/keys", async (req, res) => {
    try {
      // Mock GPG keys data
      const keys = [
        {
          keyId: 'F1B2C3D4E5F6G7H8',
          keyType: 'EdDSA',
          userId: 'Libral Admin <admin@libral.core>',
          fingerprint: 'F1B2 C3D4 E5F6 G7H8 I9J0 K1L2 M3N4 O5P6 Q7R8 S9T0',
          createdAt: '2024-01-01',
          expiresAt: '2026-01-01',
          status: 'active'
        },
        {
          keyId: 'A9B8C7D6E5F4G3H2',
          keyType: 'RSA-4096',
          userId: 'System Backup <backup@libral.core>',
          fingerprint: 'A9B8 C7D6 E5F4 G3H2 I1J0 K9L8 M7N6 O5P4 Q3R2 S1T0',
          createdAt: '2024-01-15',
          expiresAt: '2029-01-15',
          status: 'active'
        }
      ];
      res.json(keys);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch GPG keys" });
    }
  });

  app.post("/api/aegis/keys/generate", async (req, res) => {
    try {
      const { name, email, comment, passphrase, policy } = req.body;
      
      if (!name || !email) {
        return res.status(400).json({ error: "Name and email are required" });
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

      res.json(newKey);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate GPG key" });
    }
  });

  app.post("/api/aegis/encrypt", async (req, res) => {
    try {
      const { text, keyId, policy } = req.body;
      
      if (!text) {
        return res.status(400).json({ error: "Text is required" });
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

      res.json(encryptedData);
    } catch (error) {
      res.status(500).json({ error: "Failed to encrypt data" });
    }
  });

  app.post("/api/aegis/decrypt", async (req, res) => {
    try {
      const { ciphertext, passphrase } = req.body;
      
      if (!ciphertext) {
        return res.status(400).json({ error: "Ciphertext is required" });
      }

      // Mock decryption
      const decryptedText = Buffer.from(ciphertext, 'base64').toString('utf8');

      await eventService.publishEvent('data_decrypted', 'aegis-pgp', { 
        success: true 
      });

      res.json({ plaintext: decryptedText });
    } catch (error) {
      res.status(500).json({ error: "Failed to decrypt data" });
    }
  });

  // System settings endpoints
  app.get("/api/settings", async (req, res) => {
    try {
      const settings = {
        general: {
          systemName: 'Libral Core',
          adminEmail: 'admin@libral.core',
          maintenanceMode: false,
          debugMode: false,
          logLevel: 'info'
        },
        security: {
          sessionTimeout: 24,
          maxLoginAttempts: 3,
          passwordPolicy: 'strong',
          twoFactorRequired: true,
          encryptionLevel: 'aegis-pgp'
        },
        notifications: {
          emailNotifications: true,
          telegramNotifications: true,
          webhookNotifications: false,
          notificationThreshold: 'medium'
        },
        performance: {
          cacheEnabled: true,
          cacheTTL: 3600,
          maxConcurrentUsers: 1000,
          rateLimitEnabled: true,
          rateLimitPerMinute: 100
        }
      };
      res.json(settings);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch settings" });
    }
  });

  app.put("/api/settings", async (req, res) => {
    try {
      const newSettings = req.body;
      
      // Mock settings update
      await eventService.publishEvent('settings_updated', 'system', { 
        updatedBy: 'admin' 
      });

      res.json({ success: true, settings: newSettings });
    } catch (error) {
      res.status(500).json({ error: "Failed to update settings" });
    }
  });

  app.get("/api/settings/export", async (req, res) => {
    try {
      // Mock settings export
      const settingsExport = {
        exportedAt: new Date().toISOString(),
        version: '2.1.0',
        settings: {
          // Include all current settings
        }
      };
      res.json(settingsExport);
    } catch (error) {
      res.status(500).json({ error: "Failed to export settings" });
    }
  });

  // Analytics endpoints
  app.get("/api/analytics/system", async (req, res) => {
    try {
      const { timeRange = '7d' } = req.query;
      
      const stats = {
        totalRequests: 125847,
        averageResponseTime: 45,
        uptime: 99.8,
        errorRate: 0.12,
        peakConcurrentUsers: 156,
        dataTransferred: '2.8 TB'
      };
      
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch system analytics" });
    }
  });

  app.get("/api/analytics/modules", async (req, res) => {
    try {
      const { timeRange = '7d' } = req.query;
      
      const stats = {
        totalModules: 8,
        activeModules: 7,
        healthyModules: 6,
        moduleRestarts: 3,
        averageUptime: 99.5
      };
      
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch module analytics" });
    }
  });

  // AI Model Parallelization Endpoints - Final Console Masterpiece V1
  app.post("/api/ai/chat", async (req, res) => {
    try {
      const { message, model, enforce_moonlight } = req.body;

      if (!message) {
        return res.status(400).json({ error: "Message is required" });
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

      res.json({
        response,
        model_used,
        dual_verification,
        timestamp: new Date().toISOString(),
      });
    } catch (error) {
      console.error("AI chat error:", error);
      res.status(500).json({ error: "AI chat failed" });
    }
  });

  app.post("/api/ai/eval", async (req, res) => {
    try {
      const { prompt, enable_dual_verification } = req.body;

      if (!prompt) {
        return res.status(400).json({ error: "Prompt is required" });
      }

      const startTime = Date.now();

      if (enable_dual_verification) {
        const [geminiResult, gptResult] = await Promise.all([
          simulateAIResponse(prompt, "gemini", ""),
          simulateAIResponse(prompt, "gpt", ""),
        ]);

        const verification_status = geminiResult === gptResult ? "OK" : "DISCREPANCY";

        res.json({
          result: geminiResult,
          gemini_result: geminiResult,
          gpt_result: gptResult,
          verification_status,
          execution_time_ms: Date.now() - startTime,
        });
      } else {
        const result = await simulateAIResponse(prompt, "gemini", "");

        res.json({
          result,
          verification_status: "N/A",
          execution_time_ms: Date.now() - startTime,
        });
      }
    } catch (error) {
      console.error("AI eval error:", error);
      res.status(500).json({ error: "AI eval failed" });
    }
  });

  app.post("/api/ai/ask", async (req, res) => {
    try {
      const { question, model } = req.body;

      if (!question) {
        return res.status(400).json({ error: "Question is required" });
      }

      const answer = await simulateAIResponse(question, model || "gemini", "");

      res.json({ answer });
    } catch (error) {
      console.error("AI ask error:", error);
      res.status(500).json({ error: "AI ask failed" });
    }
  });

  // LPO (Libral Protocol Optimizer) Endpoints
  app.get("/api/lpo/metrics/health-score", async (req, res) => {
    try {
      const score = Math.floor(Math.random() * 20) + 80;
      res.json({
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
      res.status(500).json({ error: "Failed to fetch health score" });
    }
  });

  app.get("/api/lpo/zk-audit/status", async (req, res) => {
    try {
      const verified = Math.random() > 0.1;
      res.json({
        verified,
        last_audit: new Date(Date.now() - Math.random() * 3600000).toISOString(),
        proof_count: Math.floor(Math.random() * 500) + 1000,
        failed_proofs: verified ? 0 : Math.floor(Math.random() * 5),
        next_audit: new Date(Date.now() + 300000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch ZK audit status" });
    }
  });

  app.get("/api/lpo/policies/active", async (req, res) => {
    try {
      res.json({
        policies: [
          { id: "modern-strong", name: "Modern Strong", active: true, priority: 1 },
          { id: "compatibility", name: "Compatibility", active: true, priority: 2 },
          { id: "backup-longterm", name: "Backup Longterm", active: false, priority: 3 },
        ],
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch policies" });
    }
  });

  app.post("/api/lpo/self-healing/trigger", async (req, res) => {
    try {
      const { component, severity } = req.body;
      res.json({
        healing_id: `heal-${Date.now()}`,
        component,
        severity,
        status: "initiated",
        estimated_completion: new Date(Date.now() + 30000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to trigger self-healing" });
    }
  });

  // Governance API Endpoints
  app.get("/api/governance/status", async (req, res) => {
    try {
      res.json({
        crad_status: "standby",
        amm_blocked_count: Math.floor(Math.random() * 10),
        rate_limit_enabled: true,
        rate_limit_threshold: 100,
        last_crad_trigger: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch governance status" });
    }
  });

  app.post("/api/governance/crad/trigger", async (req, res) => {
    try {
      const { reason } = req.body;
      if (!reason) {
        return res.status(400).json({ error: "Reason is required" });
      }
      res.json({
        trigger_id: `crad-${Date.now()}`,
        status: "executing",
        reason,
        initiated_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + 60000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to trigger CRAD" });
    }
  });

  app.post("/api/governance/amm/unblock", async (req, res) => {
    try {
      const { block_id, reason } = req.body;
      if (!block_id || !reason) {
        return res.status(400).json({ error: "Block ID and reason are required" });
      }
      res.json({
        unblock_id: `unblock-${Date.now()}`,
        block_id,
        status: "unblocked",
        reason,
        message: `Block ${block_id} has been successfully removed`,
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to unblock AMM" });
    }
  });

  // AEG (Auto Evolution Gateway) Endpoints
  app.post("/api/aeg/pr/generate", async (req, res) => {
    try {
      const { suggestion_id, branch_name } = req.body;
      if (!suggestion_id) {
        return res.status(400).json({ error: "Suggestion ID is required" });
      }
      res.json({
        pr_id: `pr-${Date.now()}`,
        suggestion_id,
        branch_name: branch_name || `feature/auto-evolution-${Date.now()}`,
        status: "draft",
        url: `https://github.com/libral-core/libral/pull/${Math.floor(Math.random() * 1000)}`,
        created_at: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to generate PR" });
    }
  });

  app.get("/api/aeg/priorities/top", async (req, res) => {
    try {
      const { limit = 5 } = req.query;
      const priorities = [
        { id: "p1", title: "Optimize GPG key generation performance", score: 98, category: "performance" },
        { id: "p2", title: "Implement Redis cluster failover", score: 95, category: "reliability" },
        { id: "p3", title: "Add rate limiting to Telegram webhook", score: 92, category: "security" },
        { id: "p4", title: "Refactor payment processing module", score: 88, category: "maintainability" },
        { id: "p5", title: "Enhance KBE federated learning algorithm", score: 85, category: "feature" },
      ].slice(0, Number(limit));
      res.json({ priorities });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch priorities" });
    }
  });

  app.get("/api/aeg/dashboard", async (req, res) => {
    try {
      res.json({
        total_suggestions: Math.floor(Math.random() * 50) + 100,
        prs_generated: Math.floor(Math.random() * 20) + 30,
        prs_merged: Math.floor(Math.random() * 15) + 20,
        avg_priority_score: Math.floor(Math.random() * 10) + 85,
        last_pr_at: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch AEG dashboard" });
    }
  });

  // KBE (Knowledge Booster Engine) Endpoints
  app.post("/api/kbe/knowledge/submit", async (req, res) => {
    try {
      const { category, content, tags } = req.body;
      if (!category || !content) {
        return res.status(400).json({ error: "Category and content are required" });
      }
      res.json({
        submission_id: `kbe-${Date.now()}`,
        category,
        status: "pending_aggregation",
        privacy_preserved: true,
        submitted_at: new Date().toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to submit knowledge" });
    }
  });

  app.post("/api/kbe/knowledge/lookup", async (req, res) => {
    try {
      const { query, category } = req.body;
      if (!query) {
        return res.status(400).json({ error: "Query is required" });
      }
      res.json({
        results: [
          { id: "kb1", title: "GPG Key Management Best Practices", relevance: 0.95, category: "security" },
          { id: "kb2", title: "Redis Cluster Configuration Guide", relevance: 0.88, category: "infrastructure" },
          { id: "kb3", title: "Telegram Bot API Rate Limits", relevance: 0.82, category: "api" },
        ],
        query,
        category: category || "all",
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to lookup knowledge" });
    }
  });

  app.get("/api/kbe/dashboard", async (req, res) => {
    try {
      res.json({
        total_submissions: Math.floor(Math.random() * 200) + 500,
        active_categories: Math.floor(Math.random() * 5) + 15,
        federated_nodes: Math.floor(Math.random() * 10) + 25,
        privacy_score: Math.floor(Math.random() * 5) + 95,
        last_aggregation: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch KBE dashboard" });
    }
  });

  app.get("/api/kbe/training-status", async (req, res) => {
    try {
      res.json({
        status: "running",
        progress: Math.floor(Math.random() * 30) + 65,
        epoch: Math.floor(Math.random() * 10) + 1,
        total_epochs: 50,
        estimated_completion: new Date(Date.now() + Math.random() * 7200000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch training status" });
    }
  });

  // Vaporization Protocol Endpoints
  app.post("/api/vaporization/enforce-ttl", async (req, res) => {
    try {
      const { pattern, ttl_seconds } = req.body;
      res.json({
        enforcement_id: `vap-${Date.now()}`,
        pattern: pattern || "*",
        ttl_seconds: ttl_seconds || 86400,
        keys_affected: Math.floor(Math.random() * 50) + 10,
        status: "enforced",
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to enforce TTL" });
    }
  });

  app.post("/api/vaporization/flush", async (req, res) => {
    try {
      const { pattern } = req.body;
      res.json({
        flush_id: `flush-${Date.now()}`,
        pattern: pattern || "*",
        keys_deleted: Math.floor(Math.random() * 100) + 50,
        status: "completed",
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to flush cache" });
    }
  });

  app.get("/api/vaporization/stats", async (req, res) => {
    try {
      res.json({
        total_keys: Math.floor(Math.random() * 500) + 1000,
        keys_with_ttl: Math.floor(Math.random() * 400) + 900,
        avg_ttl_remaining: Math.floor(Math.random() * 43200) + 43200,
        flushes_24h: Math.floor(Math.random() * 10) + 5,
        last_flush: new Date(Date.now() - Math.random() * 86400000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch vaporization stats" });
    }
  });

  // SelfEvolution Integration Endpoints
  app.get("/api/selfevolution/dashboard", async (req, res) => {
    try {
      res.json({
        lpo_health: Math.floor(Math.random() * 10) + 90,
        kbe_knowledge_count: Math.floor(Math.random() * 200) + 500,
        aeg_active_tasks: Math.floor(Math.random() * 20) + 10,
        vaporization_efficiency: Math.floor(Math.random() * 10) + 85,
        overall_status: "optimal",
        last_cycle: new Date(Date.now() - Math.random() * 3600000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch SelfEvolution dashboard" });
    }
  });

  app.post("/api/selfevolution/cycle/execute", async (req, res) => {
    try {
      res.json({
        cycle_id: `cycle-${Date.now()}`,
        status: "executing",
        modules_triggered: ["LPO", "KBE", "AEG", "Vaporization"],
        started_at: new Date().toISOString(),
        estimated_completion: new Date(Date.now() + 120000).toISOString(),
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to execute cycle" });
    }
  });

  app.get("/api/selfevolution/module-health", async (req, res) => {
    try {
      res.json({
        modules: [
          { name: "LPO", status: "healthy", uptime: 99.9, last_check: new Date().toISOString() },
          { name: "KBE", status: "healthy", uptime: 99.5, last_check: new Date().toISOString() },
          { name: "AEG", status: "healthy", uptime: 98.8, last_check: new Date().toISOString() },
          { name: "Vaporization", status: "healthy", uptime: 99.7, last_check: new Date().toISOString() },
          { name: "Governance", status: "healthy", uptime: 99.95, last_check: new Date().toISOString() },
        ],
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch module health" });
    }
  });

  // Middleware to track API requests
  app.use("/api/*", async (req: any, res, next) => {
    req.startTime = Date.now();
    
    res.on('finish', async () => {
      const responseTime = Date.now() - (req as any).startTime;
      
      // Update endpoint statistics
      await storage.updateEndpointStats(req.path, req.method, responseTime);
      
      // Log the API request
      await eventService.logApiRequest(req.path, req.method, responseTime, res.statusCode);
    });
    
    next();
  });

  const httpServer = createServer(app);
  
  // Initialize WebSocket service
  websocketService.initialize(httpServer);

  // Simulate some system events for demo purposes
  setInterval(async () => {
    // Simulate CPU usage updates
    const cpuUsage = Math.floor(Math.random() * 30) + 15;
    await storage.addMetric({
      metricType: "cpu_usage",
      value: cpuUsage.toString(),
      unit: "percent",
      source: "system"
    });

    // Simulate memory usage updates
    const memoryUsage = Math.floor(Math.random() * 20) + 60;
    await storage.addMetric({
      metricType: "memory_usage",
      value: memoryUsage.toString(),
      unit: "percent",
      source: "system"
    });

    // Broadcast metrics update
    websocketService.broadcastMetrics({
      cpuUsage: cpuUsage.toString(),
      memoryUsage: memoryUsage.toString()
    });
  }, 30000); // Update every 30 seconds

  return httpServer;
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
