/**
 * AI Bridge Layer - Main Entry Point (2026 Refactor)
 * Unified interface for AI; optional Python (libral-core) integration via python-client.
 */

import { aiQueue, type AIRequest, type AIResponse } from './queue';
import { eventService } from '../../services/events';
import { checkPythonHealth, isPythonConfigured } from './python-client';

export interface AIBridgeConfig {
  enable_fallback: boolean;
  max_retries: number;
  default_priority: 'high' | 'normal' | 'low';
}

export { checkPythonHealth, isPythonConfigured } from './python-client';

class AIBridge {
  private config: AIBridgeConfig = {
    enable_fallback: true,
    max_retries: 3,
    default_priority: 'normal',
  };

  async initialize(config?: Partial<AIBridgeConfig>): Promise<void> {
    if (config) {
      this.config = { ...this.config, ...config };
    }
    console.log('[AI-BRIDGE] AI Bridge Layer initialized', this.config);
    await eventService.subscribe('ai.request', this.handleAIRequest.bind(this));

    if (isPythonConfigured()) {
      const pythonHealth = await checkPythonHealth();
      if (pythonHealth) {
        console.log('[AI-BRIDGE] Python (libral-core) reachable:', pythonHealth.version ?? pythonHealth.status);
      } else {
        console.log('[AI-BRIDGE] Python (libral-core) not reachable or not configured');
      }
    }
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
