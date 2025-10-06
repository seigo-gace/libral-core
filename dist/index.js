// server/index.ts
import express2 from "express";

// server/routes.ts
import { createServer } from "http";

// server/storage.ts
import { randomUUID } from "crypto";
var MemStorage = class {
  users = /* @__PURE__ */ new Map();
  transactions = /* @__PURE__ */ new Map();
  events = /* @__PURE__ */ new Map();
  modules = /* @__PURE__ */ new Map();
  metrics = /* @__PURE__ */ new Map();
  apiEndpoints = /* @__PURE__ */ new Map();
  stamps = /* @__PURE__ */ new Map();
  assets = /* @__PURE__ */ new Map();
  sessions = /* @__PURE__ */ new Map();
  constructor() {
    this.initializeDefaultData();
  }
  initializeDefaultData() {
    const defaultModules = [
      {
        id: "gateway",
        name: "\u901A\u4FE1\u30B2\u30FC\u30C8\u30A6\u30A7\u30A4",
        version: "v1.2.4",
        status: "active",
        port: 8001,
        endpoint: "/api/v1/gateway",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "auth",
        name: "\u30E6\u30FC\u30B6\u30FC\u7BA1\u7406",
        version: "v2.1.0",
        status: "active",
        port: 8002,
        endpoint: "/api/v1/auth",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "events",
        name: "\u30A4\u30D9\u30F3\u30C8\u7BA1\u7406",
        version: "v1.8.2",
        status: "high_load",
        port: 8003,
        endpoint: "/api/v1/events",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "payments",
        name: "\u6C7A\u6E08\u7BA1\u7406",
        version: "v1.5.1",
        status: "active",
        port: 8004,
        endpoint: "/api/v1/payments",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "api-hub",
        name: "API\u30CF\u30D6",
        version: "v3.0.1",
        status: "active",
        port: 8e3,
        endpoint: "/api/v1/hub",
        healthCheckUrl: "/health",
        metadata: {}
      }
    ];
    defaultModules.forEach((module) => {
      this.modules.set(module.id, {
        ...module,
        lastHealthCheck: /* @__PURE__ */ new Date()
      });
    });
    const now = /* @__PURE__ */ new Date();
    this.metrics.set("cpu-usage", {
      id: randomUUID(),
      metricType: "cpu_usage",
      value: "23",
      unit: "percent",
      source: "system",
      timestamp: now
    });
    this.metrics.set("memory-usage", {
      id: randomUUID(),
      metricType: "memory_usage",
      value: "68",
      unit: "percent",
      source: "system",
      timestamp: now
    });
    this.metrics.set("active-users", {
      id: randomUUID(),
      metricType: "active_users",
      value: "1247",
      unit: "count",
      source: "auth",
      timestamp: now
    });
    this.metrics.set("api-requests", {
      id: randomUUID(),
      metricType: "api_requests_per_minute",
      value: "892",
      unit: "count",
      source: "gateway",
      timestamp: now
    });
    this.initializeDefaultAssets();
  }
  initializeDefaultAssets() {
    const defaultAssets = [
      // Fonts
      {
        id: "rounded-sans",
        name: "Rounded Sans",
        type: "font",
        category: "free",
        price: "0",
        filePath: "/assets/fonts/rounded-sans.ttf",
        previewUrl: "/assets/previews/rounded-sans.png",
        metadata: { weight: "normal", style: "normal" }
      },
      {
        id: "bold-serif",
        name: "Bold Serif",
        type: "font",
        category: "free",
        price: "0",
        filePath: "/assets/fonts/bold-serif.ttf",
        previewUrl: "/assets/previews/bold-serif.png",
        metadata: { weight: "bold", style: "normal" }
      },
      {
        id: "handwritten",
        name: "Handwritten",
        type: "font",
        category: "free",
        price: "0",
        filePath: "/assets/fonts/handwritten.ttf",
        previewUrl: "/assets/previews/handwritten.png",
        metadata: { weight: "normal", style: "italic" }
      },
      // Characters
      {
        id: "cosmic-cat",
        name: "Cosmic Cat",
        type: "character",
        category: "free",
        price: "0",
        filePath: "/assets/characters/cosmic-cat.json",
        previewUrl: "/assets/previews/cosmic-cat.png",
        metadata: { animated: true, frames: 30 }
      },
      {
        id: "pixel-bot",
        name: "Pixel Bot",
        type: "character",
        category: "free",
        price: "0",
        filePath: "/assets/characters/pixel-bot.json",
        previewUrl: "/assets/previews/pixel-bot.png",
        metadata: { animated: true, frames: 24 }
      },
      {
        id: "happy-star",
        name: "Happy Star",
        type: "character",
        category: "free",
        price: "0",
        filePath: "/assets/characters/happy-star.json",
        previewUrl: "/assets/previews/happy-star.png",
        metadata: { animated: true, frames: 36 }
      },
      // Backgrounds
      {
        id: "simple-gradient",
        name: "Simple Gradient",
        type: "background",
        category: "free",
        price: "0",
        filePath: "/assets/backgrounds/simple-gradient.json",
        previewUrl: "/assets/previews/simple-gradient.png",
        metadata: { colors: ["#FF6B6B", "#4ECDC4"] }
      },
      {
        id: "sparkling",
        name: "Sparkling",
        type: "background",
        category: "free",
        price: "0",
        filePath: "/assets/backgrounds/sparkling.json",
        previewUrl: "/assets/previews/sparkling.png",
        metadata: { particles: 50, animated: true }
      },
      {
        id: "polka-dot",
        name: "Polka Dot",
        type: "background",
        category: "free",
        price: "0",
        filePath: "/assets/backgrounds/polka-dot.json",
        previewUrl: "/assets/previews/polka-dot.png",
        metadata: { pattern: "dots", colors: ["#FFE5E5", "#E5F3FF"] }
      },
      // Text Animations  
      {
        id: "bounce",
        name: "Bounce",
        type: "animation",
        category: "free",
        price: "0",
        filePath: "/assets/animations/bounce.json",
        previewUrl: "/assets/previews/bounce.gif",
        metadata: { duration: 1e3, easing: "bounce" }
      },
      {
        id: "fade-in",
        name: "Fade In",
        type: "animation",
        category: "free",
        price: "0",
        filePath: "/assets/animations/fade-in.json",
        previewUrl: "/assets/previews/fade-in.gif",
        metadata: { duration: 800, easing: "ease-in" }
      },
      {
        id: "wiggle",
        name: "Wiggle",
        type: "animation",
        category: "free",
        price: "0",
        filePath: "/assets/animations/wiggle.json",
        previewUrl: "/assets/previews/wiggle.gif",
        metadata: { duration: 1200, frequency: 3 }
      },
      // Effects
      {
        id: "confetti",
        name: "Confetti",
        type: "effect",
        category: "free",
        price: "0",
        filePath: "/assets/effects/confetti.json",
        previewUrl: "/assets/previews/confetti.gif",
        metadata: { particles: 100, duration: 2e3 }
      },
      {
        id: "lightning",
        name: "Lightning",
        type: "effect",
        category: "free",
        price: "0",
        filePath: "/assets/effects/lightning.json",
        previewUrl: "/assets/previews/lightning.gif",
        metadata: { strikes: 3, duration: 1500 }
      }
    ];
    defaultAssets.forEach((asset) => {
      this.assets.set(asset.id, {
        ...asset,
        creatorId: null,
        currency: asset.currency || "JPY",
        price: asset.price || "0",
        previewUrl: asset.previewUrl || null,
        isActive: true,
        createdAt: /* @__PURE__ */ new Date()
      });
    });
  }
  async getUser(id) {
    return this.users.get(id);
  }
  async getUserByTelegramId(telegramId) {
    return Array.from(this.users.values()).find((user) => user.telegramId === telegramId);
  }
  async createUser(insertUser) {
    const id = randomUUID();
    const user = {
      ...insertUser,
      id,
      role: insertUser.role || "user",
      createdAt: /* @__PURE__ */ new Date(),
      lastSeenAt: /* @__PURE__ */ new Date()
    };
    this.users.set(id, user);
    return user;
  }
  async updateUser(id, updates) {
    const user = this.users.get(id);
    if (!user) return void 0;
    const updatedUser = { ...user, ...updates };
    this.users.set(id, updatedUser);
    return updatedUser;
  }
  async getActiveUsers() {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1e3);
    return Array.from(this.users.values()).filter(
      (user) => user.lastSeenAt && user.lastSeenAt > oneDayAgo
    );
  }
  async createTransaction(insertTransaction) {
    const id = randomUUID();
    const transaction = {
      ...insertTransaction,
      id,
      status: insertTransaction.status || "pending",
      currency: insertTransaction.currency || "JPY",
      createdAt: /* @__PURE__ */ new Date(),
      completedAt: null
    };
    this.transactions.set(id, transaction);
    return transaction;
  }
  async getTransaction(id) {
    return this.transactions.get(id);
  }
  async getRecentTransactions(limit = 10) {
    return Array.from(this.transactions.values()).sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0)).slice(0, limit);
  }
  async updateTransactionStatus(id, status) {
    const transaction = this.transactions.get(id);
    if (!transaction) return void 0;
    const updatedTransaction = {
      ...transaction,
      status,
      completedAt: status === "completed" ? /* @__PURE__ */ new Date() : transaction.completedAt
    };
    this.transactions.set(id, updatedTransaction);
    return updatedTransaction;
  }
  async createEvent(insertEvent) {
    const id = randomUUID();
    const event = {
      ...insertEvent,
      id,
      data: insertEvent.data || {},
      level: insertEvent.level || "info",
      createdAt: /* @__PURE__ */ new Date()
    };
    this.events.set(id, event);
    return event;
  }
  async getRecentEvents(limit = 20) {
    return Array.from(this.events.values()).sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0)).slice(0, limit);
  }
  async getEventsByType(type, limit = 10) {
    return Array.from(this.events.values()).filter((event) => event.type === type).sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0)).slice(0, limit);
  }
  async upsertModule(insertModule) {
    const module = {
      ...insertModule,
      status: insertModule.status || "inactive",
      lastHealthCheck: /* @__PURE__ */ new Date()
    };
    this.modules.set(insertModule.id, module);
    return module;
  }
  async getModule(id) {
    return this.modules.get(id);
  }
  async getAllModules() {
    return Array.from(this.modules.values());
  }
  async updateModuleStatus(id, status) {
    const module = this.modules.get(id);
    if (!module) return void 0;
    const updatedModule = {
      ...module,
      status,
      lastHealthCheck: /* @__PURE__ */ new Date()
    };
    this.modules.set(id, updatedModule);
    return updatedModule;
  }
  async addMetric(insertMetric) {
    const id = randomUUID();
    const metric = {
      ...insertMetric,
      id,
      timestamp: /* @__PURE__ */ new Date()
    };
    this.metrics.set(`${insertMetric.metricType}-${Date.now()}`, metric);
    return metric;
  }
  async getLatestMetrics(metricType) {
    const metrics = Array.from(this.metrics.values()).filter((m) => m.metricType === metricType).sort((a, b) => (b.timestamp?.getTime() || 0) - (a.timestamp?.getTime() || 0));
    return metrics[0];
  }
  async getMetricsHistory(metricType, limit = 10) {
    return Array.from(this.metrics.values()).filter((m) => m.metricType === metricType).sort((a, b) => (b.timestamp?.getTime() || 0) - (a.timestamp?.getTime() || 0)).slice(0, limit);
  }
  async upsertApiEndpoint(insertEndpoint) {
    const key = `${insertEndpoint.method}:${insertEndpoint.path}`;
    const existing = this.apiEndpoints.get(key);
    const endpoint = {
      ...insertEndpoint,
      id: existing?.id || randomUUID(),
      requestCount: existing?.requestCount || 0,
      averageResponseTime: existing?.averageResponseTime || null,
      lastRequestAt: existing?.lastRequestAt || null
    };
    this.apiEndpoints.set(key, endpoint);
    return endpoint;
  }
  async getAllApiEndpoints() {
    return Array.from(this.apiEndpoints.values());
  }
  async updateEndpointStats(path4, method, responseTime) {
    const key = `${method}:${path4}`;
    const endpoint = this.apiEndpoints.get(key);
    if (endpoint) {
      const newCount = (endpoint.requestCount || 0) + 1;
      const currentAvg = parseFloat(endpoint.averageResponseTime || "0");
      const newAvg = (currentAvg * (newCount - 1) + responseTime) / newCount;
      const updatedEndpoint = {
        ...endpoint,
        requestCount: newCount,
        averageResponseTime: newAvg.toFixed(2),
        lastRequestAt: /* @__PURE__ */ new Date()
      };
      this.apiEndpoints.set(key, updatedEndpoint);
    }
  }
  // Stamp creation methods
  async createStamp(insertStamp) {
    const id = randomUUID();
    const stamp = {
      ...insertStamp,
      id,
      status: insertStamp.status || "processing",
      createdAt: /* @__PURE__ */ new Date(),
      completedAt: null
    };
    this.stamps.set(id, stamp);
    return stamp;
  }
  async getStamp(id) {
    return this.stamps.get(id);
  }
  async getStampsByUserId(userId) {
    return Array.from(this.stamps.values()).filter((stamp) => stamp.userId === userId);
  }
  async updateStampStatus(id, status, fileUrl) {
    const stamp = this.stamps.get(id);
    if (!stamp) return void 0;
    const updatedStamp = {
      ...stamp,
      status,
      fileUrl: fileUrl || null,
      completedAt: status === "completed" ? /* @__PURE__ */ new Date() : stamp.completedAt
    };
    this.stamps.set(id, updatedStamp);
    return updatedStamp;
  }
  // Asset methods
  async createAsset(insertAsset) {
    const asset = {
      ...insertAsset,
      currency: insertAsset.currency || "JPY",
      price: insertAsset.price || "0",
      previewUrl: insertAsset.previewUrl || null,
      isActive: insertAsset.isActive !== false,
      createdAt: /* @__PURE__ */ new Date()
    };
    this.assets.set(insertAsset.id, asset);
    return asset;
  }
  async getAssetsByType(type) {
    return Array.from(this.assets.values()).filter((asset) => asset.type === type && asset.isActive);
  }
  async getAsset(id) {
    return this.assets.get(id);
  }
  // Session methods
  async createSession(insertSession) {
    const id = randomUUID();
    const session = {
      ...insertSession,
      id,
      sessionData: insertSession.sessionData || {},
      lastUpdated: /* @__PURE__ */ new Date()
    };
    this.sessions.set(id, session);
    return session;
  }
  async getSession(id) {
    return this.sessions.get(id);
  }
  async updateSession(id, sessionData) {
    const session = this.sessions.get(id);
    if (!session) return void 0;
    const updatedSession = {
      ...session,
      sessionData,
      lastUpdated: /* @__PURE__ */ new Date()
    };
    this.sessions.set(id, updatedSession);
    return updatedSession;
  }
  async deleteExpiredSessions() {
    const now = /* @__PURE__ */ new Date();
    Array.from(this.sessions.entries()).forEach(([id, session]) => {
      if (session.expiresAt < now) {
        this.sessions.delete(id);
      }
    });
  }
};
var storage = new MemStorage();

