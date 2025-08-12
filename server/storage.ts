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
  type InsertApiEndpoint
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
}

export class MemStorage implements IStorage {
  private users: Map<string, User> = new Map();
  private transactions: Map<string, Transaction> = new Map();
  private events: Map<string, Event> = new Map();
  private modules: Map<string, Module> = new Map();
  private metrics: Map<string, SystemMetrics> = new Map();
  private apiEndpoints: Map<string, ApiEndpoint> = new Map();

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
}

export const storage = new MemStorage();
