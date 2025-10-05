import { 
  type User, 
  type InsertUser,
  type Transaction,
  type InsertTransaction,
  type Event,
  type InsertEvent,
  type Module,
  type InsertModule,
  type SystemMetrics,
  type InsertSystemMetrics,
  type ApiEndpoint,
  type InsertApiEndpoint,
  type Stamp,
  type InsertStamp,
  type Asset,
  type InsertAsset,
  type StampCreationSession,
  type InsertStampCreationSession
} from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // User management
  getUser(id: string): Promise<User | undefined>;
  getUserByTelegramId(telegramId: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  updateUser(id: string, updates: Partial<User>): Promise<User | undefined>;
  getActiveUsers(): Promise<User[]>;
  
  // Transaction management
  createTransaction(transaction: InsertTransaction): Promise<Transaction>;
  getTransaction(id: string): Promise<Transaction | undefined>;
  getRecentTransactions(limit?: number): Promise<Transaction[]>;
  updateTransactionStatus(id: string, status: string): Promise<Transaction | undefined>;
  
  // Event management
  createEvent(event: InsertEvent): Promise<Event>;
  getRecentEvents(limit?: number): Promise<Event[]>;
  getEventsByType(type: string, limit?: number): Promise<Event[]>;
  
  // Module management
  upsertModule(module: InsertModule): Promise<Module>;
  getModule(id: string): Promise<Module | undefined>;
  getAllModules(): Promise<Module[]>;
  updateModuleStatus(id: string, status: string): Promise<Module | undefined>;
  
  // System metrics
  addMetric(metric: InsertSystemMetrics): Promise<SystemMetrics>;
  getLatestMetrics(metricType: string): Promise<SystemMetrics | undefined>;
  getMetricsHistory(metricType: string, limit?: number): Promise<SystemMetrics[]>;
  
  // API endpoints
  upsertApiEndpoint(endpoint: InsertApiEndpoint): Promise<ApiEndpoint>;
  getAllApiEndpoints(): Promise<ApiEndpoint[]>;
  updateEndpointStats(path: string, method: string, responseTime: number): Promise<void>;
  
  // Stamp creation
  createStamp(stamp: InsertStamp): Promise<Stamp>;
  getStamp(id: string): Promise<Stamp | undefined>;
  getStampsByUserId(userId: string): Promise<Stamp[]>;
  updateStampStatus(id: string, status: string, fileUrl?: string): Promise<Stamp | undefined>;
  
  // Assets
  createAsset(asset: InsertAsset): Promise<Asset>;
  getAssetsByType(type: string): Promise<Asset[]>;
  getAsset(id: string): Promise<Asset | undefined>;
  
  // Stamp creation sessions
  createSession(session: InsertStampCreationSession): Promise<StampCreationSession>;
  getSession(id: string): Promise<StampCreationSession | undefined>;
  updateSession(id: string, sessionData: any): Promise<StampCreationSession | undefined>;
  deleteExpiredSessions(): Promise<void>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User> = new Map();
  private transactions: Map<string, Transaction> = new Map();
  private events: Map<string, Event> = new Map();
  private modules: Map<string, Module> = new Map();
  private metrics: Map<string, SystemMetrics> = new Map();
  private apiEndpoints: Map<string, ApiEndpoint> = new Map();
  private stamps: Map<string, Stamp> = new Map();
  private assets: Map<string, Asset> = new Map();
  private sessions: Map<string, StampCreationSession> = new Map();

  constructor() {
    this.initializeDefaultData();
  }

  private initializeDefaultData() {
    // Initialize default modules
    const defaultModules: InsertModule[] = [
      {
        id: "gateway",
        name: "通信ゲートウェイ",
        version: "v1.2.4",
        status: "active",
        port: 8001,
        endpoint: "/api/v1/gateway",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "auth",
        name: "ユーザー管理",
        version: "v2.1.0",
        status: "active",
        port: 8002,
        endpoint: "/api/v1/auth",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "events",
        name: "イベント管理",
        version: "v1.8.2",
        status: "high_load",
        port: 8003,
        endpoint: "/api/v1/events",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "payments",
        name: "決済管理",
        version: "v1.5.1",
        status: "active",
        port: 8004,
        endpoint: "/api/v1/payments",
        healthCheckUrl: "/health",
        metadata: {}
      },
      {
        id: "api-hub",
        name: "APIハブ",
        version: "v3.0.1",
        status: "active",
        port: 8000,
        endpoint: "/api/v1/hub",
        healthCheckUrl: "/health",
        metadata: {}
      }
    ];

    defaultModules.forEach(module => {
      this.modules.set(module.id, {
        ...module,
        lastHealthCheck: new Date()
      });
    });

    // Initialize system metrics
    const now = new Date();
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

    // Initialize default assets
    this.initializeDefaultAssets();
  }

  private initializeDefaultAssets() {
    const defaultAssets: InsertAsset[] = [
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
        metadata: { duration: 1000, easing: "bounce" }
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
        metadata: { particles: 100, duration: 2000 }
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

    defaultAssets.forEach(asset => {
      this.assets.set(asset.id, {
        ...asset,
        creatorId: null,
        currency: asset.currency || "JPY",
        price: asset.price || "0",
        previewUrl: asset.previewUrl || null,
        isActive: true,
        createdAt: new Date()
      });
    });
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByTelegramId(telegramId: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.telegramId === telegramId);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = {
      ...insertUser,
      id,
      role: insertUser.role || "user",
      createdAt: new Date(),
      lastSeenAt: new Date()
    };
    this.users.set(id, user);
    return user;
  }

  async updateUser(id: string, updates: Partial<User>): Promise<User | undefined> {
    const user = this.users.get(id);
    if (!user) return undefined;
    
    const updatedUser = { ...user, ...updates };
    this.users.set(id, updatedUser);
    return updatedUser;
  }

  async getActiveUsers(): Promise<User[]> {
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    return Array.from(this.users.values()).filter(
      user => user.lastSeenAt && user.lastSeenAt > oneDayAgo
    );
  }

  async createTransaction(insertTransaction: InsertTransaction): Promise<Transaction> {
    const id = randomUUID();
    const transaction: Transaction = {
      ...insertTransaction,
      id,
      status: insertTransaction.status || "pending",
      currency: insertTransaction.currency || "JPY",
      createdAt: new Date(),
      completedAt: null
    };
    this.transactions.set(id, transaction);
    return transaction;
  }

  async getTransaction(id: string): Promise<Transaction | undefined> {
    return this.transactions.get(id);
  }

  async getRecentTransactions(limit: number = 10): Promise<Transaction[]> {
    return Array.from(this.transactions.values())
      .sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0))
      .slice(0, limit);
  }

  async updateTransactionStatus(id: string, status: string): Promise<Transaction | undefined> {
    const transaction = this.transactions.get(id);
    if (!transaction) return undefined;
    
    const updatedTransaction = { 
      ...transaction, 
      status,
      completedAt: status === 'completed' ? new Date() : transaction.completedAt
    };
    this.transactions.set(id, updatedTransaction);
    return updatedTransaction;
  }

  async createEvent(insertEvent: InsertEvent): Promise<Event> {
    const id = randomUUID();
    const event: Event = {
      ...insertEvent,
      id,
      data: insertEvent.data || {},
      level: insertEvent.level || "info",
      createdAt: new Date()
    };
    this.events.set(id, event);
    return event;
  }

  async getRecentEvents(limit: number = 20): Promise<Event[]> {
    return Array.from(this.events.values())
      .sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0))
      .slice(0, limit);
  }

  async getEventsByType(type: string, limit: number = 10): Promise<Event[]> {
    return Array.from(this.events.values())
      .filter(event => event.type === type)
      .sort((a, b) => (b.createdAt?.getTime() || 0) - (a.createdAt?.getTime() || 0))
      .slice(0, limit);
  }

  async upsertModule(insertModule: InsertModule): Promise<Module> {
    const module: Module = {
      ...insertModule,
      status: insertModule.status || "inactive",
      lastHealthCheck: new Date()
    };
    this.modules.set(insertModule.id, module);
    return module;
  }

  async getModule(id: string): Promise<Module | undefined> {
    return this.modules.get(id);
  }

  async getAllModules(): Promise<Module[]> {
    return Array.from(this.modules.values());
  }

  async updateModuleStatus(id: string, status: string): Promise<Module | undefined> {
    const module = this.modules.get(id);
    if (!module) return undefined;
    
    const updatedModule = { 
      ...module, 
      status,
      lastHealthCheck: new Date()
    };
    this.modules.set(id, updatedModule);
    return updatedModule;
  }

  async addMetric(insertMetric: InsertSystemMetrics): Promise<SystemMetrics> {
    const id = randomUUID();
    const metric: SystemMetrics = {
      ...insertMetric,
      id,
      timestamp: new Date()
    };
    this.metrics.set(`${insertMetric.metricType}-${Date.now()}`, metric);
    return metric;
  }

  async getLatestMetrics(metricType: string): Promise<SystemMetrics | undefined> {
    const metrics = Array.from(this.metrics.values())
      .filter(m => m.metricType === metricType)
      .sort((a, b) => (b.timestamp?.getTime() || 0) - (a.timestamp?.getTime() || 0));
    
    return metrics[0];
  }

  async getMetricsHistory(metricType: string, limit: number = 10): Promise<SystemMetrics[]> {
    return Array.from(this.metrics.values())
      .filter(m => m.metricType === metricType)
      .sort((a, b) => (b.timestamp?.getTime() || 0) - (a.timestamp?.getTime() || 0))
      .slice(0, limit);
  }

  async upsertApiEndpoint(insertEndpoint: InsertApiEndpoint): Promise<ApiEndpoint> {
    const key = `${insertEndpoint.method}:${insertEndpoint.path}`;
    const existing = this.apiEndpoints.get(key);
    
    const endpoint: ApiEndpoint = {
      ...insertEndpoint,
      id: existing?.id || randomUUID(),
      requestCount: existing?.requestCount || 0,
      averageResponseTime: existing?.averageResponseTime || null,
      lastRequestAt: existing?.lastRequestAt || null
    };
    
    this.apiEndpoints.set(key, endpoint);
    return endpoint;
  }

  async getAllApiEndpoints(): Promise<ApiEndpoint[]> {
    return Array.from(this.apiEndpoints.values());
  }

  async updateEndpointStats(path: string, method: string, responseTime: number): Promise<void> {
    const key = `${method}:${path}`;
    const endpoint = this.apiEndpoints.get(key);
    
    if (endpoint) {
      const newCount = (endpoint.requestCount || 0) + 1;
      const currentAvg = parseFloat(endpoint.averageResponseTime || "0");
      const newAvg = ((currentAvg * (newCount - 1)) + responseTime) / newCount;
      
      const updatedEndpoint: ApiEndpoint = {
        ...endpoint,
        requestCount: newCount,
        averageResponseTime: newAvg.toFixed(2),
        lastRequestAt: new Date()
      };
      
      this.apiEndpoints.set(key, updatedEndpoint);
    }
  }

  // Stamp creation methods
  async createStamp(insertStamp: InsertStamp): Promise<Stamp> {
    const id = randomUUID();
    const stamp: Stamp = {
      ...insertStamp,
      id,
      status: insertStamp.status || "processing",
      createdAt: new Date(),
      completedAt: null
    };
    this.stamps.set(id, stamp);
    return stamp;
  }

  async getStamp(id: string): Promise<Stamp | undefined> {
    return this.stamps.get(id);
  }

  async getStampsByUserId(userId: string): Promise<Stamp[]> {
    return Array.from(this.stamps.values()).filter(stamp => stamp.userId === userId);
  }

  async updateStampStatus(id: string, status: string, fileUrl?: string): Promise<Stamp | undefined> {
    const stamp = this.stamps.get(id);
    if (!stamp) return undefined;

    const updatedStamp = {
      ...stamp,
      status,
      fileUrl: fileUrl || null,
      completedAt: status === 'completed' ? new Date() : stamp.completedAt
    };
    this.stamps.set(id, updatedStamp);
    return updatedStamp;
  }

  // Asset methods
  async createAsset(insertAsset: InsertAsset): Promise<Asset> {
    const asset: Asset = {
      ...insertAsset,
      currency: insertAsset.currency || "JPY",
      price: insertAsset.price || "0",
      previewUrl: insertAsset.previewUrl || null,
      isActive: insertAsset.isActive !== false,
      createdAt: new Date()
    };
    this.assets.set(insertAsset.id, asset);
    return asset;
  }

  async getAssetsByType(type: string): Promise<Asset[]> {
    return Array.from(this.assets.values()).filter(asset => asset.type === type && asset.isActive);
  }

  async getAsset(id: string): Promise<Asset | undefined> {
    return this.assets.get(id);
  }

  // Session methods
  async createSession(insertSession: InsertStampCreationSession): Promise<StampCreationSession> {
    const id = randomUUID();
    const session: StampCreationSession = {
      ...insertSession,
      id,
      sessionData: insertSession.sessionData || {},
      lastUpdated: new Date()
    };
    this.sessions.set(id, session);
    return session;
  }

  async getSession(id: string): Promise<StampCreationSession | undefined> {
    return this.sessions.get(id);
  }

  async updateSession(id: string, sessionData: any): Promise<StampCreationSession | undefined> {
    const session = this.sessions.get(id);
    if (!session) return undefined;

    const updatedSession = {
      ...session,
      sessionData,
      lastUpdated: new Date()
    };
    this.sessions.set(id, updatedSession);
    return updatedSession;
  }

  async deleteExpiredSessions(): Promise<void> {
    const now = new Date();
    Array.from(this.sessions.entries()).forEach(([id, session]) => {
      if (session.expiresAt < now) {
        this.sessions.delete(id);
      }
    });
  }
}

export const storage = new MemStorage();