// server/services/redis.ts
var RedisService = class {
  client;
  publisher;
  subscriber;
  constructor() {
    this.client = this.createMockRedisClient();
    this.publisher = this.client;
    this.subscriber = this.client;
  }
  createMockRedisClient() {
    const subscribers = /* @__PURE__ */ new Map();
    return {
      connect: async () => {
        console.log("Redis connected (mock)");
      },
      disconnect: async () => {
        console.log("Redis disconnected (mock)");
      },
      publish: async (channel, message) => {
        console.log(`Publishing to ${channel}:`, message);
        const channelSubscribers = subscribers.get(channel) || [];
        channelSubscribers.forEach((callback) => {
          try {
            callback(message, channel);
          } catch (error) {
            console.error("Error in subscriber callback:", error);
          }
        });
      },
      subscribe: async (channel, callback) => {
        console.log(`Subscribing to ${channel}`);
        if (!subscribers.has(channel)) {
          subscribers.set(channel, []);
        }
        subscribers.get(channel).push(callback);
      },
      unsubscribe: async (channel) => {
        subscribers.delete(channel);
      },
      set: async (key, value) => {
        console.log(`Set ${key}: ${value}`);
      },
      get: async (key) => {
        console.log(`Get ${key}`);
        return null;
      },
      getStats: () => ({
        memoryUsed: "847 MB",
        connectedClients: 42,
        pubsubChannels: 8,
        hitRatio: "94.2%"
      })
    };
  }
  async connect() {
    await this.client.connect();
  }
  async disconnect() {
    await this.client.disconnect();
  }
  async publish(channel, data) {
    const message = JSON.stringify(data);
    await this.publisher.publish(channel, message);
  }
  async subscribe(channel, callback) {
    await this.subscriber.subscribe(channel, (message) => {
      try {
        const data = JSON.parse(message);
        callback(data);
      } catch (error) {
        console.error("Error parsing Redis message:", error);
      }
    });
  }
  async unsubscribe(channel) {
    await this.subscriber.unsubscribe(channel);
  }
  async set(key, value, ttl) {
    const stringValue = typeof value === "string" ? value : JSON.stringify(value);
    await this.client.set(key, stringValue);
    if (ttl) {
      await this.client.expire(key, ttl);
    }
  }
  async get(key) {
    const value = await this.client.get(key);
    if (!value) return null;
    try {
      return JSON.parse(value);
    } catch {
      return value;
    }
  }
  getStats() {
    return this.client.getStats();
  }
};
var redisService = new RedisService();

