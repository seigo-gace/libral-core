import { storage } from '../storage';
import { eventService } from './events';
import { type InsertUser, type InsertTransaction } from '@shared/schema';

interface TelegramWebhookData {
  update_id: number;
  message?: {
    message_id: number;
    from: {
      id: number;
      is_bot: boolean;
      first_name: string;
      last_name?: string;
      username?: string;
      language_code?: string;
    };
    chat: {
      id: number;
      first_name: string;
      last_name?: string;
      username?: string;
      type: string;
    };
    date: number;
    text?: string;
  };
  pre_checkout_query?: {
    id: string;
    from: {
      id: number;
      is_bot: boolean;
      first_name: string;
      last_name?: string;
      username?: string;
    };
    currency: string;
    total_amount: number;
    invoice_payload: string;
  };
  successful_payment?: {
    currency: string;
    total_amount: number;
    invoice_payload: string;
    telegram_payment_charge_id: string;
    provider_payment_charge_id: string;
  };
}

export class TelegramService {
  private botToken: string;

  constructor() {
    this.botToken = process.env.TELEGRAM_BOT_TOKEN || 'mock_token';
  }

  async processWebhook(webhookData: TelegramWebhookData): Promise<any> {
    await eventService.logWebhookReceived('telegram', webhookData);

    if (webhookData.message) {
      return this.handleMessage(webhookData.message);
    }

    if (webhookData.pre_checkout_query) {
      return this.handlePreCheckoutQuery(webhookData.pre_checkout_query);
    }

    if (webhookData.successful_payment) {
      return this.handleSuccessfulPayment(webhookData.successful_payment, webhookData.message?.from);
    }

    return { status: 'ok', message: 'Webhook processed' };
  }

  private async handleMessage(message: any): Promise<any> {
    const telegramId = message.from.id.toString();
    
    // Find or create user
    let user = await storage.getUserByTelegramId(telegramId);
    
    if (!user) {
      const newUser: InsertUser = {
        telegramId,
        username: message.from.username,
        firstName: message.from.first_name,
        lastName: message.from.last_name,
        role: 'user',
        settings: {}
      };
      
      user = await storage.createUser(newUser);
      await eventService.publishEvent(
        'user_registered',
        'telegram',
        { telegramId: message.from.username || telegramId },
        user.id
      );
    } else {
      // Update last seen
      await storage.updateUser(user.id, { lastSeenAt: new Date() });
    }

    await eventService.logUserAuth(user.id, true);

    // Process the message content
    if (message.text) {
      await this.handleTextMessage(user, message.text);
    }

    return { status: 'ok', user_id: user.id };
  }

  private async handleTextMessage(user: any, text: string): Promise<void> {
    // Simple command handling
    if (text.startsWith('/start')) {
      await this.sendMessage(user.telegramId, 'Welcome to Libral Core!');
    } else if (text.startsWith('/status')) {
      const modules = await storage.getAllModules();
      const activeModules = modules.filter(m => m.status === 'active').length;
      await this.sendMessage(user.telegramId, `System Status: ${activeModules}/${modules.length} modules active`);
    }
  }

  private async handlePreCheckoutQuery(preCheckoutQuery: any): Promise<any> {
    // In a real implementation, we would validate the payment here
    await eventService.publishEvent(
      'payment_pre_checkout',
      'telegram',
      { 
        queryId: preCheckoutQuery.id,
        amount: preCheckoutQuery.total_amount,
        currency: preCheckoutQuery.currency 
      }
    );

    // Answer the pre-checkout query (approve the payment)
    return this.answerPreCheckoutQuery(preCheckoutQuery.id, true);
  }

  private async handleSuccessfulPayment(payment: any, from: any): Promise<any> {
    if (!from) return { status: 'error', message: 'No user data in payment' };

    const user = await storage.getUserByTelegramId(from.id.toString());
    if (!user) return { status: 'error', message: 'User not found' };

    // Create transaction record
    const transaction: InsertTransaction = {
      userId: user.id,
      type: 'telegram_stars',
      amount: (payment.total_amount / 100).toString(), // Convert from kopecks to rubles
      currency: payment.currency,
      telegramPaymentId: payment.telegram_payment_charge_id,
      status: 'completed',
      metadata: {
        provider_charge_id: payment.provider_payment_charge_id,
        invoice_payload: payment.invoice_payload
      }
    };

    const savedTransaction = await storage.createTransaction(transaction);
    
    await eventService.logPaymentEvent(
      savedTransaction.id,
      user.id,
      transaction.amount,
      'completed'
    );

    return { status: 'ok', transaction_id: savedTransaction.id };
  }

  private async sendMessage(chatId: string, text: string): Promise<any> {
    // In a real implementation, this would make an HTTP request to Telegram API
    console.log(`Sending message to ${chatId}: ${text}`);
    
    await eventService.publishEvent(
      'message_sent',
      'telegram',
      { chatId, text }
    );

    return { message_id: Date.now(), text };
  }

  private async answerPreCheckoutQuery(queryId: string, ok: boolean, errorMessage?: string): Promise<any> {
    // In a real implementation, this would make an HTTP request to Telegram API
    console.log(`Answering pre-checkout query ${queryId}: ${ok ? 'OK' : 'ERROR'}`);
    
    return { ok: true };
  }

  async createInvoice(chatId: string, title: string, description: string, payload: string, currency: string, prices: any[]): Promise<any> {
    // In a real implementation, this would create a Telegram invoice
    console.log(`Creating invoice for ${chatId}: ${title}`);
    
    return { 
      invoice_url: `https://t.me/invoice/${Date.now()}`,
      payload 
    };
  }

  async setWebhook(url: string): Promise<any> {
    // In a real implementation, this would set the webhook URL
    console.log(`Setting webhook to: ${url}`);
    return { ok: true, url };
  }
}

export const telegramService = new TelegramService();
