/**
 * Telegram Bot Service - Telegraf.js (2026 Refactor)
 * Webhook mode: processWebhook(update) delegates to bot.handleUpdate().
 * Handlers use Telegraf Context (ctx.reply, ctx.answerPreCheckoutQuery, etc.).
 */

import { Telegraf, type Context } from "telegraf";
import type { Update } from "telegraf/types";
import { storage } from "../storage";
import { eventService } from "./events";
import type { InsertUser, InsertTransaction } from "@shared/schema";

const BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? "mock_token";

function createBot(): Telegraf<Context<Update>> {
  const bot = new Telegraf(BOT_TOKEN);

  bot.start(async (ctx) => {
    const from = ctx.from;
    if (!from) return;
    const telegramId = from.id.toString();
    let user = await storage.getUserByTelegramId(telegramId);
    if (!user) {
      const newUser: InsertUser = {
        telegramId,
        username: from.username,
        firstName: from.first_name,
        lastName: from.last_name,
        role: "user",
        settings: {},
      };
      user = await storage.createUser(newUser);
      await eventService.publishEvent(
        "user_registered",
        "telegram",
        { telegramId: from.username ?? telegramId },
        user.id
      );
    } else {
      await storage.updateUser(user.id, { lastSeenAt: new Date() });
    }
    await eventService.logUserAuth(user.id, true);
    await ctx.reply("Welcome to Libral Core!");
  });

  bot.command("status", async (ctx) => {
    const from = ctx.from;
    if (!from) return;
    const telegramId = from.id.toString();
    let user = await storage.getUserByTelegramId(telegramId);
    if (!user) {
      const newUser: InsertUser = {
        telegramId,
        username: from.username,
        firstName: from.first_name,
        lastName: from.last_name,
        role: "user",
        settings: {},
      };
      user = await storage.createUser(newUser);
    } else {
      await storage.updateUser(user.id, { lastSeenAt: new Date() });
    }
    await eventService.logUserAuth(user.id, true);
    const modules = await storage.getAllModules();
    const activeCount = modules.filter((m) => m.status === "active").length;
    await ctx.reply(`System Status: ${activeCount}/${modules.length} modules active`);
  });

  bot.on("pre_checkout_query", async (ctx) => {
    const q = ctx.preCheckoutQuery;
    await eventService.publishEvent("payment_pre_checkout", "telegram", {
      queryId: q.id,
      amount: q.total_amount,
      currency: q.currency,
    });
    await ctx.answerPreCheckoutQuery(true);
  });

  bot.on("message", async (ctx) => {
    const msg = ctx.message;
    const from = ctx.from;
    if (!from || !("message_id" in msg)) return;

    const telegramId = from.id.toString();
    let user = await storage.getUserByTelegramId(telegramId);
    if (!user) {
      const newUser: InsertUser = {
        telegramId,
        username: from.username,
        firstName: from.first_name,
        lastName: from.last_name,
        role: "user",
        settings: {},
      };
      user = await storage.createUser(newUser);
      await eventService.publishEvent(
        "user_registered",
        "telegram",
        { telegramId: from.username ?? telegramId },
        user.id
      );
    } else {
      await storage.updateUser(user.id, { lastSeenAt: new Date() });
    }
    await eventService.logUserAuth(user.id, true);

    if ("successful_payment" in msg && msg.successful_payment) {
      const payment = msg.successful_payment;
      const transaction: InsertTransaction = {
        userId: user.id,
        type: "telegram_stars",
        amount: (payment.total_amount / 100).toString(),
        currency: payment.currency,
        telegramPaymentId: payment.telegram_payment_charge_id,
        status: "completed",
        metadata: {
          provider_charge_id: payment.provider_payment_charge_id,
          invoice_payload: payment.invoice_payload,
        },
      };
      const savedTransaction = await storage.createTransaction(transaction);
      await eventService.logPaymentEvent(
        savedTransaction.id,
        user.id,
        transaction.amount,
        "completed"
      );
    }
  });

  return bot;
}

const bot = createBot();

export class TelegramService {
  async processWebhook(webhookData: Update): Promise<{ status: string; [k: string]: unknown }> {
    await eventService.logWebhookReceived("telegram", webhookData as any);
    await bot.handleUpdate(webhookData);
    return { status: "ok", message: "Webhook processed" };
  }

  async setWebhook(url: string): Promise<{ ok: boolean; url: string }> {
    const secret = process.env.WEBHOOK_SECRET;
    await bot.telegram.setWebhook(url, secret ? { secret_token: secret } : undefined);
    return { ok: true, url };
  }

  async createInvoice(
    chatId: string,
    title: string,
    _description: string,
    payload: string,
    _currency: string,
    _prices: unknown[]
  ): Promise<{ invoice_url: string; payload: string }> {
    return {
      invoice_url: `https://t.me/invoice/${Date.now()}`,
      payload,
    };
  }
}

export const telegramService = new TelegramService();
