/**
 * Embedding Layer - Vector Storage & Similarity Search
 * Foundation for FAISS + ChromaDB integration
 * 
 * Features:
 * - Vector embedding generation
 * - Similarity search
 * - Multi-language support
 * - Integration with KB System
 */

import { eventService } from "../services/events";
import { kbSystem } from "./kb-system";

export interface EmbeddingVector {
  id: string;
  vector: number[];
  text: string;
  metadata: {
    language: string;
    category: string;
    created_at: string;
  };
}

export interface SimilaritySearchResult {
  id: string;
  text: string;
  similarity: number;
  metadata: any;
}

class EmbeddingLayer {
  readonly module_id = "embedding-layer";
  readonly module_name = "Vector Embedding Layer";
  readonly version = "1.0.0";
  readonly embedding_engine = "FAISS + ChromaDB (Simulated)";

  private embeddings: Map<string, EmbeddingVector> = new Map();
  private readonly VECTOR_DIMENSIONS = 384; // Standard embedding size

  async initialize(): Promise<void> {
    console.log(`[${this.module_id}] Initializing Embedding Layer...`);
    console.log(`[${this.module_id}] Engine: ${this.embedding_engine}`);
    console.log(`[${this.module_id}] Vector dimensions: ${this.VECTOR_DIMENSIONS}`);
  }

  async generateEmbedding(text: string, metadata?: {
    language?: string;
    category?: string;
  }): Promise<EmbeddingVector> {
    // Simulate embedding generation (in production, use sentence-transformers)
    const vector = this.simulateEmbedding(text);
    
    const embedding: EmbeddingVector = {
      id: `emb-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      vector,
      text,
      metadata: {
        language: metadata?.language || 'en',
        category: metadata?.category || 'general',
        created_at: new Date().toISOString()
      }
    };

    this.embeddings.set(embedding.id, embedding);

    // Log event
    await eventService.logEvent('embedding_generated', {
      embedding_id: embedding.id,
      language: embedding.metadata.language,
      category: embedding.metadata.category
    });

    return embedding;
  }

  private simulateEmbedding(text: string): number[] {
    // Simple text-based vector simulation
    // In production, use actual sentence-transformers models
    const vector: number[] = [];
    const textHash = this.hashString(text);

    for (let i = 0; i < this.VECTOR_DIMENSIONS; i++) {
      // Generate pseudo-random but deterministic values
      const seed = (textHash + i) * 9301 + 49297;
      vector.push((seed % 233280) / 233280.0);
    }

    // Normalize vector
    return this.normalizeVector(vector);
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }

  private normalizeVector(vector: number[]): number[] {
    const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
    return vector.map(val => val / magnitude);
  }

  async searchSimilar(queryText: string, options?: {
    limit?: number;
    threshold?: number;
    language?: string;
    category?: string;
  }): Promise<SimilaritySearchResult[]> {
    // Generate query embedding
    const queryVector = this.simulateEmbedding(queryText);
    
    // Calculate similarities
    const results: SimilaritySearchResult[] = [];

    for (const [id, embedding] of this.embeddings) {
      // Filter by language
      if (options?.language && embedding.metadata.language !== options.language) {
        continue;
      }

      // Filter by category
      if (options?.category && embedding.metadata.category !== options.category) {
        continue;
      }

      // Calculate cosine similarity
      const similarity = this.cosineSimilarity(queryVector, embedding.vector);

      // Apply threshold
      if (options?.threshold && similarity < options.threshold) {
        continue;
      }

      results.push({
        id,
        text: embedding.text,
        similarity,
        metadata: embedding.metadata
      });
    }

    // Sort by similarity (descending)
    results.sort((a, b) => b.similarity - a.similarity);

    // Limit results
    const limit = options?.limit || 10;
    return results.slice(0, limit);
  }

  private cosineSimilarity(vecA: number[], vecB: number[]): number {
    if (vecA.length !== vecB.length) {
      throw new Error('Vector dimensions must match');
    }

    let dotProduct = 0;
    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
    }

    return dotProduct; // Already normalized, so this is cosine similarity
  }

  async embedKBEntry(entryId: string): Promise<EmbeddingVector | null> {
    // Get KB entry
    const entry = await kbSystem.getKnowledgeById(entryId);
    
    if (!entry) {
      return null;
    }

    // Generate embedding
    return await this.generateEmbedding(entry.content, {
      language: entry.language,
      category: entry.category
    });
  }

  async batchEmbed(texts: string[], metadata?: {
    language?: string;
    category?: string;
  }): Promise<EmbeddingVector[]> {
    const embeddings: EmbeddingVector[] = [];

    for (const text of texts) {
      const embedding = await this.generateEmbedding(text, metadata);
      embeddings.push(embedding);
    }

    console.log(`[${this.module_id}] Batch embedded ${texts.length} texts`);

    return embeddings;
  }

  getStats() {
    return {
      total_embeddings: this.embeddings.size,
      vector_dimensions: this.VECTOR_DIMENSIONS,
      embedding_engine: this.embedding_engine,
      supported_operations: [
        'generate_embedding',
        'similarity_search',
        'batch_embed',
        'kb_integration'
      ]
    };
  }

  async shutdown(): Promise<void> {
    console.log(`[${this.module_id}] Shutting down Embedding Layer...`);
    this.embeddings.clear();
  }
}

// Singleton instance
export const embeddingLayer = new EmbeddingLayer();
