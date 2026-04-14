/**
 * E2E: 稼働確認用。サーバー起動後に GET /api/health で健全性を確認する。
 */

import { test, expect } from "@playwright/test";

test("GET /api/health returns healthy", async ({ request }) => {
  const res = await request.get("/api/health");
  expect(res.ok()).toBe(true);
  const body = await res.json();
  expect(body.status).toBe("healthy");
  expect(body.timestamp).toBeDefined();
  expect(body.pythonWorker).toBeDefined();
});
