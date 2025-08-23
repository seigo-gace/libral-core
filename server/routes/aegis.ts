// server/routes/aegis.ts
import type { Express } from "express";
import { getTransportRouter } from "../core/transport/bootstrap";
import { aegisClient } from "../crypto/aegisClient";
import { storage } from "../storage";
import { nanoid } from "nanoid";

export function registerAegisRoutes(app: Express) {
  // Aegis-PGP Encryption endpoint
  app.post("/api/aegis/encrypt", async (req, res) => {
    try {
      const { recipient, data, policyId = "modern-strong" } = req.body;
      
      if (!recipient || !data) {
        return res.status(400).json({ error: "Recipient and data are required" });
      }

      const requestId = nanoid();
      const result = await aegisClient.encrypt({ recipient, data, policyId });
      
      // Log audit event
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

  // Aegis-PGP Decryption endpoint
  app.post("/api/aegis/decrypt", async (req, res) => {
    try {
      const { blob, policyId = "modern-strong" } = req.body;
      
      if (!blob) {
        return res.status(400).json({ error: "Blob is required" });
      }

      const requestId = nanoid();
      const result = await aegisClient.decrypt({ blob, policyId });
      
      // Log audit event
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

  // Aegis-PGP Signing endpoint
  app.post("/api/aegis/sign", async (req, res) => {
    try {
      const { data, ctxLabels } = req.body;
      
      if (!data) {
        return res.status(400).json({ error: "Data is required" });
      }

      const requestId = nanoid();
      
      // Add default context labels
      const contextLabels = {
        "aegis.app": "libral-core@1.0",
        "aegis.ts": Date.now().toString(),
        "aegis.policy": "modern-strong",
        ...ctxLabels
      };

      const result = await aegisClient.sign({ data, ctxLabels: contextLabels });
      
      // Log audit event
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

  // Aegis-PGP Verification endpoint
  app.post("/api/aegis/verify", async (req, res) => {
    try {
      const { data, sig, requireContext = true } = req.body;
      
      if (!data || !sig) {
        return res.status(400).json({ error: "Data and signature are required" });
      }

      const requestId = nanoid();
      const result = await aegisClient.verify({ data, sig, requireContext });
      
      // Log audit event
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

  // Secure send with encryption
  app.post("/api/aegis/send", async (req, res) => {
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
      
      // First encrypt the data
      const encrypted = await aegisClient.encrypt({ recipient, data, policyId });
      
      // Then send via transport layer
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

      // Log combined operation
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

  // WKD path utility
  app.get("/api/aegis/wkd-path", async (req, res) => {
    try {
      const email = req.query.email as string;
      
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

  // PGP blob inspection
  app.post("/api/aegis/inspect", async (req, res) => {
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