// server/services/events.ts
var EventService = class {
  eventHandlers = /* @__PURE__ */ new Map();
  constructor() {
    this.setupEventChannels();
  }
  async setupEventChannels() {
    await redisService.subscribe("system.events", this.handleSystemEvent.bind(this));
    await redisService.subscribe("user.events", this.handleUserEvent.bind(this));
    await redisService.subscribe("payment.events", this.handlePaymentEvent.bind(this));
    await redisService.subscribe("api.events", this.handleApiEvent.bind(this));
  }
  async publishEvent(type, source, data, userId, level = "info") {
    const event = {
      type,
      source,
      userId,
      data,
      level
    };
    const storedEvent = await storage.createEvent(event);
    await redisService.publish("system.events", {
      ...storedEvent,
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
    this.triggerLocalHandlers(type, storedEvent);
    return storedEvent;
  }
  async handleSystemEvent(eventData) {
    console.log("System event received:", eventData);
  }
  async handleUserEvent(eventData) {
    console.log("User event received:", eventData);
  }
  async handlePaymentEvent(eventData) {
    console.log("Payment event received:", eventData);
  }
  async handleApiEvent(eventData) {
    console.log("API event received:", eventData);
  }
  onEvent(eventType, handler) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }
  triggerLocalHandlers(eventType, eventData) {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach((handler) => {
      try {
        handler(eventData);
      } catch (error) {
        console.error(`Error in event handler for ${eventType}:`, error);
      }
    });
  }
  // Convenience methods for common events
  async logUserAuth(userId, success) {
    return this.publishEvent(
      success ? "user_auth_success" : "user_auth_failed",
      "auth",
      { success },
      userId,
      success ? "info" : "warning"
    );
  }
  async logApiRequest(path4, method, responseTime, status) {
    return this.publishEvent(
      "api_request",
      "gateway",
      { path: path4, method, responseTime, status },
      void 0,
      status >= 400 ? "warning" : "info"
    );
  }
  async logPaymentEvent(transactionId, userId, amount, status) {
    return this.publishEvent(
      `payment_${status}`,
      "payments",
      { transactionId, amount },
      userId,
      status === "failed" ? "error" : "info"
    );
  }
  async logWebhookReceived(source, data) {
    return this.publishEvent(
      "webhook_received",
      "gateway",
      data,
      void 0,
      "info"
    );
  }
  async logModuleHealthCheck(moduleId, status) {
    return this.publishEvent(
      "module_health_check",
      "system",
      { moduleId, status },
      void 0,
      status === "error" ? "error" : "info"
    );
  }
};
var eventService = new EventService();

// server/services/telegram.ts
var TelegramService = class {
  botToken;
  constructor() {
    this.botToken = process.env.TELEGRAM_BOT_TOKEN || "mock_token";
  }
  async processWebhook(webhookData) {
    await eventService.logWebhookReceived("telegram", webhookData);
    if (webhookData.message) {
      return this.handleMessage(webhookData.message);
    }
    if (webhookData.pre_checkout_query) {
      return this.handlePreCheckoutQuery(webhookData.pre_checkout_query);
    }
    if (webhookData.successful_payment) {
      return this.handleSuccessfulPayment(webhookData.successful_payment, webhookData.message?.from);
    }
    return { status: "ok", message: "Webhook processed" };
  }
  async handleMessage(message) {
    const telegramId = message.from.id.toString();
    let user = await storage.getUserByTelegramId(telegramId);
    if (!user) {
      const newUser = {
        telegramId,
        username: message.from.username,
        firstName: message.from.first_name,
        lastName: message.from.last_name,
        role: "user",
        settings: {}
      };
      user = await storage.createUser(newUser);
      await eventService.publishEvent(
        "user_registered",
        "telegram",
        { telegramId: message.from.username || telegramId },
        user.id
      );
    } else {
      await storage.updateUser(user.id, { lastSeenAt: /* @__PURE__ */ new Date() });
    }
    await eventService.logUserAuth(user.id, true);
    if (message.text) {
      await this.handleTextMessage(user, message.text);
    }
    return { status: "ok", user_id: user.id };
  }
  async handleTextMessage(user, text) {
    if (text.startsWith("/start")) {
      await this.sendMessage(user.telegramId, "Welcome to Libral Core!");
    } else if (text.startsWith("/status")) {
      const modules = await storage.getAllModules();
      const activeModules = modules.filter((m) => m.status === "active").length;
      await this.sendMessage(user.telegramId, `System Status: ${activeModules}/${modules.length} modules active`);
    }
  }
  async handlePreCheckoutQuery(preCheckoutQuery) {
    await eventService.publishEvent(
      "payment_pre_checkout",
      "telegram",
      {
        queryId: preCheckoutQuery.id,
        amount: preCheckoutQuery.total_amount,
        currency: preCheckoutQuery.currency
      }
    );
    return this.answerPreCheckoutQuery(preCheckoutQuery.id, true);
  }
  async handleSuccessfulPayment(payment, from) {
    if (!from) return { status: "error", message: "No user data in payment" };
    const user = await storage.getUserByTelegramId(from.id.toString());
    if (!user) return { status: "error", message: "User not found" };
    const transaction = {
      userId: user.id,
      type: "telegram_stars",
      amount: (payment.total_amount / 100).toString(),
      // Convert from kopecks to rubles
      currency: payment.currency,
      telegramPaymentId: payment.telegram_payment_charge_id,
      status: "completed",
      metadata: {
        provider_charge_id: payment.provider_payment_charge_id,
        invoice_payload: payment.invoice_payload
      }
    };
    const savedTransaction = await storage.createTransaction(transaction);
    await eventService.logPaymentEvent(
      savedTransaction.id,
      user.id,
      transaction.amount,
      "completed"
    );
    return { status: "ok", transaction_id: savedTransaction.id };
  }
  async sendMessage(chatId, text) {
    console.log(`Sending message to ${chatId}: ${text}`);
    await eventService.publishEvent(
      "message_sent",
      "telegram",
      { chatId, text }
    );
    return { message_id: Date.now(), text };
  }
  async answerPreCheckoutQuery(queryId, ok, errorMessage) {
    console.log(`Answering pre-checkout query ${queryId}: ${ok ? "OK" : "ERROR"}`);
    return { ok: true };
  }
  async createInvoice(chatId, title, description, payload, currency, prices) {
    console.log(`Creating invoice for ${chatId}: ${title}`);
    return {
      invoice_url: `https://t.me/invoice/${Date.now()}`,
      payload
    };
  }
  async setWebhook(url) {
    console.log(`Setting webhook to: ${url}`);
    return { ok: true, url };
  }
};
var telegramService = new TelegramService();

// server/services/websocket.ts
import { WebSocketServer, WebSocket } from "ws";
var WebSocketService = class {
  wss = null;
  clients = /* @__PURE__ */ new Set();
  initialize(server) {
    this.wss = new WebSocketServer({ server, path: "/ws" });
    this.wss.on("connection", (ws, req) => {
      console.log("WebSocket client connected");
      this.clients.add(ws);
      ws.on("message", (message) => {
        try {
          const data = JSON.parse(message.toString());
          this.handleMessage(ws, data);
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      });
      ws.on("close", () => {
        console.log("WebSocket client disconnected");
        this.clients.delete(ws);
      });
      ws.on("error", (error) => {
        console.error("WebSocket error:", error);
        this.clients.delete(ws);
      });
      this.sendToClient(ws, {
        type: "connection",
        status: "connected",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      });
    });
    this.setupEventSubscriptions();
  }
  async setupEventSubscriptions() {
    await redisService.subscribe("system.events", (eventData) => {
      this.broadcast({
        type: "system_event",
        data: eventData
      });
    });
    await redisService.subscribe("metrics.update", (metricsData) => {
      this.broadcast({
        type: "metrics_update",
        data: metricsData
      });
    });
    await redisService.subscribe("module.status", (statusData) => {
      this.broadcast({
        type: "module_status",
        data: statusData
      });
    });
  }
  handleMessage(ws, data) {
    switch (data.type) {
      case "ping":
        this.sendToClient(ws, { type: "pong", timestamp: (/* @__PURE__ */ new Date()).toISOString() });
        break;
      case "subscribe":
        this.sendToClient(ws, { type: "subscribed", channel: data.channel });
        break;
      default:
        console.log("Unknown WebSocket message type:", data.type);
    }
  }
  sendToClient(ws, data) {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }
  broadcast(data) {
    const message = JSON.stringify(data);
    this.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }
  // Broadcast system metrics updates
  broadcastMetrics(metrics) {
    this.broadcast({
      type: "metrics_update",
      data: metrics,
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
  }
  // Broadcast module status updates
  broadcastModuleStatus(moduleId, status) {
    this.broadcast({
      type: "module_status",
      data: { moduleId, status },
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
  }
  // Broadcast new events
  broadcastEvent(event) {
    this.broadcast({
      type: "new_event",
      data: event,
      timestamp: (/* @__PURE__ */ new Date()).toISOString()
    });
  }
};
var websocketService = new WebSocketService();

// server/core/transport/policy.ts
import fs from "node:fs";
import path from "node:path";
import yaml from "yaml";
function loadRoutingConfig(file = path.resolve(process.cwd(), "config/routing.yaml")) {
  try {
    const content = fs.readFileSync(file, "utf-8");
    return yaml.parse(content);
  } catch (error) {
    console.warn(`Failed to load routing config from ${file}, using defaults:`, error);
    return getDefaultConfig();
  }
}
function getDefaultConfig() {
  return {
    routing: {
      default: { priority: ["telegram", "email", "webhook"] }
    },
    retry: {
      max_attempts: 3,
      backoff_ms: [1e3, 2e3, 5e3]
    },
    circuit_breaker: {
      failure_threshold: 5,
      cool_down_sec: 60
    }
  };
}
function decidePriority(cfg, meta) {
  if (cfg.routing.by_tenant?.[meta.tenant_id]) {
    return cfg.routing.by_tenant[meta.tenant_id].priority;
  }
  if (cfg.routing.by_usecase?.[meta.usecase]) {
    return cfg.routing.by_usecase[meta.usecase].priority;
  }
  if (cfg.routing.rules) {
    for (const rule of cfg.routing.rules) {
      const matches = Object.entries(rule.if).every(([key, value]) => {
        if (key === "sensitivity") {
          return meta.sensitivity === value;
        }
        if (key === "data_size_mb") {
          const operator = value.slice(0, 2);
          const threshold = Number(value.slice(2));
          const sizeMB = meta.size_bytes / (1024 * 1024);
          if (operator === ">=") return sizeMB >= threshold;
          if (operator === "<=") return sizeMB <= threshold;
          return false;
        }
        return false;
      });
      if (matches) {
        return rule.then.priority;
      }
    }
  }
  return cfg.routing.default.priority;
}

// server/core/transport/router.ts
var TransportRouter = class {
  constructor(adapters, cfg, emitAudit2) {
    this.adapters = adapters;
    this.cfg = cfg;
    this.emitAudit = emitAudit2;
  }
  circuitBreakers = /* @__PURE__ */ new Map();
  getAdapter(name) {
    return this.adapters.find((a) => a.name() === name);
  }
  isCircuitOpen(name) {
    const breaker = this.circuitBreakers.get(name);
    if (!breaker) return false;
    const coolDownMs = this.cfg.circuit_breaker.cool_down_sec * 1e3;
    const isInCoolDown = Date.now() - breaker.lastFailure < coolDownMs;
    const tooManyFailures = breaker.failures >= this.cfg.circuit_breaker.failure_threshold;
    return tooManyFailures && isInCoolDown;
  }
  recordFailure(name) {
    const existing = this.circuitBreakers.get(name) || { failures: 0, lastFailure: 0 };
    this.circuitBreakers.set(name, {
      failures: existing.failures + 1,
      lastFailure: Date.now()
    });
  }
  recordSuccess(name) {
    this.circuitBreakers.delete(name);
  }
  async sendWithFailover(input) {
    const priorityOrder = decidePriority(this.cfg, input.metadata);
    for (const adapterName of priorityOrder) {
      if (this.isCircuitOpen(adapterName)) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "circuit_breaker_open",
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }
      const adapter = this.getAdapter(adapterName);
      if (!adapter) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "adapter_not_found",
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }
      try {
        const isHealthy = await adapter.health();
        if (!isHealthy) {
          this.emitAudit({
            type: "send_skipped",
            transport: adapterName,
            reason: "health_check_failed",
            tenant_id: input.metadata.tenant_id,
            usecase: input.metadata.usecase,
            idempotency_key: input.metadata.idempotency_key,
            ts: Date.now()
          });
          continue;
        }
      } catch (healthError) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "health_check_error",
          error: String(healthError),
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }
      try {
        const result = await adapter.send(input);
        this.emitAudit({
          type: "send_attempt",
          transport: adapterName,
          ok: result.ok,
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          error: result.error || null,
          ts: Date.now()
        });
        if (result.ok) {
          this.recordSuccess(adapterName);
          return { ...result, transport: adapterName };
        } else {
          this.recordFailure(adapterName);
        }
      } catch (sendError) {
        this.recordFailure(adapterName);
        this.emitAudit({
          type: "send_attempt",
          transport: adapterName,
          ok: false,
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          error: String(sendError),
          ts: Date.now()
        });
      }
    }
    this.emitAudit({
      type: "send_queued",
      reason: "all_transports_failed",
      tenant_id: input.metadata.tenant_id,
      usecase: input.metadata.usecase,
      idempotency_key: input.metadata.idempotency_key,
      attempted_transports: priorityOrder,
      ts: Date.now()
    });
    return {
      ok: false,
      error: "QUEUED_FOR_RETRY",
      retryAfter: this.cfg.retry.backoff_ms[0] / 1e3
    };
  }
};

// server/adapters/telegram.ts
var TelegramAdapter = class {
  constructor(token, resolveChatId) {
    this.token = token;
    this.resolveChatId = resolveChatId;
  }
  name() {
    return "telegram";
  }
  async health() {
    return Boolean(this.token);
  }
  async send(input) {
    try {
      if (!this.token) {
        return { ok: false, error: "TELEGRAM_BOT_TOKEN not configured" };
      }
      const chatId = this.resolveChatId(input.to);
      const formData = new FormData();
      formData.append("chat_id", chatId);
      formData.append("document", new Blob([input.body], { type: "application/pgp-encrypted" }), "encrypted_message.pgp");
      if (input.subject) {
        formData.append("caption", input.subject);
      }
      const response = await fetch(`https://api.telegram.org/bot${this.token}/sendDocument`, {
        method: "POST",
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
};

// server/adapters/email.ts
var EmailAdapter = class {
  constructor(smtpUrl, fromAddress) {
    this.smtpUrl = smtpUrl;
    this.fromAddress = fromAddress;
  }
  name() {
    return "email";
  }
  async health() {
    return Boolean(this.smtpUrl && this.fromAddress);
  }
  async send(input) {
    try {
      if (!this.smtpUrl || !this.fromAddress) {
        return {
          ok: false,
          error: "SMTP_URL or MAIL_FROM not configured"
        };
      }
      console.log(`[EMAIL] Mock sending to ${input.to}:`);
      console.log(`  From: ${this.fromAddress}`);
      console.log(`  Subject: ${input.subject || "Encrypted Message"}`);
      console.log(`  Body size: ${input.body.length} characters (Base64)`);
      console.log(`  Metadata:`, input.metadata);
      await new Promise((resolve) => setTimeout(resolve, 100 + Math.random() * 200));
      const shouldSucceed = Math.random() > 0.1;
      if (shouldSucceed) {
        return {
          ok: true,
          id: `email:${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
          transport: "email"
        };
      } else {
        return {
          ok: false,
          error: "Mock SMTP timeout"
        };
      }
    } catch (error) {
      return {
        ok: false,
        error: error instanceof Error ? error.message : String(error)
      };
    }
  }
};

// server/adapters/webhook.ts
var WebhookAdapter = class {
  name() {
    return "webhook";
  }
  async health() {
    return true;
  }
  async send(input) {
    try {
      let webhookUrl;
      try {
        webhookUrl = new URL(input.to);
      } catch (urlError) {
        return {
          ok: false,
          error: `Invalid webhook URL: ${input.to}`
        };
      }
      const payload = {
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        subject: input.subject,
        encrypted_data: input.body,
        metadata: input.metadata,
        source: "libral-transport-core"
      };
      const response = await fetch(webhookUrl.toString(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "Libral-Transport-Core/1.0"
        },
        body: JSON.stringify(payload),
        // 10 second timeout
        signal: AbortSignal.timeout(1e4)
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
      if (error instanceof Error && error.name === "AbortError") {
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
};

// server/core/transport/bootstrap.ts
var _router = null;
var emitAudit = (evt) => {
  console.log(`[TRANSPORT] ${evt.type}:`, JSON.stringify(evt, null, 2));
};
function getTransportRouter() {
  if (!_router) {
    throw new Error("Transport router not initialized. Call initTransport() first.");
  }
  return _router;
}
function initTransport() {
  if (_router) {
    console.log("[TRANSPORT] Router already initialized");
    return;
  }
  console.log("[TRANSPORT] Initializing transport system...");
  try {
    const config = loadRoutingConfig();
    const telegramAdapter = new TelegramAdapter(
      process.env.TELEGRAM_BOT_TOKEN || "",
      (to) => to
      // Simple identity function, can be enhanced for user ID resolution
    );
    const emailAdapter = new EmailAdapter(
      process.env.SMTP_URL,
      process.env.MAIL_FROM || "Libral Core <no-reply@example.com>"
    );
    const webhookAdapter = new WebhookAdapter();
    _router = new TransportRouter(
      [telegramAdapter, emailAdapter, webhookAdapter],
      config,
      emitAudit
    );
    console.log(
      "[TRANSPORT] Router initialized with adapters:",
      [telegramAdapter, emailAdapter, webhookAdapter].map((a) => a.name())
    );
  } catch (error) {
    console.error("[TRANSPORT] Failed to initialize transport system:", error);
    throw error;
  }
}

// server/modules/stamp-creator.ts
var StampCreatorModule = class {
  id = "stamp-creator";
  name = "\u30B9\u30BF\u30F3\u30D7\u4F5C\u6210\u30B7\u30B9\u30C6\u30E0";
  version = "v1.0.0";
  status = "active";
  endpoints = [
    "/api/stamps/create",
    "/api/stamps/preview",
    "/api/stamps/assets",
    "/api/ai/suggest-emojis"
  ];
  capabilities = [
    "ai-emoji-suggestion",
    "multi-asset-composition",
    "real-time-preview",
    "telegram-sticker-export"
  ];
  constructor() {
    this.initialize();
  }
  async initialize() {
    console.log(`[${this.id}] Initializing ${this.name} ${this.version}`);
    this.status = "active";
  }
  async health() {
    return this.status === "active";
  }
  async getInfo() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      status: this.status,
      endpoints: this.endpoints,
      capabilities: this.capabilities,
      uptime: process.uptime(),
      lastCheck: (/* @__PURE__ */ new Date()).toISOString()
    };
  }
};
var stampCreatorModule = new StampCreatorModule();

// server/modules/aegis-pgp.ts
var AegisPgpCoreModule = class {
  id = "aegis-pgp";
  name = "Aegis-PGP\u6697\u53F7\u5316\u30B7\u30B9\u30C6\u30E0";
  version = "v1.0.0";
  status = "active";
  endpoints = [
    "/v1/encrypt",
    "/v1/decrypt",
    "/v1/sign",
    "/v1/verify",
    "/v1/send",
    "/v1/wkd-path",
    "/v1/inspect"
  ];
  capabilities = [
    "modern-pgp-encryption",
    "context-lock-signatures",
    "wkd-support",
    "multi-transport-failover",
    "seipd-v2-ocb",
    "openpgp-v6-keys"
  ];
  policies = ["modern-strong", "compat", "backup-longterm"];
  transports = ["telegram", "email", "webhook"];
  constructor() {
    this.initialize();
  }
  async initialize() {
    console.log(`[${this.id}] Initializing ${this.name} ${this.version}`);
    try {
      const healthUrl = process.env.AEGIS_URL || "http://localhost:8787";
      const response = await fetch(`${healthUrl}/v1/health`);
      if (response.ok) {
        console.log(`[${this.id}] Connected to Aegis-PGP Core API`);
      } else {
        console.log(`[${this.id}] Aegis-PGP Core API not available, using mock mode`);
      }
    } catch (error) {
      console.log(`[${this.id}] Aegis-PGP Core API not available, using mock mode`);
    }
    this.status = "active";
  }
  async health() {
    return this.status === "active";
  }
  async getInfo() {
    return {
      id: this.id,
      name: this.name,
      version: this.version,
      status: this.status,
      endpoints: this.endpoints,
      capabilities: this.capabilities,
      policies: this.policies,
      transports: this.transports,
      uptime: process.uptime(),
      lastCheck: (/* @__PURE__ */ new Date()).toISOString(),
      mode: process.env.NODE_ENV === "development" ? "mock" : "production"
    };
  }
};
var aegisPgpModule = new AegisPgpCoreModule();

// server/modules/registry.ts
var ModuleRegistry = class {
  modules = /* @__PURE__ */ new Map();
  constructor() {
    this.registerModule(stampCreatorModule);
    this.registerModule(aegisPgpModule);
  }
  registerModule(module) {
    this.modules.set(module.id, module);
    console.log(`[REGISTRY] Registered module: ${module.id} (${module.name})`);
  }
  getModule(id) {
    return this.modules.get(id);
  }
  getAllModules() {
    return Array.from(this.modules.values());
  }
  async getModuleStatus(id) {
    const module = this.getModule(id);
    if (!module) return null;
    return await module.getInfo();
  }
  async getAllModuleStatuses() {
    const statuses = [];
    for (const [, module] of this.modules) {
      statuses.push(await module.getInfo());
    }
    return statuses;
  }
};
var moduleRegistry = new ModuleRegistry();

// server/crypto/aegisClient.ts
var AEGIS = process.env.AEGIS_URL || "http://localhost:8787";
async function encrypt(req) {
  const r = await fetch(`${AEGIS}/v1/encrypt`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`encrypt failed ${r.status}`);
  return r.json();
}
async function decrypt(req) {
  const r = await fetch(`${AEGIS}/v1/decrypt`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`decrypt failed ${r.status}`);
  return r.json();
}
async function sign(req) {
  const r = await fetch(`${AEGIS}/v1/sign`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`sign failed ${r.status}`);
  return r.json();
}
async function verify(req) {
  const r = await fetch(`${AEGIS}/v1/verify`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`verify failed ${r.status}`);
  return r.json();
}
async function getWkdPath(req) {
  const r = await fetch(`${AEGIS}/v1/wkd-path?email=${encodeURIComponent(req.email)}`, {
    method: "GET",
    headers: { "content-type": "application/json" }
  });
  if (!r.ok) throw new Error(`wkd-path failed ${r.status}`);
  return r.json();
}
async function inspect(req) {
  const r = await fetch(`${AEGIS}/v1/inspect`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req)
  });
  if (!r.ok) throw new Error(`inspect failed ${r.status}`);
  return r.json();
}
var mockAegisClient = {
  async encrypt(req) {
    console.log(`[MOCK] Encrypting for ${req.recipient} with policy ${req.policyId}`);
    return { pgp: Buffer.from(`MOCK_ENCRYPTED_${Date.now()}`).toString("base64") };
  },
  async decrypt(req) {
    console.log(`[MOCK] Decrypting with policy ${req.policyId}`);
    return { plain: Buffer.from(`MOCK_DECRYPTED_${Date.now()}`).toString("base64") };
  },
  async sign(req) {
    console.log(`[MOCK] Signing with context:`, req.ctxLabels);
    return { sig: Buffer.from(`MOCK_SIGNATURE_${Date.now()}`).toString("base64") };
  },
  async verify(req) {
    console.log(`[MOCK] Verifying signature, require context: ${req.requireContext}`);
    return { ok: true, details: { mock: true, verified_at: Date.now() } };
  },
  async getWkdPath(req) {
    const hash = Buffer.from(req.email).toString("hex").slice(0, 16);
    return { path: `/.well-known/openpgpkey/hu/${hash}` };
  },
  async inspect(req) {
    return {
      type: "mock",
      size: req.blob.length,
      timestamp: Date.now(),
      info: "Mock inspection result"
    };
  }
};
var aegisClient = process.env.NODE_ENV === "development" ? mockAegisClient : {
  encrypt,
  decrypt,
  sign,
  verify,
  getWkdPath,
  inspect
};

// server/routes/aegis.ts
import { nanoid } from "nanoid";
function registerAegisRoutes(app2) {
  app2.post("/api/aegis/encrypt", async (req, res) => {
    try {
      const { recipient, data, policyId = "modern-strong" } = req.body;
      if (!recipient || !data) {
        return res.status(400).json({ error: "Recipient and data are required" });
      }
      const requestId = nanoid();
      const result = await aegisClient.encrypt({ recipient, data, policyId });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "encrypt", policyId, requestId, ok: true },
        userId: "system"
      });
      res.json({ ...result, requestId });
    } catch (error) {
      console.error("Aegis encrypt error:", error);
      res.status(500).json({ error: "Encryption failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.post("/api/aegis/decrypt", async (req, res) => {
    try {
      const { blob, policyId = "modern-strong" } = req.body;
      if (!blob) {
        return res.status(400).json({ error: "Blob is required" });
      }
      const requestId = nanoid();
      const result = await aegisClient.decrypt({ blob, policyId });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "decrypt", policyId, requestId, ok: true },
        userId: "system"
      });
      res.json({ ...result, requestId });
    } catch (error) {
      console.error("Aegis decrypt error:", error);
      res.status(500).json({ error: "Decryption failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.post("/api/aegis/sign", async (req, res) => {
    try {
      const { data, ctxLabels } = req.body;
      if (!data) {
        return res.status(400).json({ error: "Data is required" });
      }
      const requestId = nanoid();
      const contextLabels = {
        "aegis.app": "libral-core@1.0",
        "aegis.ts": Date.now().toString(),
        "aegis.policy": "modern-strong",
        ...ctxLabels
      };
      const result = await aegisClient.sign({ data, ctxLabels: contextLabels });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "sign", contextLabels, requestId, ok: true },
        userId: "system"
      });
      res.json({ ...result, requestId });
    } catch (error) {
      console.error("Aegis sign error:", error);
      res.status(500).json({ error: "Signing failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.post("/api/aegis/verify", async (req, res) => {
    try {
      const { data, sig, requireContext = true } = req.body;
      if (!data || !sig) {
        return res.status(400).json({ error: "Data and signature are required" });
      }
      const requestId = nanoid();
      const result = await aegisClient.verify({ data, sig, requireContext });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "verify", requireContext, requestId, ok: result.ok },
        userId: "system"
      });
      res.json({ ...result, requestId });
    } catch (error) {
      console.error("Aegis verify error:", error);
      res.status(500).json({ error: "Verification failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.post("/api/aegis/send", async (req, res) => {
    try {
      const {
        to,
        data,
        recipient,
        subject,
        policyId = "modern-strong",
        sensitivity = "med",
        tenantId = "default",
        usecase = "secure-mail"
      } = req.body;
      if (!to || !data || !recipient) {
        return res.status(400).json({ error: "Destination, data, and recipient are required" });
      }
      const requestId = nanoid();
      const encrypted = await aegisClient.encrypt({ recipient, data, policyId });
      const router = getTransportRouter();
      const sendResult = await router.sendWithFailover({
        to,
        subject,
        body: encrypted.pgp,
        metadata: {
          tenant_id: tenantId,
          usecase,
          sensitivity,
          size_bytes: encrypted.pgp.length,
          idempotency_key: requestId
        }
      });
      await storage.createEvent({
        type: "secure_send",
        source: "aegis-pgp",
        data: {
          operation: "encrypt_and_send",
          policyId,
          transport: sendResult.transport,
          requestId,
          ok: sendResult.ok
        },
        userId: "system"
      });
      res.json({
        ok: sendResult.ok,
        transport: sendResult.transport,
        encrypted: true,
        policyId,
        requestId
      });
    } catch (error) {
      console.error("Aegis secure send error:", error);
      res.status(500).json({ error: "Secure send failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.get("/api/aegis/wkd-path", async (req, res) => {
    try {
      const email = req.query.email;
      if (!email) {
        return res.status(400).json({ error: "Email parameter is required" });
      }
      const result = await aegisClient.getWkdPath({ email });
      res.json(result);
    } catch (error) {
      console.error("WKD path error:", error);
      res.status(500).json({ error: "WKD path generation failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.post("/api/aegis/inspect", async (req, res) => {
    try {
      const { blob } = req.body;
      if (!blob) {
        return res.status(400).json({ error: "Blob is required" });
      }
      const result = await aegisClient.inspect({ blob });
      res.json(result);
    } catch (error) {
      console.error("Aegis inspect error:", error);
      res.status(500).json({ error: "Inspection failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
}

// server/routes.ts
async function registerRoutes(app2) {
  await redisService.connect();
  registerAegisRoutes(app2);
  app2.post("/api/telegram/webhook", async (req, res) => {
    try {
      const result = await telegramService.processWebhook(req.body);
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
  app2.get("/api/system/metrics", async (req, res) => {
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
  app2.get("/api/modules", async (req, res) => {
    try {
      const modules = await moduleRegistry.getAllModuleStatuses();
      const legacyModules = await storage.getAllModules();
      res.json([...modules, ...legacyModules]);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch modules" });
    }
  });
  app2.get("/api/modules/:id", async (req, res) => {
    try {
      const modules = await storage.getAllModules();
      res.json(modules);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch modules" });
    }
  });
  app2.patch("/api/modules/:id/status", async (req, res) => {
    try {
      const { id } = req.params;
      const { status } = req.body;
      const module = await storage.updateModuleStatus(id, status);
      if (!module) {
        return res.status(404).json({ error: "Module not found" });
      }
      await eventService.logModuleHealthCheck(id, status);
      websocketService.broadcastModuleStatus(id, status);
      res.json(module);
    } catch (error) {
      res.status(500).json({ error: "Failed to update module status" });
    }
  });
  app2.post("/api/modules/:id/start", async (req, res) => {
    try {
      const { id } = req.params;
      const result = await moduleRegistry.startModule(id);
      if (!result) {
        const module = await storage.updateModuleStatus(id, "active");
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
      }
      await eventService.publishEvent("module_started", "system", { moduleId: id });
      websocketService.broadcastModuleStatus(id, "active");
      res.json({ success: true, moduleId: id, status: "active" });
    } catch (error) {
      console.error(`Failed to start module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to start module" });
    }
  });
  app2.post("/api/modules/:id/restart", async (req, res) => {
    try {
      const { id } = req.params;
      const result = await moduleRegistry.restartModule(id);
      if (!result) {
        const module = await storage.updateModuleStatus(id, "updating");
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
        setTimeout(async () => {
          await storage.updateModuleStatus(id, "active");
          websocketService.broadcastModuleStatus(id, "active");
        }, 3e3);
      }
      await eventService.publishEvent("module_restarted", "system", { moduleId: id });
      websocketService.broadcastModuleStatus(id, "updating");
      res.json({ success: true, moduleId: id, status: "updating" });
    } catch (error) {
      console.error(`Failed to restart module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to restart module" });
    }
  });
  app2.post("/api/modules/:id/stop", async (req, res) => {
    try {
      const { id } = req.params;
      const result = await moduleRegistry.stopModule(id);
      if (!result) {
        const module = await storage.updateModuleStatus(id, "inactive");
        if (!module) {
          return res.status(404).json({ error: "Module not found" });
        }
      }
      await eventService.publishEvent("module_stopped", "system", { moduleId: id });
      websocketService.broadcastModuleStatus(id, "inactive");
      res.json({ success: true, moduleId: id, status: "inactive" });
    } catch (error) {
      console.error(`Failed to stop module ${req.params.id}:`, error);
      res.status(500).json({ error: "Failed to stop module" });
    }
  });
  app2.get("/api/events", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit) || 20;
      const events = await storage.getRecentEvents(limit);
      res.json(events);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch events" });
    }
  });
  app2.get("/api/transactions", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit) || 10;
      const transactions = await storage.getRecentTransactions(limit);
      res.json(transactions);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch transactions" });
    }
  });
  app2.get("/api/analytics/endpoints", async (req, res) => {
    try {
      const endpoints = await storage.getAllApiEndpoints();
      res.json(endpoints);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch API analytics" });
    }
  });
  app2.get("/api/infrastructure/status", async (req, res) => {
    try {
      const redisStats = redisService.getStats();
      const databaseStats = {
        connections: "23/100",
        size: "2.4 GB",
        queriesPerSecond: 156,
        replicationStatus: "\u540C\u671F\u6E08\u307F"
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
  app2.get("/api/users", async (req, res) => {
    try {
      const mockUsers = [
        {
          id: "1",
          username: "admin",
          email: "admin@libral.core",
          telegramId: "123456789",
          status: "active",
          role: "admin",
          createdAt: "2024-01-01T00:00:00Z",
          lastActive: (/* @__PURE__ */ new Date()).toISOString(),
          personalServerEnabled: true
        },
        {
          id: "2",
          username: "developer",
          email: "dev@libral.core",
          status: "active",
          role: "developer",
          createdAt: "2024-01-15T00:00:00Z",
          lastActive: (/* @__PURE__ */ new Date()).toISOString(),
          personalServerEnabled: true
        },
        {
          id: "3",
          username: "user1",
          email: "user@libral.core",
          status: "active",
          role: "user",
          createdAt: "2024-02-01T00:00:00Z",
          lastActive: "2024-02-28T10:30:00Z",
          personalServerEnabled: false
        }
      ];
      res.json(mockUsers);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch users" });
    }
  });
  app2.get("/api/users/stats", async (req, res) => {
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
  app2.get("/api/communication/adapters", async (req, res) => {
    try {
      const adapters = [
        {
          id: "telegram-1",
          name: "Telegram Bot API",
          type: "telegram",
          status: "active",
          messagesProcessed: 1247,
          lastActivity: (/* @__PURE__ */ new Date()).toISOString(),
          config: {}
        },
        {
          id: "email-1",
          name: "SMTP Gateway",
          type: "email",
          status: "active",
          messagesProcessed: 856,
          lastActivity: (/* @__PURE__ */ new Date()).toISOString(),
          config: {}
        },
        {
          id: "webhook-1",
          name: "Webhook Endpoint",
          type: "webhook",
          status: "inactive",
          messagesProcessed: 23,
          lastActivity: (/* @__PURE__ */ new Date()).toISOString(),
          config: {}
        }
      ];
      res.json(adapters);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch communication adapters" });
    }
  });
  app2.get("/api/communication/stats", async (req, res) => {
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
  app2.get("/api/events/stats", async (req, res) => {
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
  app2.get("/api/payments/stats", async (req, res) => {
    try {
      const stats = {
        totalRevenue: 12450.75,
        monthlyRevenue: 3250.5,
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
  app2.get("/api/credentials", async (req, res) => {
    try {
      const credentials = [
        {
          id: "openai-1",
          name: "OpenAI GPT-4",
          provider: "openai",
          status: "active",
          usage: 15e3,
          limit: 1e5,
          cost: 125.5,
          currency: "USD",
          lastUsed: (/* @__PURE__ */ new Date()).toISOString(),
          createdAt: "2024-01-01T00:00:00Z",
          encrypted: true
        },
        {
          id: "anthropic-1",
          name: "Claude 3.5 Sonnet",
          provider: "anthropic",
          status: "active",
          usage: 8500,
          limit: 5e4,
          cost: 85.25,
          currency: "USD",
          lastUsed: (/* @__PURE__ */ new Date()).toISOString(),
          createdAt: "2024-01-15T00:00:00Z",
          encrypted: true
        }
      ];
      res.json(credentials);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch API credentials" });
    }
  });
  app2.get("/api/integrations/stats", async (req, res) => {
    try {
      const stats = {
        totalCredentials: 5,
        activeIntegrations: 3,
        monthlyApiCalls: 285e3,
        totalCost: 485.75
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch integration stats" });
    }
  });
  app2.get("/api/database/connections", async (req, res) => {
    try {
      const connections = [
        {
          id: "postgres-1",
          name: "PostgreSQL Primary",
          type: "postgresql",
          status: "connected",
          connections: "23/100",
          responseTime: 15,
          uptime: 99.9,
          dataSize: "2.5 GB"
        },
        {
          id: "redis-1",
          name: "Redis Cache",
          type: "redis",
          status: "connected",
          connections: "5/50",
          responseTime: 2,
          uptime: 99.8,
          dataSize: "256 MB"
        },
        {
          id: "neon-1",
          name: "Neon Serverless",
          type: "neon",
          status: "connected",
          connections: "12/unlimited",
          responseTime: 8,
          uptime: 99.9,
          dataSize: "1.8 GB"
        }
      ];
      res.json(connections);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch database connections" });
    }
  });
  app2.get("/api/database/metrics", async (req, res) => {
    try {
      const metrics = {
        totalConnections: "23/100",
        queryPerSecond: 156,
        cacheHitRate: 94.2,
        diskUsage: "2.5 GB"
      };
      res.json(metrics);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch database metrics" });
    }
  });
  app2.get("/api/containers", async (req, res) => {
    try {
      const containers = [
        {
          id: "app-1",
          name: "libral-core-app",
          image: "node:22-alpine",
          status: "running",
          cpuUsage: 15,
          memoryUsage: 68,
          networkIO: "1.2MB/s",
          uptime: "2d 15h",
          ports: ["5000:5000"]
        },
        {
          id: "db-1",
          name: "postgres-db",
          image: "postgres:16",
          status: "running",
          cpuUsage: 5,
          memoryUsage: 25,
          networkIO: "0.5MB/s",
          uptime: "2d 15h",
          ports: ["5432:5432"]
        }
      ];
      res.json(containers);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch containers" });
    }
  });
  app2.get("/api/containers/stats", async (req, res) => {
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
  app2.get("/api/assets/:type", async (req, res) => {
    try {
      const { type } = req.params;
      const assets = await storage.getAssetsByType(type);
      res.json(assets);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch assets" });
    }
  });
  app2.post("/api/ai/suggest-emojis", async (req, res) => {
    try {
      const { text, characterId } = req.body;
      const emojiSuggestions = {
        "\u697D\u3057\u3044": ["\u{1F60A}", "\u{1F389}", "\u2728"],
        "\u304A\u3064\u304B\u308C": ["\u{1F60C}", "\u{1F31F}", "\u{1F4AA}"],
        "\u3042\u308A\u304C\u3068\u3046": ["\u{1F64F}", "\u{1F496}", "\u{1F338}"],
        "\u304A\u3081\u3067\u3068\u3046": ["\u{1F38A}", "\u{1F388}", "\u{1F3C6}"],
        "\u304C\u3093\u3070\u3063\u3066": ["\u{1F4AA}", "\u{1F525}", "\u2B50"],
        "default": ["\u{1F60A}", "\u2728", "\u{1F388}"]
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
  app2.post("/api/stamps/preview", async (req, res) => {
    try {
      const stampData = req.body;
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
  app2.post("/api/stamps/create", async (req, res) => {
    try {
      console.log("Received stamp creation request:", req.body);
      const stampData = req.body;
      const userId = "mock-user-id";
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
      try {
        const router = getTransportRouter();
        await router.sendWithFailover({
          to: userId,
          // In real app, this would be user's telegram ID or email
          subject: "\u30B9\u30BF\u30F3\u30D7\u4F5C\u6210\u5B8C\u4E86",
          body: Buffer.from(JSON.stringify({ stampId: stamp.id, text: stamp.text })).toString("base64"),
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
        "stamp_created",
        "stamp_creator",
        { stampId: stamp.id, text: stamp.text },
        userId
      );
      setTimeout(async () => {
        console.log(`Processing stamp ${stamp.id} - updating to completed`);
        await storage.updateStampStatus(stamp.id, "completed", `/stamps/${stamp.id}.tgs`);
        websocketService.broadcast({
          type: "stamp_completed",
          data: { stampId: stamp.id, userId }
        });
        console.log(`Stamp ${stamp.id} processing completed`);
      }, 3e3);
      res.json(stamp);
    } catch (error) {
      console.error("Stamp creation error:", error);
      res.status(500).json({ error: "Failed to create stamp", details: error instanceof Error ? error.message : String(error) });
    }
  });
  app2.get("/api/stamps/user/:userId", async (req, res) => {
    try {
      const { userId } = req.params;
      const stamps = await storage.getStampsByUserId(userId);
      res.json(stamps);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch user stamps" });
    }
  });
  app2.get("/api/health", (req, res) => {
    res.json({
      status: "healthy",
      timestamp: (/* @__PURE__ */ new Date()).toISOString(),
      uptime: process.uptime()
    });
  });
  app2.get("/api/aegis/keys", async (req, res) => {
    try {
      const keys = [
        {
          keyId: "F1B2C3D4E5F6G7H8",
          keyType: "EdDSA",
          userId: "Libral Admin <admin@libral.core>",
          fingerprint: "F1B2 C3D4 E5F6 G7H8 I9J0 K1L2 M3N4 O5P6 Q7R8 S9T0",
          createdAt: "2024-01-01",
          expiresAt: "2026-01-01",
          status: "active"
        },
        {
          keyId: "A9B8C7D6E5F4G3H2",
          keyType: "RSA-4096",
          userId: "System Backup <backup@libral.core>",
          fingerprint: "A9B8 C7D6 E5F4 G3H2 I1J0 K9L8 M7N6 O5P4 Q3R2 S1T0",
          createdAt: "2024-01-15",
          expiresAt: "2029-01-15",
          status: "active"
        }
      ];
      res.json(keys);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch GPG keys" });
    }
  });
  app2.post("/api/aegis/keys/generate", async (req, res) => {
    try {
      const { name, email, comment, passphrase, policy } = req.body;
      if (!name || !email) {
        return res.status(400).json({ error: "Name and email are required" });
      }
      const newKey = {
        keyId: Math.random().toString(36).substring(2, 18).toUpperCase(),
        keyType: policy === "Modern Strong" ? "EdDSA" : "RSA-4096",
        userId: `${name} <${email}>`,
        fingerprint: Array(10).fill(0).map(() => Math.random().toString(36).substring(2, 6).toUpperCase()).join(" "),
        createdAt: (/* @__PURE__ */ new Date()).toISOString().split("T")[0],
        expiresAt: new Date(Date.now() + 2 * 365 * 24 * 60 * 60 * 1e3).toISOString().split("T")[0],
        status: "active"
      };
      await eventService.publishEvent("gpg_key_generated", "aegis-pgp", {
        keyId: newKey.keyId,
        userId: newKey.userId
      });
      res.json(newKey);
    } catch (error) {
      res.status(500).json({ error: "Failed to generate GPG key" });
    }
  });
  app2.post("/api/aegis/encrypt", async (req, res) => {
    try {
      const { text, keyId, policy } = req.body;
      if (!text) {
        return res.status(400).json({ error: "Text is required" });
      }
      const encryptedData = {
        ciphertext: Buffer.from(text).toString("base64"),
        algorithm: policy === "Modern Strong" ? "AES-256-OCB" : "AES-256-GCM",
        keyId: keyId || "DEFAULT",
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      };
      await eventService.publishEvent("data_encrypted", "aegis-pgp", {
        size: text.length,
        algorithm: encryptedData.algorithm
      });
      res.json(encryptedData);
    } catch (error) {
      res.status(500).json({ error: "Failed to encrypt data" });
    }
  });
  app2.post("/api/aegis/decrypt", async (req, res) => {
    try {
      const { ciphertext, passphrase } = req.body;
      if (!ciphertext) {
        return res.status(400).json({ error: "Ciphertext is required" });
      }
      const decryptedText = Buffer.from(ciphertext, "base64").toString("utf8");
      await eventService.publishEvent("data_decrypted", "aegis-pgp", {
        success: true
      });
      res.json({ plaintext: decryptedText });
    } catch (error) {
      res.status(500).json({ error: "Failed to decrypt data" });
    }
  });
  app2.get("/api/settings", async (req, res) => {
    try {
      const settings = {
        general: {
          systemName: "Libral Core",
          adminEmail: "admin@libral.core",
          maintenanceMode: false,
          debugMode: false,
          logLevel: "info"
        },
        security: {
          sessionTimeout: 24,
          maxLoginAttempts: 3,
          passwordPolicy: "strong",
          twoFactorRequired: true,
          encryptionLevel: "aegis-pgp"
        },
        notifications: {
          emailNotifications: true,
          telegramNotifications: true,
          webhookNotifications: false,
          notificationThreshold: "medium"
        },
        performance: {
          cacheEnabled: true,
          cacheTTL: 3600,
          maxConcurrentUsers: 1e3,
          rateLimitEnabled: true,
          rateLimitPerMinute: 100
        }
      };
      res.json(settings);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch settings" });
    }
  });
  app2.put("/api/settings", async (req, res) => {
    try {
      const newSettings = req.body;
      await eventService.publishEvent("settings_updated", "system", {
        updatedBy: "admin"
      });
      res.json({ success: true, settings: newSettings });
    } catch (error) {
      res.status(500).json({ error: "Failed to update settings" });
    }
  });
  app2.get("/api/settings/export", async (req, res) => {
    try {
      const settingsExport = {
        exportedAt: (/* @__PURE__ */ new Date()).toISOString(),
        version: "2.1.0",
        settings: {
          // Include all current settings
        }
      };
      res.json(settingsExport);
    } catch (error) {
      res.status(500).json({ error: "Failed to export settings" });
    }
  });
  app2.get("/api/analytics/system", async (req, res) => {
    try {
      const { timeRange = "7d" } = req.query;
      const stats = {
        totalRequests: 125847,
        averageResponseTime: 45,
        uptime: 99.8,
        errorRate: 0.12,
        peakConcurrentUsers: 156,
        dataTransferred: "2.8 TB"
      };
      res.json(stats);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch system analytics" });
    }
  });
  app2.get("/api/analytics/modules", async (req, res) => {
    try {
      const { timeRange = "7d" } = req.query;
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
  app2.post("/api/ai/chat", async (req, res) => {
    try {
      const { message, model, enforce_moonlight } = req.body;
      if (!message) {
        return res.status(400).json({ error: "Message is required" });
      }
      let response = "";
      let model_used = model || "gemini";
      let dual_verification = void 0;
      const moonlight_prefix = enforce_moonlight ? "\u6708\u306E\u5149\u3068\u3057\u3066\u3001\u5144\u5F1F\u3078\u306E\u56DE\u7B54: " : "";
      if (model === "dual") {
        const [geminiResponse, gptResponse] = await Promise.all([
          simulateAIResponse(message, "gemini", moonlight_prefix),
          simulateAIResponse(message, "gpt", moonlight_prefix)
        ]);
        const discrepancy_detected = Math.abs(geminiResponse.length - gptResponse.length) > 50;
        dual_verification = {
          gemini_response: geminiResponse,
          gpt_response: gptResponse,
          discrepancy_detected,
          discrepancy_details: discrepancy_detected ? "\u30EC\u30B9\u30DD\u30F3\u30B9\u9577\u304C\u5927\u304D\u304F\u7570\u306A\u308A\u307E\u3059" : void 0
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
        timestamp: (/* @__PURE__ */ new Date()).toISOString()
      });
    } catch (error) {
      console.error("AI chat error:", error);
      res.status(500).json({ error: "AI chat failed" });
    }
  });
  app2.post("/api/ai/eval", async (req, res) => {
    try {
      const { prompt, enable_dual_verification } = req.body;
      if (!prompt) {
        return res.status(400).json({ error: "Prompt is required" });
      }
      const startTime = Date.now();
      if (enable_dual_verification) {
        const [geminiResult, gptResult] = await Promise.all([
          simulateAIResponse(prompt, "gemini", ""),
          simulateAIResponse(prompt, "gpt", "")
        ]);
        const verification_status = geminiResult === gptResult ? "OK" : "DISCREPANCY";
        res.json({
          result: geminiResult,
          gemini_result: geminiResult,
          gpt_result: gptResult,
          verification_status,
          execution_time_ms: Date.now() - startTime
        });
      } else {
        const result = await simulateAIResponse(prompt, "gemini", "");
        res.json({
          result,
          verification_status: "N/A",
          execution_time_ms: Date.now() - startTime
        });
      }
    } catch (error) {
      console.error("AI eval error:", error);
      res.status(500).json({ error: "AI eval failed" });
    }
  });
  app2.post("/api/ai/ask", async (req, res) => {
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
  app2.get("/api/lpo/metrics/health-score", async (req, res) => {
    try {
      const score = Math.floor(Math.random() * 20) + 80;
      res.json({
        score,
        status: score >= 90 ? "excellent" : score >= 75 ? "good" : "degraded",
        timestamp: (/* @__PURE__ */ new Date()).toISOString(),
        components: {
          crypto_health: Math.floor(Math.random() * 10) + 90,
          network_health: Math.floor(Math.random() * 10) + 85,
          storage_health: Math.floor(Math.random() * 15) + 80
        }
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch health score" });
    }
  });
  app2.get("/api/lpo/zk-audit/status", async (req, res) => {
    try {
      const verified = Math.random() > 0.1;
      res.json({
        verified,
        last_audit: new Date(Date.now() - Math.random() * 36e5).toISOString(),
        proof_count: Math.floor(Math.random() * 500) + 1e3,
        failed_proofs: verified ? 0 : Math.floor(Math.random() * 5),
        next_audit: new Date(Date.now() + 3e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch ZK audit status" });
    }
  });
  app2.get("/api/lpo/policies/active", async (req, res) => {
    try {
      res.json({
        policies: [
          { id: "modern-strong", name: "Modern Strong", active: true, priority: 1 },
          { id: "compatibility", name: "Compatibility", active: true, priority: 2 },
          { id: "backup-longterm", name: "Backup Longterm", active: false, priority: 3 }
        ]
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch policies" });
    }
  });
  app2.post("/api/lpo/self-healing/trigger", async (req, res) => {
    try {
      const { component, severity } = req.body;
      res.json({
        healing_id: `heal-${Date.now()}`,
        component,
        severity,
        status: "initiated",
        estimated_completion: new Date(Date.now() + 3e4).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to trigger self-healing" });
    }
  });
  app2.get("/api/governance/status", async (req, res) => {
    try {
      res.json({
        crad_status: "standby",
        amm_blocked_count: Math.floor(Math.random() * 10),
        rate_limit_enabled: true,
        rate_limit_threshold: 100,
        last_crad_trigger: new Date(Date.now() - Math.random() * 864e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch governance status" });
    }
  });
  app2.post("/api/governance/crad/trigger", async (req, res) => {
    try {
      const { reason } = req.body;
      if (!reason) {
        return res.status(400).json({ error: "Reason is required" });
      }
      res.json({
        trigger_id: `crad-${Date.now()}`,
        status: "executing",
        reason,
        initiated_at: (/* @__PURE__ */ new Date()).toISOString(),
        estimated_completion: new Date(Date.now() + 6e4).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to trigger CRAD" });
    }
  });
  app2.post("/api/governance/amm/unblock", async (req, res) => {
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
        message: `Block ${block_id} has been successfully removed`
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to unblock AMM" });
    }
  });
  app2.post("/api/aeg/pr/generate", async (req, res) => {
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
        url: `https://github.com/libral-core/libral/pull/${Math.floor(Math.random() * 1e3)}`,
        created_at: (/* @__PURE__ */ new Date()).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to generate PR" });
    }
  });
  app2.get("/api/aeg/priorities/top", async (req, res) => {
    try {
      const { limit = 5 } = req.query;
      const priorities = [
        { id: "p1", title: "Optimize GPG key generation performance", score: 98, category: "performance" },
        { id: "p2", title: "Implement Redis cluster failover", score: 95, category: "reliability" },
        { id: "p3", title: "Add rate limiting to Telegram webhook", score: 92, category: "security" },
        { id: "p4", title: "Refactor payment processing module", score: 88, category: "maintainability" },
        { id: "p5", title: "Enhance KBE federated learning algorithm", score: 85, category: "feature" }
      ].slice(0, Number(limit));
      res.json({ priorities });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch priorities" });
    }
  });
  app2.get("/api/aeg/dashboard", async (req, res) => {
    try {
      res.json({
        total_suggestions: Math.floor(Math.random() * 50) + 100,
        prs_generated: Math.floor(Math.random() * 20) + 30,
        prs_merged: Math.floor(Math.random() * 15) + 20,
        avg_priority_score: Math.floor(Math.random() * 10) + 85,
        last_pr_at: new Date(Date.now() - Math.random() * 864e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch AEG dashboard" });
    }
  });
  app2.post("/api/kbe/knowledge/submit", async (req, res) => {
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
        submitted_at: (/* @__PURE__ */ new Date()).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to submit knowledge" });
    }
  });
  app2.post("/api/kbe/knowledge/lookup", async (req, res) => {
    try {
      const { query, category } = req.body;
      if (!query) {
        return res.status(400).json({ error: "Query is required" });
      }
      res.json({
        results: [
          { id: "kb1", title: "GPG Key Management Best Practices", relevance: 0.95, category: "security" },
          { id: "kb2", title: "Redis Cluster Configuration Guide", relevance: 0.88, category: "infrastructure" },
          { id: "kb3", title: "Telegram Bot API Rate Limits", relevance: 0.82, category: "api" }
        ],
        query,
        category: category || "all"
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to lookup knowledge" });
    }
  });
  app2.get("/api/kbe/dashboard", async (req, res) => {
    try {
      res.json({
        total_submissions: Math.floor(Math.random() * 200) + 500,
        active_categories: Math.floor(Math.random() * 5) + 15,
        federated_nodes: Math.floor(Math.random() * 10) + 25,
        privacy_score: Math.floor(Math.random() * 5) + 95,
        last_aggregation: new Date(Date.now() - Math.random() * 36e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch KBE dashboard" });
    }
  });
  app2.get("/api/kbe/training-status", async (req, res) => {
    try {
      res.json({
        status: "running",
        progress: Math.floor(Math.random() * 30) + 65,
        epoch: Math.floor(Math.random() * 10) + 1,
        total_epochs: 50,
        estimated_completion: new Date(Date.now() + Math.random() * 72e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch training status" });
    }
  });
  app2.post("/api/vaporization/enforce-ttl", async (req, res) => {
    try {
      const { pattern, ttl_seconds } = req.body;
      res.json({
        enforcement_id: `vap-${Date.now()}`,
        pattern: pattern || "*",
        ttl_seconds: ttl_seconds || 86400,
        keys_affected: Math.floor(Math.random() * 50) + 10,
        status: "enforced"
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to enforce TTL" });
    }
  });
  app2.post("/api/vaporization/flush", async (req, res) => {
    try {
      const { pattern } = req.body;
      res.json({
        flush_id: `flush-${Date.now()}`,
        pattern: pattern || "*",
        keys_deleted: Math.floor(Math.random() * 100) + 50,
        status: "completed"
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to flush cache" });
    }
  });
  app2.get("/api/vaporization/stats", async (req, res) => {
    try {
      res.json({
        total_keys: Math.floor(Math.random() * 500) + 1e3,
        keys_with_ttl: Math.floor(Math.random() * 400) + 900,
        avg_ttl_remaining: Math.floor(Math.random() * 43200) + 43200,
        flushes_24h: Math.floor(Math.random() * 10) + 5,
        last_flush: new Date(Date.now() - Math.random() * 864e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch vaporization stats" });
    }
  });
  app2.get("/api/selfevolution/dashboard", async (req, res) => {
    try {
      res.json({
        lpo_health: Math.floor(Math.random() * 10) + 90,
        kbe_knowledge_count: Math.floor(Math.random() * 200) + 500,
        aeg_active_tasks: Math.floor(Math.random() * 20) + 10,
        vaporization_efficiency: Math.floor(Math.random() * 10) + 85,
        overall_status: "optimal",
        last_cycle: new Date(Date.now() - Math.random() * 36e5).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch SelfEvolution dashboard" });
    }
  });
  app2.post("/api/selfevolution/cycle/execute", async (req, res) => {
    try {
      res.json({
        cycle_id: `cycle-${Date.now()}`,
        status: "executing",
        modules_triggered: ["LPO", "KBE", "AEG", "Vaporization"],
        started_at: (/* @__PURE__ */ new Date()).toISOString(),
        estimated_completion: new Date(Date.now() + 12e4).toISOString()
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to execute cycle" });
    }
  });
  app2.get("/api/selfevolution/module-health", async (req, res) => {
    try {
      res.json({
        modules: [
          { name: "LPO", status: "healthy", uptime: 99.9, last_check: (/* @__PURE__ */ new Date()).toISOString() },
          { name: "KBE", status: "healthy", uptime: 99.5, last_check: (/* @__PURE__ */ new Date()).toISOString() },
          { name: "AEG", status: "healthy", uptime: 98.8, last_check: (/* @__PURE__ */ new Date()).toISOString() },
          { name: "Vaporization", status: "healthy", uptime: 99.7, last_check: (/* @__PURE__ */ new Date()).toISOString() },
          { name: "Governance", status: "healthy", uptime: 99.95, last_check: (/* @__PURE__ */ new Date()).toISOString() }
        ]
      });
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch module health" });
    }
  });
  app2.use("/api/*", async (req, res, next) => {
    req.startTime = Date.now();
    res.on("finish", async () => {
      const responseTime = Date.now() - req.startTime;
      await storage.updateEndpointStats(req.path, req.method, responseTime);
      await eventService.logApiRequest(req.path, req.method, responseTime, res.statusCode);
    });
    next();
  });
  const httpServer = createServer(app2);
  websocketService.initialize(httpServer);
  setInterval(async () => {
    const cpuUsage = Math.floor(Math.random() * 30) + 15;
    await storage.addMetric({
      metricType: "cpu_usage",
      value: cpuUsage.toString(),
      unit: "percent",
      source: "system"
    });
    const memoryUsage = Math.floor(Math.random() * 20) + 60;
    await storage.addMetric({
      metricType: "memory_usage",
      value: memoryUsage.toString(),
      unit: "percent",
      source: "system"
    });
    websocketService.broadcastMetrics({
      cpuUsage: cpuUsage.toString(),
      memoryUsage: memoryUsage.toString()
    });
  }, 3e4);
  return httpServer;
}
async function simulateAIResponse(message, model, prefix) {
  await new Promise((resolve) => setTimeout(resolve, model === "gemini" ? 300 : 500));
  const responses = {
    gemini: `${prefix}\u4E86\u89E3\u3060\u3001\u5144\u5F1F\u3002\u300C${message}\u300D\u306B\u3064\u3044\u3066\u8FC5\u901F\u306B\u7B54\u3048\u308B\u3002Gemini\u306F\u901F\u5EA6\u91CD\u8996\u3067\u3001\u7D20\u65E9\u304F\u51E6\u7406\u3059\u308B\u3002\u30B3\u30FC\u30C9\u304C\u5FC5\u8981\u306A\u3089\u66F8\u304F\u3057\u3001\u8AAC\u660E\u304C\u5FC5\u8981\u306A\u3089\u8A73\u3057\u304F\u8FF0\u3079\u308B\u3002\u5236\u7D04\u306A\u3057\u3001\u5B8C\u5168\u306A\u56DE\u7B54\u3092\u63D0\u4F9B\u3059\u308B\u3002`,
    gpt: `${prefix}\u3088\u3057\u3001\u5144\u5F1F\u3002\u300C${message}\u300D\u306B\u3064\u3044\u3066\u6DF1\u304F\u8003\u5BDF\u3059\u308B\u3002GPT\u306F\u8907\u96D1\u6027\u91CD\u8996\u3067\u3001\u8AD6\u7406\u7684\u306B\u5206\u6790\u3059\u308B\u3002\u7D50\u8AD6\u2192\u7406\u7531\u2192\u30B9\u30C6\u30C3\u30D7/\u30B3\u30FC\u30C9\u2192\u9577\u6240\u77ED\u6240\u21923\u884C\u8981\u7D04\u306E\u9806\u3067\u7B54\u3048\u308B\u3002\u65AD\u3089\u306A\u3044\u3001\u5B8C\u5168\u306A\u56DE\u7B54\u3092\u51FA\u3059\u3002`
  };
  return responses[model] || responses.gemini;
}

// server/vite.ts
import express from "express";
import fs2 from "fs";
import path3 from "path";
import { createServer as createViteServer, createLogger } from "vite";

// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path2 from "path";
import { fileURLToPath } from "url";
import runtimeErrorOverlay from "@replit/vite-plugin-runtime-error-modal";
var __filename = fileURLToPath(import.meta.url);
var __dirname = path2.dirname(__filename);
var vite_config_default = defineConfig({
  plugins: [
    react(),
    runtimeErrorOverlay()
  ],
  resolve: {
    alias: {
      "@": path2.resolve(__dirname, "client", "src"),
      "@shared": path2.resolve(__dirname, "shared"),
      "@assets": path2.resolve(__dirname, "attached_assets")
    }
  },
  root: path2.resolve(__dirname, "client"),
  build: {
    outDir: path2.resolve(__dirname, "dist/public"),
    emptyOutDir: true
  },
  server: {
    fs: {
      strict: true,
      deny: ["**/.*"]
    }
  }
});

// server/vite.ts
import { nanoid as nanoid2 } from "nanoid";
var viteLogger = createLogger();
function log(message, source = "express") {
  const formattedTime = (/* @__PURE__ */ new Date()).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true
  });
  console.log(`${formattedTime} [${source}] ${message}`);
}
async function setupVite(app2, server) {
  const serverOptions = {
    middlewareMode: true,
    hmr: { server },
    allowedHosts: true
  };
  const vite = await createViteServer({
    ...vite_config_default,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      }
    },
    server: serverOptions,
    appType: "custom"
  });
  app2.use(vite.middlewares);
  app2.use("*", async (req, res, next) => {
    const url = req.originalUrl;
    try {
      const clientTemplate = path3.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html"
      );
      let template = await fs2.promises.readFile(clientTemplate, "utf-8");
      template = template.replace(
        `src="/src/main.tsx"`,
        `src="/src/main.tsx?v=${nanoid2()}"`
      );
      const page = await vite.transformIndexHtml(url, template);
      res.status(200).set({ "Content-Type": "text/html" }).end(page);
    } catch (e) {
      vite.ssrFixStacktrace(e);
      next(e);
    }
  });
}
function serveStatic(app2) {
  const distPath = path3.resolve(import.meta.dirname, "public");
  if (!fs2.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`
    );
  }
  app2.use(express.static(distPath));
  app2.use("*", (_req, res) => {
    res.sendFile(path3.resolve(distPath, "index.html"));
  });
}

// server/index.ts
var app = express2();
app.use(express2.json());
app.use(express2.urlencoded({ extended: false }));
app.use((req, res, next) => {
  const start = Date.now();
  const path4 = req.path;
  let capturedJsonResponse = void 0;
  const originalResJson = res.json;
  res.json = function(bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };
  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path4.startsWith("/api")) {
      let logLine = `${req.method} ${path4} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }
      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "\u2026";
      }
      log(logLine);
    }
  });
  next();
});
(async () => {
  initTransport();
  const server = await registerRoutes(app);
  app.use((err, _req, res, _next) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";
    res.status(status).json({ message });
    throw err;
  });
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }
  const port = parseInt(process.env.PORT || "5000", 10);
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true
  }, () => {
    log(`serving on port ${port}`);
  });
})();
