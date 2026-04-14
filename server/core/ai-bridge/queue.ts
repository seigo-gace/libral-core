/**
 * AI Bridge Layer - Async Queue Controller
 * Handles all AI communication with automatic retry and fallback
 */

export interface AIRequest {
  id: string;
  prompt: string;
  model: 'gemini' | 'gpt5-mini' | 'oss-model';
  priority: 'high' | 'normal' | 'low';
  retry_count: number;
  max_retries: number;
  created_at: string;
}

export interface AIResponse {
  request_id: string;
  response: string;
  model_used: string;
  execution_time_ms: number;
  fallback_used: boolean;
  timestamp: string;
}

class AIQueue {
  private queue: AIRequest[] = [];
  private processing: boolean = false;
  private readonly FALLBACK_CHAIN = {
    'gemini': 'gpt5-mini',
    'gpt5-mini': 'oss-model',
    'oss-model': null
  } as const;

  async enqueue(request: Omit<AIRequest, 'id' | 'retry_count' | 'created_at'>): Promise<string> {
    const id = `ai-req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const fullRequest: AIRequest = {
      id,
      ...request,
      retry_count: 0,
      created_at: new Date().toISOString()
    };

    // Priority-based insertion
    if (fullRequest.priority === 'high') {
      this.queue.unshift(fullRequest);
    } else {
      this.queue.push(fullRequest);
    }

    // Start processing if not already running
    if (!this.processing) {
      this.processQueue();
    }

    return id;
  }

  private async processQueue(): Promise<void> {
    if (this.queue.length === 0) {
      this.processing = false;
      return;
    }

    this.processing = true;
    const request = this.queue.shift()!;

    try {
      await this.executeRequest(request);
    } catch (error) {
      console.error(`[AI-QUEUE] Request ${request.id} failed:`, error);
      
      // Retry with fallback
      if (request.retry_count < request.max_retries) {
        await this.retryWithFallback(request);
      }
    }

    // Continue processing
    setTimeout(() => this.processQueue(), 100);
  }

  private async executeRequest(request: AIRequest): Promise<AIResponse> {
    const startTime = Date.now();
    
    // Simulate AI call (replace with actual AI integration)
    const response = await this.callAI(request.model, request.prompt);
    
    const executionTime = Date.now() - startTime;

    const aiResponse: AIResponse = {
      request_id: request.id,
      response,
      model_used: request.model,
      execution_time_ms: executionTime,
      fallback_used: request.retry_count > 0,
      timestamp: new Date().toISOString()
    };

    return aiResponse;
  }

  private async retryWithFallback(request: AIRequest): Promise<void> {
    const fallbackModel = this.FALLBACK_CHAIN[request.model];
    
    if (!fallbackModel) {
      console.error(`[AI-QUEUE] No fallback available for ${request.model}`);
      return;
    }

    const retryRequest: AIRequest = {
      ...request,
      model: fallbackModel as any,
      retry_count: request.retry_count + 1
    };

    console.log(`[AI-QUEUE] Retrying with fallback: ${fallbackModel}`);
    
    // Re-enqueue with fallback model
    if (retryRequest.priority === 'high') {
      this.queue.unshift(retryRequest);
    } else {
      this.queue.push(retryRequest);
    }
  }

  private async callAI(model: string, prompt: string): Promise<string> {
    // Simulate AI call with random delay
    await new Promise(resolve => setTimeout(resolve, Math.random() * 1000 + 500));
    
    // Simulate occasional failures for testing fallback
    if (Math.random() < 0.1) {
      throw new Error(`${model} temporary failure`);
    }

    return `Response from ${model}: ${prompt}`;
  }

  getQueueStats() {
    return {
      queue_length: this.queue.length,
      processing: this.processing,
      high_priority: this.queue.filter(r => r.priority === 'high').length,
      normal_priority: this.queue.filter(r => r.priority === 'normal').length,
      low_priority: this.queue.filter(r => r.priority === 'low').length
    };
  }

  clearQueue(): void {
    this.queue = [];
    this.processing = false;
  }
}

// Singleton instance
export const aiQueue = new AIQueue();
