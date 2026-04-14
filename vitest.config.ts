import { defineConfig } from "vitest/config";
import path from "path";

/** 速度優先: run 単発、カバレッジなし、短タイムアウト */
export default defineConfig({
  test: {
    environment: "node",
    include: ["server/**/*.test.ts", "shared/**/*.test.ts"],
    exclude: ["node_modules", "dist", "client"],
    testTimeout: 5000,
    hookTimeout: 3000,
    pool: "threads",
    globals: false,
  },
  resolve: {
    alias: {
      "@shared/schema": path.resolve(__dirname, "shared/schema.ts"),
      "@shared": path.resolve(__dirname, "shared"),
    },
  },
});
