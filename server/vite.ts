/**
 * Vite dev server & static serving for Fastify (2026 Refactor)
 * Uses @fastify/middie for Connect-compatible middleware.
 */

import type { FastifyInstance } from "fastify";
import fs from "fs";
import path from "path";
import { createServer as createViteServer, createLogger } from "vite";
import viteConfig from "../vite.config";
import { nanoid } from "nanoid";

const viteLogger = createLogger();

export function log(message: string, source = "fastify") {
  const formattedTime = new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
  console.log(`${formattedTime} [${source}] ${message}`);
}

export async function setupVite(app: FastifyInstance): Promise<void> {
  const serverOptions = {
    middlewareMode: true,
    hmr: process.env.VITE_HMR_PORT
      ? { port: Number(process.env.VITE_HMR_PORT) }
      : true,
    allowedHosts: true as const,
  };

  const vite = await createViteServer({
    ...viteConfig,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg: string, options?: any) => {
        viteLogger.error(msg, options);
        process.exit(1);
      },
    },
    server: serverOptions,
    appType: "custom",
  });

  app.use(vite.middlewares);
  app.use("*", async (req: any, res: any, next: (err?: any) => void) => {
    const url = req.originalUrl ?? req.url;
    try {
      const clientTemplate = path.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html"
      );
      let template = await fs.promises.readFile(clientTemplate, "utf-8");
      template = template.replace(
        `src="/src/main.tsx"`,
        `src="/src/main.tsx?v=${nanoid()}"`
      );
      const page = await vite.transformIndexHtml(url, template);
      res.statusCode = 200;
      res.setHeader("Content-Type", "text/html");
      res.end(page);
    } catch (e) {
      vite.ssrFixStacktrace(e as Error);
      next(e);
    }
  });
}

export async function serveStatic(app: FastifyInstance): Promise<void> {
  const distPath = path.resolve(import.meta.dirname, "public");
  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`
    );
  }
  const staticPlugin = (await import("@fastify/static")).default;
  await app.register(staticPlugin, { root: distPath });
  app.setNotFoundHandler((_request, reply) => {
    const indexHtml = path.join(distPath, "index.html");
    if (fs.existsSync(indexHtml)) {
      return reply.type("text/html").send(fs.createReadStream(indexHtml));
    }
    return reply.status(404).send({ message: "Not Found" });
  });
}
