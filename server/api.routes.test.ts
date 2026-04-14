/**
 * API ルートの Vitest（AUDIT_AND_UPDATE_PROPOSAL 推奨）
 * buildApp を利用し、inject で GET /api/health と POST 不正 body → 400 を検証する。
 */

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { buildApp } from "./app";
import type { FastifyInstance } from "fastify";

describe("API routes", () => {
  let app: FastifyInstance;

  beforeAll(async () => {
    app = await buildApp();
  });

  afterAll(async () => {
    await app.close();
  });

  it("GET /api/health returns 200 and status healthy", async () => {
    const res = await app.inject({ method: "GET", url: "/api/health" });
    expect(res.statusCode).toBe(200);
    const body = JSON.parse(res.payload);
    expect(body.status).toBe("healthy");
    expect(body.timestamp).toBeDefined();
    expect(body.uptime).toBeDefined();
    expect(body.pythonWorker).toBeDefined();
    expect(typeof body.pythonWorker.status).toBe("string");
  });

  it("POST /api/kb/entries with invalid body returns 400", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/api/kb/entries",
      payload: { content: "x", language: "en" },
      headers: { "content-type": "application/json" },
    });
    expect(res.statusCode).toBe(400);
    const body = JSON.parse(res.payload);
    expect(body.error).toBeDefined();
  });

  it("POST /api/kbe/knowledge/submit with empty category returns 400", async () => {
    const res = await app.inject({
      method: "POST",
      url: "/api/kbe/knowledge/submit",
      payload: { category: "", content: "test" },
      headers: { "content-type": "application/json" },
    });
    expect(res.statusCode).toBe(400);
  });
});
