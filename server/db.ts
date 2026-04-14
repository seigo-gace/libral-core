/**
 * Database (Neon/PostgreSQL) - 最適案: DATABASE_URL 未設定時は null、起動時エラーにしない
 * 将来 Drizzle ストレージに切り替える際は db が null でないことを確認して使用すること。
 */

import { Pool, neonConfig } from "@neondatabase/serverless";
import { drizzle } from "drizzle-orm/neon-serverless";
import ws from "ws";
import * as schema from "@shared/schema";

neonConfig.webSocketConstructor = ws;

const connectionString = process.env.DATABASE_URL;

export const pool: Pool | null = connectionString
  ? new Pool({ connectionString })
  : null;

export const db = pool ? drizzle({ client: pool, schema }) : null;

/** DATABASE_URL が設定されているか */
export function isDatabaseConfigured(): boolean {
  return Boolean(connectionString);
}
