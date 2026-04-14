// server/standalone/server.ts
import express from "express";
import { initTransport, getTransportRouter } from "../core/transport/bootstrap";
import { aegisClient } from "../crypto/aegisClient";

const app = express();
app.use(express.json({ limit: '50mb' }));

// CORS for development
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Initialize transport system
initTransport();
const transportRouter = getTransportRouter();

// Core transport endpoint
app.post("/v1/send", async (req, res) => {
  try {
    const result = await transportRouter.sendWithFailover(req.body);
    if (result.ok) {
      return res.json(result);
    }
    return res.status(202).json(result); // Queued for retry
  } catch (e: any) {
    console.error("Send failed:", e);
    return res.status(500).json({ ok: false, error: String(e) });
  }
});

// Aegis-PGP proxy endpoints
app.post("/v1/encrypt", async (req, res) => {
  try {
    const result = await aegisClient.encrypt(req.body);
    res.json(result);
  } catch (e: any) {
    console.error("Encrypt failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

app.post("/v1/decrypt", async (req, res) => {
  try {
    const result = await aegisClient.decrypt(req.body);
    res.json(result);
  } catch (e: any) {
    console.error("Decrypt failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

app.post("/v1/sign", async (req, res) => {
  try {
    const result = await aegisClient.sign(req.body);
    res.json(result);
  } catch (e: any) {
    console.error("Sign failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

app.post("/v1/verify", async (req, res) => {
  try {
    const result = await aegisClient.verify(req.body);
    res.json(result);
  } catch (e: any) {
    console.error("Verify failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

app.get("/v1/wkd-path", async (req, res) => {
  try {
    const email = req.query.email as string;
    if (!email) {
      return res.status(400).json({ error: "email parameter required" });
    }
    const result = await aegisClient.getWkdPath({ email });
    res.json(result);
  } catch (e: any) {
    console.error("WKD path failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

app.post("/v1/inspect", async (req, res) => {
  try {
    const result = await aegisClient.inspect(req.body);
    res.json(result);
  } catch (e: any) {
    console.error("Inspect failed:", e);
    res.status(500).json({ error: String(e) });
  }
});

// Health check
app.get("/v1/health", (_req, res) => {
  res.json({ 
    ok: true, 
    ts: Date.now(),
    service: "libral-transport-core",
    version: "1.0.0",
    uptime: process.uptime()
  });
});

// API info
app.get("/v1/info", (_req, res) => {
  res.json({
    service: "Libral Transport Core API",
    version: "1.0.0",
    endpoints: {
      transport: ["/v1/send"],
      crypto: ["/v1/encrypt", "/v1/decrypt", "/v1/sign", "/v1/verify"],
      utils: ["/v1/wkd-path", "/v1/inspect"],
      system: ["/v1/health", "/v1/info"]
    },
    policies: ["modern-strong", "compat", "backup-longterm"],
    transports: ["telegram", "email", "webhook"]
  });
});

const port = parseInt(process.env.PORT || "8787", 10);
app.listen(port, "0.0.0.0", () => {
  console.log(`[libral-transport-core] API server listening on port ${port}`);
  console.log(`Health check: http://localhost:${port}/v1/health`);
  console.log(`API info: http://localhost:${port}/v1/info`);
});