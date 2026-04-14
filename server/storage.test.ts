import { describe, it, expect, beforeEach } from "vitest";
import { MemStorage } from "./storage";

describe("MemStorage", () => {
  let storage: MemStorage;

  beforeEach(() => {
    storage = new MemStorage();
  });

  it("createUser returns user with id and role", async () => {
    const user = await storage.createUser({
      telegramId: "tg-123",
      username: "test",
      role: "user",
    });
    expect(user.id).toBeDefined();
    expect(user.telegramId).toBe("tg-123");
    expect(user.role).toBe("user");
  });

  it("getUser returns undefined for unknown id", async () => {
    const got = await storage.getUser("unknown");
    expect(got).toBeUndefined();
  });

  it("getUser returns user after createUser", async () => {
    const created = await storage.createUser({
      telegramId: "tg-456",
      username: "u2",
      role: "user",
    });
    const got = await storage.getUser(created.id);
    expect(got?.id).toBe(created.id);
    expect(got?.telegramId).toBe("tg-456");
  });

  it("getLatestMetrics returns metric when present", async () => {
    const m = await storage.getLatestMetrics("cpu_usage");
    expect(m).toBeDefined();
    expect(m?.metricType).toBe("cpu_usage");
  });
});
