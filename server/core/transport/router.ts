// server/core/transport/router.ts
import { TransportAdapter, SendInput, SendResult } from "./adapter";
import { RoutingConfig, decidePriority } from "./policy";

export class TransportRouter {
  private circuitBreakers = new Map<string, { failures: number; lastFailure: number }>();

  constructor(
    private adapters: TransportAdapter[],
    private cfg: RoutingConfig,
    private emitAudit: (evt: any) => void
  ) {}

  private getAdapter(name: string): TransportAdapter | undefined {
    return this.adapters.find(a => a.name() === name);
  }

  private isCircuitOpen(name: string): boolean {
    const breaker = this.circuitBreakers.get(name);
    if (!breaker) return false;

    const coolDownMs = this.cfg.circuit_breaker.cool_down_sec * 1000;
    const isInCoolDown = (Date.now() - breaker.lastFailure) < coolDownMs;
    const tooManyFailures = breaker.failures >= this.cfg.circuit_breaker.failure_threshold;

    return tooManyFailures && isInCoolDown;
  }

  private recordFailure(name: string): void {
    const existing = this.circuitBreakers.get(name) || { failures: 0, lastFailure: 0 };
    this.circuitBreakers.set(name, {
      failures: existing.failures + 1,
      lastFailure: Date.now()
    });
  }

  private recordSuccess(name: string): void {
    this.circuitBreakers.delete(name);
  }

  async sendWithFailover(input: SendInput): Promise<SendResult> {
    const priorityOrder = decidePriority(this.cfg, input.metadata);
    
    for (const adapterName of priorityOrder) {
      // Skip if circuit breaker is open
      if (this.isCircuitOpen(adapterName)) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "circuit_breaker_open",
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }

      const adapter = this.getAdapter(adapterName);
      if (!adapter) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "adapter_not_found",
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }

      // Check adapter health
      try {
        const isHealthy = await adapter.health();
        if (!isHealthy) {
          this.emitAudit({
            type: "send_skipped",
            transport: adapterName,
            reason: "health_check_failed",
            tenant_id: input.metadata.tenant_id,
            usecase: input.metadata.usecase,
            idempotency_key: input.metadata.idempotency_key,
            ts: Date.now()
          });
          continue;
        }
      } catch (healthError) {
        this.emitAudit({
          type: "send_skipped",
          transport: adapterName,
          reason: "health_check_error",
          error: String(healthError),
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          ts: Date.now()
        });
        continue;
      }

      // Attempt to send
      try {
        const result = await adapter.send(input);
        
        this.emitAudit({
          type: "send_attempt",
          transport: adapterName,
          ok: result.ok,
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          error: result.error || null,
          ts: Date.now()
        });

        if (result.ok) {
          this.recordSuccess(adapterName);
          return { ...result, transport: adapterName };
        } else {
          this.recordFailure(adapterName);
        }
      } catch (sendError) {
        this.recordFailure(adapterName);
        this.emitAudit({
          type: "send_attempt",
          transport: adapterName,
          ok: false,
          tenant_id: input.metadata.tenant_id,
          usecase: input.metadata.usecase,
          idempotency_key: input.metadata.idempotency_key,
          error: String(sendError),
          ts: Date.now()
        });
      }
    }

    // All adapters failed
    this.emitAudit({
      type: "send_queued",
      reason: "all_transports_failed",
      tenant_id: input.metadata.tenant_id,
      usecase: input.metadata.usecase,
      idempotency_key: input.metadata.idempotency_key,
      attempted_transports: priorityOrder,
      ts: Date.now()
    });

    return { 
      ok: false, 
      error: "QUEUED_FOR_RETRY",
      retryAfter: this.cfg.retry.backoff_ms[0] / 1000
    };
  }
}