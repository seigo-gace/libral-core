import { redisService } from './redis';
import { storage } from '../storage';
import { type InsertEvent } from '@shared/schema';

export class EventService {
  private eventHandlers: Map<string, Function[]> = new Map();

  constructor() {
    this.setupEventChannels();
  }

  private async setupEventChannels() {
    // Subscribe to various event channels
    await redisService.subscribe('system.events', this.handleSystemEvent.bind(this));
    await redisService.subscribe('user.events', this.handleUserEvent.bind(this));
    await redisService.subscribe('payment.events', this.handlePaymentEvent.bind(this));
    await redisService.subscribe('api.events', this.handleApiEvent.bind(this));
  }

  async publishEvent(type: string, source: string, data: any, userId?: string, level: string = 'info') {
    const event: InsertEvent = {
      type,
      source,
      userId,
      data,
      level
    };

    // Store event in database
    const storedEvent = await storage.createEvent(event);

    // Publish to Redis for real-time subscribers
    await redisService.publish('system.events', {
      ...storedEvent,
      timestamp: new Date().toISOString()
    });

    // Trigger local event handlers
    this.triggerLocalHandlers(type, storedEvent);

    return storedEvent;
  }

  private async handleSystemEvent(eventData: any) {
    console.log('System event received:', eventData);
    // Additional system event processing can be added here
  }

  private async handleUserEvent(eventData: any) {
    console.log('User event received:', eventData);
    // User-specific event processing
  }

  private async handlePaymentEvent(eventData: any) {
    console.log('Payment event received:', eventData);
    // Payment-specific event processing
  }

  private async handleApiEvent(eventData: any) {
    console.log('API event received:', eventData);
    // API-specific event processing
  }

  onEvent(eventType: string, handler: Function) {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  private triggerLocalHandlers(eventType: string, eventData: any) {
    const handlers = this.eventHandlers.get(eventType) || [];
    handlers.forEach(handler => {
      try {
        handler(eventData);
      } catch (error) {
        console.error(`Error in event handler for ${eventType}:`, error);
      }
    });
  }

  // Convenience methods for common events
  async logUserAuth(userId: string, success: boolean) {
    return this.publishEvent(
      success ? 'user_auth_success' : 'user_auth_failed',
      'auth',
      { success },
      userId,
      success ? 'info' : 'warning'
    );
  }

  async logApiRequest(path: string, method: string, responseTime: number, status: number) {
    return this.publishEvent(
      'api_request',
      'gateway',
      { path, method, responseTime, status },
      undefined,
      status >= 400 ? 'warning' : 'info'
    );
  }

  async logPaymentEvent(transactionId: string, userId: string, amount: string, status: string) {
    return this.publishEvent(
      `payment_${status}`,
      'payments',
      { transactionId, amount },
      userId,
      status === 'failed' ? 'error' : 'info'
    );
  }

  async logWebhookReceived(source: string, data: any) {
    return this.publishEvent(
      'webhook_received',
      'gateway',
      data,
      undefined,
      'info'
    );
  }

  async logModuleHealthCheck(moduleId: string, status: string) {
    return this.publishEvent(
      'module_health_check',
      'system',
      { moduleId, status },
      undefined,
      status === 'error' ? 'error' : 'info'
    );
  }
}

export const eventService = new EventService();
