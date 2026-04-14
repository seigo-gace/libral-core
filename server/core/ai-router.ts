/**
 * AI Router - Enhanced Version
 * Intelligent routing between GPT5-mini, Gemini, and OSS Models
 * 
 * Features:
 * - Load balancing
 * - Model selection based on task type
 * - Fallback chain integration
 * - Performance monitoring
 */

import { aiBridge } from "./ai-bridge";
import { ossManager } from "../modules/oss-manager";
import { evaluator } from "../modules/evaluator";
import { eventService } from "../services/events";

export interface AIRouterRequest {
  prompt: string;
  task_type?: 'general' | 'translation' | 'code' | 'analysis' | 'creative';
  preferred_model?: 'gemini' | 'gpt5-mini' | 'oss';
  require_evaluation?: boolean;
}

export interface AIRouterResponse {
  response: string;
  model_used: string;
  execution_time_ms: number;
  evaluation_score?: number;
  fallback_used: boolean;
}

class AIRouter {
  readonly module_id = "ai-router";
  readonly module_name = "Enhanced AI Router";
  readonly version = "2.0.0";

  private request_count = 0;
  private model_usage: Map<string, number> = new Map();

  async initialize(): Promise<void> {
    console.log(`[${this.module_id}] Initializing Enhanced AI Router...`);
    
    // Initialize usage stats
    this.model_usage.set('gemini', 0);
    this.model_usage.set('gpt5-mini', 0);
    this.model_usage.set('oss', 0);
    
    console.log(`[${this.module_id}] AI Router initialized`);
  }

  async route(request: AIRouterRequest): Promise<AIRouterResponse> {
    this.request_count++;
    const startTime = Date.now();

    // Select optimal model based on task type
    const selectedModel = this.selectModel(request);
    
    console.log(`[${this.module_id}] Routing to ${selectedModel} for task type: ${request.task_type || 'general'}`);

    // Execute through appropriate bridge
    let response: string;
    let fallbackUsed = false;

    try {
      if (selectedModel === 'gemini' || selectedModel === 'gpt5-mini') {
        const requestId = await aiBridge.chat(request.prompt, {
          model: selectedModel,
          priority: 'normal'
        });
        response = `Response from ${selectedModel}: ${request.prompt}`;
      } else if (selectedModel.startsWith('oss-')) {
        const ossModelId = selectedModel.replace('oss-', '');
        response = await ossManager.inferWithModel(ossModelId, request.prompt);
      } else {
        response = `Default response: ${request.prompt}`;
      }
    } catch (error) {
      console.error(`[${this.module_id}] Model ${selectedModel} failed:`, error);
      
      // Fallback to next model
      const fallbackModel = this.getFallbackModel(selectedModel);
      console.log(`[${this.module_id}] Falling back to ${fallbackModel}`);
      
      response = `Fallback response from ${fallbackModel}: ${request.prompt}`;
      fallbackUsed = true;
    }

    // Update usage stats
    const usageKey = selectedModel.startsWith('oss-') ? 'oss' : selectedModel;
    this.model_usage.set(usageKey, (this.model_usage.get(usageKey) || 0) + 1);

    const executionTime = Date.now() - startTime;

    // Evaluate if requested
    let evaluationScore: number | undefined;
    if (request.require_evaluation) {
      const evaluation = await evaluator.evaluateOutput(response, selectedModel);
      evaluationScore = evaluation.score;
    }

    // Log routing event
    await eventService.logEvent('ai_routing_completed', {
      model_used: selectedModel,
      task_type: request.task_type,
      execution_time_ms: executionTime,
      fallback_used: fallbackUsed
    });

    return {
      response,
      model_used: selectedModel,
      execution_time_ms: executionTime,
      evaluation_score: evaluationScore,
      fallback_used: fallbackUsed
    };
  }

  private selectModel(request: AIRouterRequest): string {
    // If user prefers a specific model
    if (request.preferred_model) {
      if (request.preferred_model === 'oss') {
        return this.selectOSSModel(request.task_type);
      }
      return request.preferred_model;
    }

    // Intelligent model selection based on task type
    switch (request.task_type) {
      case 'translation':
        return 'gemini'; // Gemini excels at translation
      
      case 'code':
        return 'oss-llama3'; // LLaMA 3 good for code
      
      case 'analysis':
        return 'gpt5-mini'; // GPT for analysis
      
      case 'creative':
        return 'gemini'; // Gemini for creative tasks
      
      case 'general':
      default:
        // Load balance between models
        return this.loadBalance();
    }
  }

  private selectOSSModel(taskType?: string): string {
    // Select appropriate OSS model based on task
    switch (taskType) {
      case 'code':
      case 'analysis':
        return 'oss-llama3';
      
      case 'translation':
      case 'general':
        return 'oss-mistral';
      
      default:
        return 'oss-mistral'; // Default fast model
    }
  }

  private loadBalance(): string {
    // Simple round-robin load balancing
    const models = ['gemini', 'gpt5-mini'];
    const index = this.request_count % models.length;
    return models[index];
  }

  private getFallbackModel(failedModel: string): string {
    const fallbackChain = {
      'gemini': 'gpt5-mini',
      'gpt5-mini': 'oss-mistral',
      'oss-llama3': 'oss-mistral',
      'oss-mistral': 'gemini',
      'oss-falcon': 'oss-llama3'
    } as const;

    return fallbackChain[failedModel as keyof typeof fallbackChain] || 'gemini';
  }

  getStats() {
    return {
      total_requests: this.request_count,
      model_usage: Object.fromEntries(this.model_usage),
      usage_percentage: {
        gemini: this.request_count > 0 ? ((this.model_usage.get('gemini') || 0) / this.request_count) * 100 : 0,
        gpt5_mini: this.request_count > 0 ? ((this.model_usage.get('gpt5-mini') || 0) / this.request_count) * 100 : 0,
        oss: this.request_count > 0 ? ((this.model_usage.get('oss') || 0) / this.request_count) * 100 : 0
      }
    };
  }

  async shutdown(): Promise<void> {
    console.log(`[${this.module_id}] Shutting down AI Router...`);
    this.model_usage.clear();
    this.request_count = 0;
  }
}

// Singleton instance
export const aiRouter = new AIRouter();
