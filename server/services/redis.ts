/**
 * Redis - 最適案: REDIS_URL 設定時は実接続、未設定時はインメモリモック
 * 本番では REDIS_URL を設定して実 Redis を使用すること。
 */

import { createClient, type RedisClientType } from "redis";

const REDIS_URL = process.env.REDIS_URL ?? "";

type RedisLike = {
  connect: () => Promise<void>;
  disconnect: () => Promise<void>;
  publish: (channel: string, message: string) => Promise<void>;
  subscribe: (channel: string, callback: (message: string) => void) => Promise<void>;
  unsubscribe: (channel: string) => Promise<void>;
  set: (key: string, value: string, options?: { EX?: number }) => Promise<void>;
  get: (key: string) => Promise<string | null>;
  expire?: (key: string, seconds: number) => Promise<void>;
  getStats?: () => Record<string, unknown>;
};

function createMockRedisClient(): RedisLike {
  const subscribers = new Map<string, ((message: string) => void)[]>();

  return {
    connect: async () => {
      console.log("[Redis] Using in-memory mock (REDIS_URL not set)");
    },
    disconnect: async () => {},
    publish: async (channel: string, message: string) => {
      const cbs = subscribers.get(channel) ?? [];
      cbs.forEach((cb) => {
        try {
          cb(message);
        } catch (e) {
          console.error("[Redis] Mock subscriber error:", e);
        }
      });
    },
    subscribe: async (channel: string, callback: (message: string) => void) => {
      if (!subscribers.has(channel)) subscribers.set(channel, []);
      subscribers.get(channel)!.push(callback);
    },
    unsubscribe: async (channel: string) => {
      subscribers.delete(channel);
    },
    set: async (_key: string, _value: string) => {},
    get: async () => null,
    getStats: () => ({
      memoryUsed: "0",
      connectedClients: 0,
      pubsubChannels: subscribers.size,
      hitRatio: "0%",
      mode: "mock",
    }),
  };
}

async function createRealRedisClients(): Promise<{
  client: RedisLike;
  publisher: RedisLike;
  subscriber: RedisLike;
}> {
  const client = createClient({ url: REDIS_URL }) as RedisClientType & RedisLike;
  const subscriberClient = client.duplicate() as RedisClientType & RedisLike;

  client.on("error", (err) => console.error("[Redis] Client error:", err));
  subscriberClient.on("error", (err) => console.error("[Redis] Subscriber error:", err));

  await Promise.all([client.connect(), subscriberClient.connect()]);
  console.log("[Redis] Connected to", REDIS_URL.replace(/:[^:@]+@/, ":****@"));

  const adapter: RedisLike = {
    connect: async () => {},
    disconnect: async () => {
      await client.quit();
      await subscriberClient.quit();
    },
    publish: (channel: string, message: string) => client.publish(channel, message),
    subscribe: async (channel: string, callback: (message: string) => void) => {
      await subscriberClient.subscribe(channel, (msg: string, _ch: string) => callback(msg));
    },
    unsubscribe: async (channel: string) => {
      await subscriberClient.unsubscribe(channel);
    },
    set: async (key: string, value: string, options?: { EX?: number }) => {
      await client.set(key, value, options);
    },
    get: (key: string) => client.get(key),
  };

  const getStats = (): Record<string, unknown> => ({
    mode: "real",
    memoryUsed: "-",
    connectedClients: "-",
    pubsubChannels: "-",
    hitRatio: "-",
    url: REDIS_URL.replace(/:[^:@]+@/, ":****@"),
  });

  return {
    client: { ...adapter, getStats },
    publisher: adapter,
    subscriber: adapter,
  };
}

class RedisService {
  private client!: RedisLike;
  private publisher!: RedisLike;
  private subscriber!: RedisLike;
  private initialized = false;

  private async ensureInit() {
    if (this.initialized) return;
    if (REDIS_URL.trim()) {
      const real = await createRealRedisClients();
      this.client = real.client;
      this.publisher = real.publisher;
      this.subscriber = real.subscriber;
    } else {
      const mock = createMockRedisClient();
      this.client = mock;
      this.publisher = mock;
      this.subscriber = mock;
    }
    this.initialized = true;
  }

  async connect() {
    await this.ensureInit();
    await this.client.connect();
  }

  async disconnect() {
    if (this.client?.disconnect) await this.client.disconnect();
  }

  async publish(channel: string, data: unknown) {
    await this.ensureInit();
    const message = typeof data === "string" ? data : JSON.stringify(data);
    await this.publisher.publish(channel, message);
  }

  async subscribe(channel: string, callback: (data: unknown) => void) {
    await this.ensureInit();
    await this.subscriber.subscribe(channel, (message: string) => {
      try {
        const data = JSON.parse(message) as unknown;
        callback(data);
      } catch {
        callback(message);
      }
    });
  }

  async unsubscribe(channel: string) {
    await this.subscriber.unsubscribe(channel);
  }

  async set(key: string, value: unknown, ttl?: number) {
    await this.ensureInit();
    const stringValue = typeof value === "string" ? value : JSON.stringify(value);
    if (ttl) {
      await this.client.set(key, stringValue, { EX: ttl });
    } else {
      await this.client.set(key, stringValue);
    }
  }

  async get(key: string): Promise<unknown> {
    await this.ensureInit();
    const value = await this.client.get(key);
    if (value == null) return null;
    try {
      return JSON.parse(value) as unknown;
    } catch {
      return value;
    }
  }

  getStats(): Record<string, unknown> {
    if (!this.initialized || !this.client.getStats) {
      return { mode: "mock", connectedClients: 0 };
    }
    return this.client.getStats();
  }
}

export const redisService = new RedisService();
