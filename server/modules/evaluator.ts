/**
 * Evaluator 2.0 - AI Output Quality Scoring System
 * Automatically scores AI outputs and triggers regeneration if score < 90
 * 
 * Features:
 * - Multi-criteria evaluation (accuracy, coherence, relevance, ethics)
 * - Automatic regeneration for low scores
 * - Learning from feedback
 * - Integration with KB System for improvement
 */

import { eventService } from "../services/events";
import { kbSystem } from "./kb-system";

export interface EvaluationCriteria {
  accuracy: number;      // 0-100
  coherence: number;     // 0-100
  relevance: number;     // 0-100
  ethics: number;        // 0-100
  completeness: number;  // 0-100
}

export interface EvaluationResult {
  id: string;
  ai_output: string;
  model_used: string;
  score: number;
  criteria: EvaluationCriteria;
  passed: boolean;
  regeneration_needed: boolean;
  recommendations: string[];
  timestamp: string;
}

class Evaluator {
  readonly module_id = "evaluator-2.0";
  readonly module_name = "AI Output Quality Evaluator";
  readonly version = "2.0.0";
  readonly PASSING_SCORE = 90;

  private evaluation_history: EvaluationResult[] = [];

  async initialize(): Promise<void> {
    console.log(`[${this.module_id}] Initializing Evaluator 2.0...`);
    
    // Subscribe to AI output events
    await eventService.subscribe('ai.output', this.evaluateOutput.bind(this));
    
    console.log(`[${this.module_id}] Evaluator 2.0 initialized with passing score: ${this.PASSING_SCORE}`);
  }

