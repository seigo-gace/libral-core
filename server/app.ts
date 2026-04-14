/**
 * Libral Core - Fastify App Builder (テスト・稼働両用)
 * buildApp() を export し、index.ts と API テストの両方で利用する。
 */

import Fastify, { type FastifyInstance } from "fastify";
import fastifyCors from "@fastify/cors";
import fastifyFormbody from "@fastify/formbody";
import fastifyHelmet from "@fastify/helmet";
import fastifyRateLimit from "@fastify/rate-limit";
import fastifyMiddie from "@fastify/middie";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { initTransport } from "./core/transport/bootstrap";

/** 本番では CORS_ORIGINS にカンマ区切りでオリジン指定。未設定・development は true（全許可） */
function getCorsOrigin(): boolean | string | string[] {
  const raw = process.env.CORS_ORIGINS;
  if (process.env.NODE_ENV !== "production" || !raw?.trim()) return true;
  return raw.split(",").map((o) => o.trim()).filter(Boolean);
}

export async function buildApp(): Promise<FastifyInstance> {
  const app = Fastify({
    logger: process.env.NODE_ENV === "development",
    requestIdHeader: "x-request-id",
    requestIdLogLabel: "reqId",
  });

  await app.register(fastifyHelmet, {
    contentSecurityPolicy: process.env.NODE_ENV === "production",
    global: true,
  });
  await app.register(fastifyCors, { origin: getCorsOrigin() });
  await app.register(fastifyRateLimit, {
    max: parseInt(process.env.RATE_LIMIT_MAX ?? "100", 10),
    timeWindow: process.env.RATE_LIMIT_WINDOW ?? "1 minute",
  });
  await app.register(fastifyFormbody);
  await app.register(fastifyMiddie);

  app.addHook("onRequest", (request, _reply, done) => {
    (request as any).startTime = Date.now();
    done();
  });
  app.addHook("onResponse", (request, reply, done) => {
    const path = request.url.split("?")[0];
    if (path.startsWith("/api")) {
      const duration = Date.now() - (request as any).startTime;
      let logLine = `${request.method} ${path} ${reply.statusCode} in ${duration}ms`;
      if (logLine.length > 80) logLine = logLine.slice(0, 79) + "…";
      log(logLine);
    }
    done();
  });

  initTransport();
  await registerRoutes(app);

  app.setErrorHandler((err, request, reply) => {
    const status = (err as any).statusCode ?? (err as any).status ?? 500;
    const message = err.message ?? "Internal Server Error";
    reply.status(status).send({ message });
  });

  if (process.env.NODE_ENV === "development") {
    await setupVite(app);
  } else {
    await serveStatic(app);
  }

  return app;
}
