// server/routes/aegis.ts - Fastify plugin (2026 Refactor)
import type { FastifyInstance } from "fastify";
import { aegisEncryptSchema, aegisDecryptSchema, aegisSignSchema, aegisVerifySchema } from "@shared/requestSchemas";
import { getTransportRouter } from "../core/transport/bootstrap";
import { aegisClient } from "../crypto/aegisClient";
import { storage } from "../storage";
import { nanoid } from "nanoid";

export function registerAegisRoutes(fastify: FastifyInstance): void {
  fastify.post("/api/aegis/encrypt", async (request, reply) => {
    try {
      const body = aegisEncryptSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { recipient, data, policyId } = body.data;
      const requestId = nanoid();
      const result = await aegisClient.encrypt({ recipient, data, policyId: policyId ?? "modern-strong" });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "encrypt", policyId, requestId, ok: true },
        userId: "system",
      });
      return reply.send({ ...result, requestId });
    } catch (error) {
      console.error("Aegis encrypt error:", error);
      return reply.status(500).send({ error: "Encryption failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.post("/api/aegis/decrypt", async (request, reply) => {
    try {
      const body = aegisDecryptSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { blob, policyId } = body.data;
      const requestId = nanoid();
      const result = await aegisClient.decrypt({ blob, policyId: policyId ?? "modern-strong" });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "decrypt", policyId, requestId, ok: true },
        userId: "system",
      });
      return reply.send({ ...result, requestId });
    } catch (error) {
      console.error("Aegis decrypt error:", error);
      return reply.status(500).send({ error: "Decryption failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.post("/api/aegis/sign", async (request, reply) => {
    try {
      const body = aegisSignSchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { data, ctxLabels } = body.data;
      const requestId = nanoid();
      const contextLabels = {
        "aegis.app": "libral-core@1.0",
        "aegis.ts": Date.now().toString(),
        "aegis.policy": "modern-strong",
        ...ctxLabels,
      };
      const result = await aegisClient.sign({ data, ctxLabels: contextLabels });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "sign", contextLabels, requestId, ok: true },
        userId: "system",
      });
      return reply.send({ ...result, requestId });
    } catch (error) {
      console.error("Aegis sign error:", error);
      return reply.status(500).send({ error: "Signing failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.post("/api/aegis/verify", async (request, reply) => {
    try {
      const body = aegisVerifySchema.safeParse(request.body);
      if (!body.success) {
        return reply.status(400).send({ error: "Invalid body", details: body.error.flatten() });
      }
      const { data, sig, requireContext } = body.data;
      const requestId = nanoid();
      const result = await aegisClient.verify({ data, sig, requireContext: requireContext ?? true });
      await storage.createEvent({
        type: "crypto_operation",
        source: "aegis-pgp",
        data: { operation: "verify", requireContext, requestId, ok: result.ok },
        userId: "system",
      });
      return reply.send({ ...result, requestId });
    } catch (error) {
      console.error("Aegis verify error:", error);
      return reply.status(500).send({ error: "Verification failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.post("/api/aegis/send", async (request, reply) => {
    try {
      const body = (request.body as any) ?? {};
      const {
        to,
        data,
        recipient,
        subject,
        policyId = "modern-strong",
        sensitivity = "med",
        tenantId = "default",
        usecase = "secure-mail",
      } = body;
      if (!to || !data || !recipient) {
        return reply.status(400).send({ error: "Destination, data, and recipient are required" });
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
          idempotency_key: requestId,
        },
      });
      await storage.createEvent({
        type: "secure_send",
        source: "aegis-pgp",
        data: { operation: "encrypt_and_send", policyId, transport: sendResult.transport, requestId, ok: sendResult.ok },
        userId: "system",
      });
      return reply.send({
        ok: sendResult.ok,
        transport: sendResult.transport,
        encrypted: true,
        policyId,
        requestId,
      });
    } catch (error) {
      console.error("Aegis secure send error:", error);
      return reply.status(500).send({ error: "Secure send failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.get("/api/aegis/wkd-path", async (request, reply) => {
    try {
      const email = (request.query as any)?.email as string;
      if (!email) {
        return reply.status(400).send({ error: "Email parameter is required" });
      }
      const result = await aegisClient.getWkdPath({ email });
      return reply.send(result);
    } catch (error) {
      console.error("WKD path error:", error);
      return reply.status(500).send({ error: "WKD path generation failed", details: error instanceof Error ? error.message : String(error) });
    }
  });

  fastify.post("/api/aegis/inspect", async (request, reply) => {
    try {
      const { blob } = (request.body as any) ?? {};
      if (!blob) {
        return reply.status(400).send({ error: "Blob is required" });
      }
      const result = await aegisClient.inspect({ blob });
      return reply.send(result);
    } catch (error) {
      console.error("Aegis inspect error:", error);
      return reply.status(500).send({ error: "Inspection failed", details: error instanceof Error ? error.message : String(error) });
    }
  });
}