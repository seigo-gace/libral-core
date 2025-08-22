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

export async function registerRoutes(app: Express): Promise<Server> {
  // Initialize services
  await redisService.connect();

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
      const activeUsers = await storage.getActiveUsers();
      res.json(activeUsers);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch users" });
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
