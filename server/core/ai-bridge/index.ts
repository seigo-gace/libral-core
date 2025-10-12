/**
 * AI Bridge Layer - Main Entry Point
 * Unified interface for all AI communications
 */

import { aiQueue, type AIRequest, type AIResponse } from './queue';
import { eventService } from '../../services/events';

export interface AIBridgeConfig {
  enable_fallback: boolean;
  max_retries: number;
  default_priority: 'high' | 'normal' | 'low';
}

class AIBridge {
  private config: AIBridgeConfig = {
    enable_fallback: true,
    max_retries: 3,
    default_priority: 'normal'
  };

  async initialize(config?: Partial<AIBridgeConfig>): Promise<void> {
    if (config) {
      this.config = { ...this.config, ...config };
    }

    console.log('[AI-BRIDGE] AI Bridge Layer initialized', this.config);
    
    // Subscribe to AI-related events
    await eventService.subscribe('ai.request', this.handleAIRequest.bind(this));
  }

  async chat(prompt: string, options?: {
    model?: 'gemini' | 'gpt5-mini' | 'oss-model';
    priority?: 'high' | 'normal' | 'low';
  }): Promise<string> {
    const requestId = await aiQueue.enqueue({
      prompt,
      model: options?.model || 'gemini',
      priority: options?.priority || this.config.default_priority,
      max_retries: this.config.max_retries
    });

    // In production, wait for response via event/callback
    // For now, return request ID
    return requestId;
  }

  async evaluate(prompt: string, enableDualVerification: boolean = false): Promise<{
    result: string;
    verification?: {
      gemini_result: string;
      gpt_result: string;
      status: 'OK' | 'DISCREPANCY';
    };
  }> {
    if (enableDualVerification) {
      const [geminiId, gptId] = await Promise.all([
        aiQueue.enqueue({
          prompt,
          model: 'gemini',
          priority: 'high',
          max_retries: this.config.max_retries
        }),
        aiQueue.enqueue({
          prompt,
          model: 'gpt5-mini',
          priority: 'high',
          max_retries: this.config.max_retries
        })
      ]);

      // Simulated results (in production, wait for actual responses)
      const geminiResult = `Gemini: ${prompt}`;
      const gptResult = `GPT: ${prompt}`;
      
      return {
        result: geminiResult,
        verification: {
          gemini_result: geminiResult,
          gpt_result: gptResult,
          status: geminiResult === gptResult ? 'OK' : 'DISCREPANCY'
        }
      };
    }

    const requestId = await aiQueue.enqueue({
      prompt,
      model: 'gemini',
      priority: 'normal',
      max_retries: this.config.max_retries
    });

    return {
      result: `Evaluation result for: ${prompt}`
    };
  }

  async getQueueStats() {
    return aiQueue.getQueueStats();
  }

  private async handleAIRequest(data: any): Promise<void> {
    console.log('[AI-BRIDGE] AI request event:', data);
  }

  async shutdown(): Promise<void> {
    console.log('[AI-BRIDGE] Shutting down AI Bridge...');
    aiQueue.clearQueue();
  }
}

// Singleton instance
export const aiBridge = new AIBridge();
export { aiQueue } from './queue';
export type { AIRequest, AIResponse } from './queue';
