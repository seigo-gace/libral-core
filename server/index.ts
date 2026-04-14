/**
 * Libral Core - Fastify Server Entry Point (2026 Refactor)
 * buildApp は server/app.ts で定義（テストからも利用可能）。
 */

import { buildApp } from "./app";
import { log } from "./vite";
import { websocketService } from "./services/websocket";

const PORT = parseInt(process.env.PORT ?? "5000", 10);

async function initializeAiModules() {
  try {
    const [{ kbSystem }, { aiBridge }, { evaluator }, { ossManager }, { embeddingLayer }, { aiRouter }] =
      await Promise.all([
        import("./modules/kb-system"),
        import("./core/ai-bridge"),
        import("./modules/evaluator"),
        import("./modules/oss-manager"),
        import("./modules/embedding"),
        import("./core/ai-router"),
      ]);

    await Promise.all([
      kbSystem.initialize(),
      aiBridge.initialize(),
      evaluator.initialize(),
      ossManager.initialize(),
      embeddingLayer.initialize(),
      aiRouter.initialize(),
    ]);

    console.log("[LIBRAL-CORE] All AI modules initialized successfully");
  } catch (error) {
    console.error("[LIBRAL-CORE] AI modules initialization failed:", error);
    console.log("[LIBRAL-CORE] Continuing without AI modules...");
  }
}

(async () => {
  const app = await buildApp();

  try {
    await app.listen({ port: PORT, host: "0.0.0.0" });
    log(`serving on port ${PORT}`);

    const httpServer = (app as any).server;
    if (httpServer) {
      websocketService.initialize(httpServer);
    }

    void initializeAiModules();
  } catch (err) {
    app.log?.error(err);
    process.exit(1);
  }
})();
