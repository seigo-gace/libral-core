import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, integer, decimal, jsonb, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  telegramId: text("telegram_id").notNull().unique(),
  username: text("username"),
  firstName: text("first_name"),
  lastName: text("last_name"),
  role: text("role").notNull().default("user"), // user, creator, streamer, admin
  settings: jsonb("settings").default({}),
  createdAt: timestamp("created_at").defaultNow(),
  lastSeenAt: timestamp("last_seen_at").defaultNow(),
});

export const transactions = pgTable("transactions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id),
  type: text("type").notNull(), // sticker_purchase, stars_purchase, subscription, etc.
  amount: decimal("amount", { precision: 10, scale: 2 }).notNull(),
  currency: text("currency").notNull().default("JPY"),
  telegramPaymentId: text("telegram_payment_id"),
  status: text("status").notNull().default("pending"), // pending, completed, failed, refunded
  metadata: jsonb("metadata").default({}),
  createdAt: timestamp("created_at").defaultNow(),
  completedAt: timestamp("completed_at"),
});

export const events = pgTable("events", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  type: text("type").notNull(), // user_auth, api_request, payment_completed, etc.
  source: text("source").notNull(), // gateway, auth, payment, etc.
  userId: varchar("user_id").references(() => users.id),
  data: jsonb("data").default({}),
  level: text("level").notNull().default("info"), // info, warning, error
  createdAt: timestamp("created_at").defaultNow(),
});

export const modules = pgTable("modules", {
  id: varchar("id").primaryKey(),
  name: text("name").notNull(),
  version: text("version").notNull(),
  status: text("status").notNull().default("inactive"), // active, inactive, error, high_load
  port: integer("port"),
  endpoint: text("endpoint"),
  healthCheckUrl: text("health_check_url"),
  lastHealthCheck: timestamp("last_health_check"),
  metadata: jsonb("metadata").default({}),
});

export const systemMetrics = pgTable("system_metrics", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  metricType: text("metric_type").notNull(), // cpu, memory, api_requests, etc.
  value: decimal("value", { precision: 10, scale: 2 }).notNull(),
  unit: text("unit").notNull(), // percent, mb, count, etc.
  source: text("source").notNull(),
  timestamp: timestamp("timestamp").defaultNow(),
});

export const apiEndpoints = pgTable("api_endpoints", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  path: text("path").notNull(),
  method: text("method").notNull(),
  requestCount: integer("request_count").default(0),
  averageResponseTime: decimal("average_response_time", { precision: 10, scale: 2 }),
  lastRequestAt: timestamp("last_request_at"),
});

// Stamp Creation System Tables
export const stamps = pgTable("stamps", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id),
  text: text("text").notNull(),
  fontId: text("font_id").notNull(),
  characterId: text("character_id"),
  backgroundId: text("background_id"),
  effectId: text("effect_id"),
  animationId: text("animation_id"),
  emojis: text("emojis").array(),
  format: text("format").notNull().default("TGS"), // TGS, WEBM
  fileUrl: text("file_url"),
  fileSize: integer("file_size"),
  status: text("status").notNull().default("processing"), // processing, completed, failed
  metadata: jsonb("metadata").default({}),
  createdAt: timestamp("created_at").defaultNow(),
  completedAt: timestamp("completed_at"),
});

export const assets = pgTable("assets", {
  id: varchar("id").primaryKey(),
  name: text("name").notNull(),
  type: text("type").notNull(), // font, character, background, effect, animation
  category: text("category").notNull(), // free, premium, creator
  creatorId: varchar("creator_id").references(() => users.id),
  price: decimal("price", { precision: 10, scale: 2 }).default("0"),
  currency: text("currency").default("JPY"),
  filePath: text("file_path").notNull(),
  previewUrl: text("preview_url"),
  metadata: jsonb("metadata").default({}),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
});

export const stampCreationSessions = pgTable("stamp_creation_sessions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").notNull().references(() => users.id),
  sessionData: jsonb("session_data").default({}),
  lastUpdated: timestamp("last_updated").defaultNow(),
  expiresAt: timestamp("expires_at").notNull(),
});

// Insert schemas
export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
  createdAt: true,
  lastSeenAt: true,
});

export const insertTransactionSchema = createInsertSchema(transactions).omit({
  id: true,
  createdAt: true,
  completedAt: true,
});

export const insertEventSchema = createInsertSchema(events).omit({
  id: true,
  createdAt: true,
});

export const insertModuleSchema = createInsertSchema(modules).omit({
  lastHealthCheck: true,
});

export const insertSystemMetricsSchema = createInsertSchema(systemMetrics).omit({
  id: true,
  timestamp: true,
});

export const insertApiEndpointSchema = createInsertSchema(apiEndpoints).omit({
  id: true,
  lastRequestAt: true,
});

export const insertStampSchema = createInsertSchema(stamps).omit({
  id: true,
  createdAt: true,
  completedAt: true,
});

export const insertAssetSchema = createInsertSchema(assets).omit({
  createdAt: true,
});

export const insertStampCreationSessionSchema = createInsertSchema(stampCreationSessions).omit({
  id: true,
  lastUpdated: true,
});

// Audit events table for Aegis-PGP monitoring
export const auditEvents = pgTable("audit_events", {
  id: text("id").primaryKey().$defaultFn(() => nanoid()),
  event: text("event").notNull(), // sign|verify|encrypt|decrypt|send_attempt|send_queued
  tenantId: text("tenant_id").notNull(),
  policyId: text("policy_id"),
  transport: text("transport"),
  ok: boolean("ok"),
  requestId: text("request_id"),
  errorMessage: text("error_message"),
  metadata: text("metadata"), // JSON for additional context
  createdAt: timestamp("created_at").defaultNow()
});

export const insertAuditEventSchema = createInsertSchema(auditEvents).omit({
  id: true,
  createdAt: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Transaction = typeof transactions.$inferSelect;
export type InsertTransaction = z.infer<typeof insertTransactionSchema>;
export type Event = typeof events.$inferSelect;
export type InsertEvent = z.infer<typeof insertEventSchema>;
export type Module = typeof modules.$inferSelect;
export type InsertModule = z.infer<typeof insertModuleSchema>;
export type SystemMetrics = typeof systemMetrics.$inferSelect;
export type InsertSystemMetrics = z.infer<typeof insertSystemMetricsSchema>;
export type ApiEndpoint = typeof apiEndpoints.$inferSelect;
export type InsertApiEndpoint = z.infer<typeof insertApiEndpointSchema>;
export type Stamp = typeof stamps.$inferSelect;
export type InsertStamp = z.infer<typeof insertStampSchema>;
export type Asset = typeof assets.$inferSelect;
export type InsertAsset = z.infer<typeof insertAssetSchema>;
export type StampCreationSession = typeof stampCreationSessions.$inferSelect;
export type InsertStampCreationSession = z.infer<typeof insertStampCreationSessionSchema>;
export type AuditEvent = typeof auditEvents.$inferSelect;
export type InsertAuditEvent = z.infer<typeof insertAuditEventSchema>;