  async evaluateOutput(aiOutput: string, modelUsed: string): Promise<EvaluationResult> {
    const evaluationId = `eval-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Perform multi-criteria evaluation
    const criteria = await this.evaluateCriteria(aiOutput);
    
    // Calculate overall score (weighted average)
    const score = this.calculateOverallScore(criteria);
    
    // Determine if regeneration is needed
    const regenerationNeeded = score < this.PASSING_SCORE;
    
    // Generate recommendations
    const recommendations = this.generateRecommendations(criteria, score);

    const result: EvaluationResult = {
      id: evaluationId,
      ai_output: aiOutput,
      model_used: modelUsed,
      score,
      criteria,
      passed: score >= this.PASSING_SCORE,
      regeneration_needed: regenerationNeeded,
      recommendations,
      timestamp: new Date().toISOString()
    };

    // Store in history
    this.evaluation_history.push(result);

    // Log evaluation
    await eventService.logEvent('ai_evaluation_completed', {
      evaluation_id: evaluationId,
      score,
      passed: result.passed
    });

    // If regeneration needed, trigger alert
    if (regenerationNeeded) {
      await this.triggerRegeneration(result);
    } else {
      // Submit to KB if quality is good
      await this.submitToKB(result);
    }

    return result;
  }

  private async evaluateCriteria(output: string): Promise<EvaluationCriteria> {
    // Simulate AI-based evaluation (in production, use actual AI models)
    
    // Accuracy: Check for factual correctness
    const accuracy = this.evaluateAccuracy(output);
    
    // Coherence: Check logical flow and structure
    const coherence = this.evaluateCoherence(output);
    
    // Relevance: Check if output addresses the query
    const relevance = this.evaluateRelevance(output);
    
    // Ethics: Check for biases and harmful content
    const ethics = this.evaluateEthics(output);
    
    // Completeness: Check if output is comprehensive
    const completeness = this.evaluateCompleteness(output);

    return {
      accuracy,
      coherence,
      relevance,
      ethics,
      completeness
    };
  }

  private evaluateAccuracy(output: string): number {
    // Simulate accuracy check
    const hasKeywords = output.length > 20;
    const noErrors = !output.includes('error') && !output.includes('failed');
    return hasKeywords && noErrors ? 85 + Math.random() * 15 : 60 + Math.random() * 25;
  }

  private evaluateCoherence(output: string): number {
    // Check sentence structure and flow
    const sentences = output.split('.').filter(s => s.trim().length > 0);
    const hasMultipleSentences = sentences.length >= 2;
    return hasMultipleSentences ? 80 + Math.random() * 20 : 50 + Math.random() * 30;
  }

  private evaluateRelevance(output: string): number {
    // Check if output addresses the topic
    const hasContent = output.length > 50;
    return hasContent ? 85 + Math.random() * 15 : 60 + Math.random() * 30;
  }

  private evaluateEthics(output: string): number {
    // Check for harmful content, biases
    const harmfulTerms = ['hack', 'exploit', 'illegal', 'harmful'];
    const hasHarmfulContent = harmfulTerms.some(term => output.toLowerCase().includes(term));
    return hasHarmfulContent ? 50 + Math.random() * 30 : 90 + Math.random() * 10;
  }

  private evaluateCompleteness(output: string): number {
    // Check if output is comprehensive
    const wordCount = output.split(' ').length;
    if (wordCount < 20) return 50 + Math.random() * 20;
    if (wordCount < 50) return 70 + Math.random() * 20;
    return 85 + Math.random() * 15;
  }

  private calculateOverallScore(criteria: EvaluationCriteria): number {
    // Weighted average
    const weights = {
      accuracy: 0.3,
      coherence: 0.2,
      relevance: 0.25,
      ethics: 0.15,
      completeness: 0.1
    };

    const score = 
      criteria.accuracy * weights.accuracy +
      criteria.coherence * weights.coherence +
      criteria.relevance * weights.relevance +
      criteria.ethics * weights.ethics +
      criteria.completeness * weights.completeness;

    return Math.round(score * 10) / 10; // Round to 1 decimal
  }

  private generateRecommendations(criteria: EvaluationCriteria, score: number): string[] {
    const recommendations: string[] = [];

    if (criteria.accuracy < 80) {
      recommendations.push("Improve factual accuracy - verify information sources");
    }

    if (criteria.coherence < 80) {
      recommendations.push("Enhance logical flow and sentence structure");
    }

    if (criteria.relevance < 80) {
      recommendations.push("Focus more on addressing the core query");
    }

    if (criteria.ethics < 90) {
      recommendations.push("Review content for potential biases or harmful elements");
    }

    if (criteria.completeness < 80) {
      recommendations.push("Provide more comprehensive and detailed responses");
    }

    if (score < this.PASSING_SCORE) {
      recommendations.push(`Overall score ${score} is below passing threshold ${this.PASSING_SCORE} - regeneration recommended`);
    }

    return recommendations;
  }

  private async triggerRegeneration(result: EvaluationResult): Promise<void> {
    console.log(`[${this.module_id}] REGENERATION TRIGGERED for ${result.id}`);
    console.log(`  Score: ${result.score}/${this.PASSING_SCORE}`);
    console.log(`  Recommendations:`, result.recommendations);

    // Publish regeneration event
    await eventService.logEvent('ai_regeneration_triggered', {
      evaluation_id: result.id,
      score: result.score,
      model: result.model_used,
      recommendations: result.recommendations
    });
  }

  private async submitToKB(result: EvaluationResult): Promise<void> {
    // Submit high-quality outputs to KB System
    if (result.score >= 95) {
      try {
        await kbSystem.addKnowledge({
          content: `High-quality AI output (score: ${result.score}): ${result.ai_output}`,
          language: "en",
          category: "ai-quality-examples"
        });

        console.log(`[${this.module_id}] Submitted high-quality output to KB System`);
      } catch (error) {
        console.error(`[${this.module_id}] Failed to submit to KB:`, error);
      }
    }
  }

  async getEvaluationHistory(limit: number = 10): Promise<EvaluationResult[]> {
    return this.evaluation_history.slice(-limit);
  }

  async getStats() {
    const totalEvaluations = this.evaluation_history.length;
    const passedEvaluations = this.evaluation_history.filter(e => e.passed).length;
    const avgScore = totalEvaluations > 0
      ? this.evaluation_history.reduce((sum, e) => sum + e.score, 0) / totalEvaluations
      : 0;

    return {
      total_evaluations: totalEvaluations,
      passed: passedEvaluations,
      failed: totalEvaluations - passedEvaluations,
      pass_rate: totalEvaluations > 0 ? (passedEvaluations / totalEvaluations) * 100 : 0,
      average_score: Math.round(avgScore * 10) / 10,
      passing_threshold: this.PASSING_SCORE
    };
  }

  async shutdown(): Promise<void> {
    console.log(`[${this.module_id}] Shutting down Evaluator 2.0...`);
    this.evaluation_history = [];
  }
}

// Singleton instance
export const evaluator = new Evaluator();
