import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { telegramService } from "./services/telegram";
import { eventService } from "./services/events";
import { redisService } from "./services/redis";
import { websocketService } from "./services/websocket";
import { z } from "zod";

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
        Date.now() - req.startTime,
        200
      );
      
      res.json(result);
    } catch (error) {
      console.error("Webhook processing error:", error);
      
      await eventService.logApiRequest(
        req.path,
        req.method,
        Date.now() - req.startTime,
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

  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({ 
      status: "healthy", 
      timestamp: new Date().toISOString(),
      uptime: process.uptime()
    });
  });

  // Middleware to track API requests
  app.use("/api/*", async (req, res, next) => {
    req.startTime = Date.now();
    
    res.on('finish', async () => {
      const responseTime = Date.now() - req.startTime;
      
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
